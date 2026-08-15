"""
Turns an EXTERNAL finding (news / paper) into a post, routed to an archetype
the source content can actually FILL. Or skips it.

The hard lesson: an abstract has results, not mechanism. Routing everything to
TEARDOWN_THREAD (which needs mechanism) makes good content fail as
'insufficient_input'. So synthesis picks the archetype that fits what the
source actually contains:

  - a specific factual finding / result / number   -> TIL_SNIPPET   (default)
  - a strong, debatable technical position          -> CONTRARIAN_TAKE
  - genuinely detailed mechanism (rare in abstracts)-> TEARDOWN_THREAD
  - nothing worth posting                            -> None (skip)

First-party (own_work) never reaches synthesis - it routes via strategy.
"""

import json
import re
from dataclasses import dataclass

from core.llm import invoke_llm


EXTERNAL_ARCHETYPES = ["TIL_SNIPPET", "CONTRARIAN_TAKE", "TEARDOWN_THREAD"]


@dataclass
class Insight:
    archetype: str
    key_point: str
    angle: str


def _text(response) -> str:
    return response.content if hasattr(response, "content") else str(response)


def _parse_json(raw: str):
    text = raw.strip()
    fenced = re.search(r"```(?:json)?\s*(.*?)```", text, re.DOTALL)
    if fenced:
        text = fenced.group(1).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        raise


_SYNTH_SYSTEM = """You are a strict editor deciding whether, and how, to post about an
AI/tech source (a paper abstract or a news item).

First decide if it is worth posting at all. Worth posting means: a concrete, real
artifact (released model, published paper, benchmark result, shipped system) with
at least one specific, interesting, checkable fact. Rumors, funding rounds, vague
opinion pieces, and incremental noise are NOT worth posting. Be strict - most
items should be skipped.

If it IS worth posting, choose the archetype the source can actually support:

  TIL_SNIPPET  - DEFAULT. Use when the source has a specific factual finding,
                 result, or number. Almost any real paper/news qualifies. This is
                 your safe, reliable choice.

  CONTRARIAN_TAKE - Use only when the source makes a strong, debatable technical
                 claim you could take a real position on. Needs a genuine angle,
                 not manufactured disagreement.

  TEARDOWN_THREAD - Use ONLY when the source contains actual MECHANISM detail:
                 specific components, data flows, how it works step by step. Most
                 abstracts do NOT have this - they have results, not method. If you
                 are unsure whether there is real mechanism, do NOT choose teardown.

When in doubt between archetypes, choose TIL_SNIPPET - it reliably works from
limited source text.

Return ONLY this JSON:
{"worth_it": true|false,
 "archetype": "TIL_SNIPPET" | "CONTRARIAN_TAKE" | "TEARDOWN_THREAD",
 "key_point": "the specific fact or position to build the post around",
 "angle": "one line on the framing",
 "reason": "one line on why this archetype"}

If worth_it is false, the other fields may be empty."""


def synthesize(finding) -> Insight | None:
    if finding.source_type == "own_work":
        return None

    user = (
        f"TITLE: {finding.title}\n\n"
        f"CONTENT:\n{finding.content[:4000]}\n\n"
        f"Decide whether and how to post about this."
    )

    messages = [
        {"role": "system", "content": _SYNTH_SYSTEM},
        {"role": "user", "content": user},
    ]

    raw = _text(invoke_llm(messages))
    decision = _parse_json(raw)

    if not decision.get("worth_it"):
        return None

    archetype = str(decision.get("archetype", "")).strip().upper()
    if archetype not in EXTERNAL_ARCHETYPES:
        archetype = "TIL_SNIPPET"

    return Insight(
        archetype=archetype,
        key_point=str(decision.get("key_point", "")).strip(),
        angle=str(decision.get("angle", "")).strip(),
    )