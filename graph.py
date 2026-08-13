from dataclasses import asdict

from langgraph.graph import END, START, StateGraph

from core.config import GROQ_MODEL
from core.state import SpineState
from sources.web import fetch_news
from writers.x_writer import write
from agents.verifier import verify_variant
from writers.strategy import choose_archetype


# ----------------------------------------------------------------------
# node 1: research
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
# node: strategy — pick the archetype from the finding (uses YOUR logic)
# ----------------------------------------------------------------------
def strategy_node(state: SpineState) -> SpineState:
    if state.get("status") != "ok":
        return state

    finding = state["finding"]
    try:
        decision = choose_archetype(
            source_type=finding.source_type,
            is_first_party=(finding.source_type == "own_work"),
            has_real_failure=False,
            has_real_measurement=False,
            has_real_completion=False,
        )
    except Exception as exc:
        return {**state, "status": "no_archetype",
                "error": f"strategy refused/raised: {exc}"}

    archetype = getattr(decision, "archetype", None)
    if not archetype:
        return {**state, "status": "no_archetype",
                "error": f"no archetype for source_type={finding.source_type}"}

    return {**state, "archetype": archetype, "status": "ok", "error": ""}

# ----------------------------------------------------------------------
# node 2: write
# ----------------------------------------------------------------------
def write_node(state: SpineState) -> SpineState:
    if state.get("status") != "ok":        # short-circuit on upstream failure
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
# node 3: verify
#   BRIDGE: write() gives DraftVariant OBJECTS, verify_variant() wants a
#   dict. We convert each variant with asdict() and pass the finding's
#   source text + url + model name that verify_variant requires.
# ----------------------------------------------------------------------
def verify_node(state: SpineState) -> SpineState:
    if state.get("status") != "ok":
        return state

    finding = state["finding"]
    draft = state["draft"]
    verifications = {}

    try:
        for variant in draft.variants:
            variant_dict = asdict(variant)          # DraftVariant -> dict
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

    # if EVERY variant was blocked, mark the whole run
    all_blocked = all(
        v.status == "BLOCKED" for v in verifications.values()
    )
    status = "all_blocked" if all_blocked else "ok"

    return {**state, "verifications": verifications,
            "status": status, "error": ""}


# ----------------------------------------------------------------------
# build + compile the graph  (linear this week; supervisor comes week 2)
# ----------------------------------------------------------------------
def build_graph():
    g = StateGraph(SpineState)

    g.add_node("research", research_node)
    g.add_node("strategy", strategy_node)
    g.add_node("write", write_node)
    g.add_node("verify", verify_node)

    g.add_edge(START, "research")
    g.add_edge("research", "strategy")
    g.add_edge("strategy", "write")
    g.add_edge("write", "verify")
    g.add_edge("verify", END)

    return g.compile()