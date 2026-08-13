from dataclasses import asdict

from langgraph.graph import END, START, StateGraph

from core.config import GROQ_MODEL
from core.state import SpineState

from sources.web import fetch_news
from sources.interview import run_interview
from writers.strategy import choose_archetype
from writers.x_writer import write
from agents.verifier import verify_variant


# ----------------------------------------------------------------------
# node: interview  (first-party entry point)
#   Shows you your week's work, asks what happened, and sets the strategy
#   flags from your answer. Returns 'nothing_to_post' if there's no work
#   or you opt out - a valid outcome, not an error.
# ----------------------------------------------------------------------
def interview_node(state: SpineState) -> SpineState:
    result = run_interview(days=state.get("days", 7))

    if result is None:
        return {**state, "status": "nothing_to_post", "error": ""}

    return {
        **state,
        "finding": result.finding,
        "is_first_party": result.is_first_party,
        "has_real_completion": result.has_real_completion,
        "has_real_failure": result.has_real_failure,
        "has_real_measurement": result.has_real_measurement,
        "status": "ok",
        "error": "",
    }


# ----------------------------------------------------------------------
# node: research  (news path - kept for later, NOT wired this week)
# ----------------------------------------------------------------------
def research_node(state: SpineState) -> SpineState:
    days = state.get("days", 1)
    try:
        findings = fetch_news(days=days)
    except Exception as exc:
        return {**state, "status": "error", "error": f"research failed: {exc}"}

    if not findings:
        return {**state, "status": "no_findings", "error": "",
                "findings": [], "finding": None}

    return {**state, "findings": findings, "finding": findings[0],
            "status": "ok", "error": ""}


# ----------------------------------------------------------------------
# node: strategy  (reads the flags the interview set)
# ----------------------------------------------------------------------
def strategy_node(state: SpineState) -> SpineState:
    if state.get("status") != "ok":
        return state

    finding = state["finding"]
    try:
        decision = choose_archetype(
            source_type=finding.source_type,
            is_first_party=state.get("is_first_party", False),
            has_real_failure=state.get("has_real_failure", False),
            has_real_measurement=state.get("has_real_measurement", False),
            has_real_completion=state.get("has_real_completion", False),
        )
    except Exception as exc:
        return {**state, "status": "no_archetype",
                "error": f"strategy refused/raised: {exc}"}

    archetype = getattr(decision, "archetype", None)
    if not archetype:
        return {**state, "status": "no_archetype",
                "error": f"no archetype for source_type={finding.source_type}"}

    print(f"\n[strategy] archetype = {archetype}  ({decision.reason})")
    return {**state, "archetype": archetype, "status": "ok", "error": ""}


# ----------------------------------------------------------------------
# node: write
# ----------------------------------------------------------------------
def write_node(state: SpineState) -> SpineState:
    if state.get("status") != "ok":
        return state

    finding = state["finding"]
    archetype = state["archetype"]

    try:
        draft = write(finding, archetype)
    except Exception as exc:
        return {**state, "status": "write_failed",
                "error": f"write raised: {exc}"}

    if draft.status == "insufficient_input":
        return {**state, "draft": draft, "status": "insufficient_input",
                "error": f"source insufficient: {draft.notes}"}

    if draft.status != "ok" or not draft.variants:
        return {**state, "draft": draft, "status": "write_failed",
                "error": f"writer status: {draft.status}"}

    return {**state, "draft": draft, "status": "ok", "error": ""}


# ----------------------------------------------------------------------
# node: verify
#   BRIDGE: write() gives DraftVariant OBJECTS, verify_variant() wants a
#   dict + the source text/url/model. asdict() converts each variant.
# ----------------------------------------------------------------------
def verify_node(state: SpineState) -> SpineState:
    if state.get("status") != "ok":
        return state

    finding = state["finding"]
    draft = state["draft"]
    verifications = {}

    try:
        for variant in draft.variants:
            variant_dict = asdict(variant)
            result = verify_variant(
                variant=variant_dict,
                source_text=finding.content,
                source_url=finding.source_url,
                model_name=GROQ_MODEL,
            )
            verifications[variant.id] = result
    except Exception as exc:
        return {**state, "status": "error",
                "error": f"verification raised: {exc}"}

    all_blocked = all(v.status == "BLOCKED" for v in verifications.values())
    status = "all_blocked" if all_blocked else "ok"

    return {**state, "verifications": verifications,
            "status": status, "error": ""}


# ----------------------------------------------------------------------
# build + compile  (first-party path this week: interview -> ... -> verify)
# ----------------------------------------------------------------------
def build_graph():
    g = StateGraph(SpineState)

    g.add_node("interview", interview_node)
    g.add_node("strategy", strategy_node)
    g.add_node("write", write_node)
    g.add_node("verify", verify_node)

    g.add_edge(START, "interview")
    g.add_edge("interview", "strategy")
    g.add_edge("strategy", "write")
    g.add_edge("write", "verify")
    g.add_edge("verify", END)

    return g.compile()