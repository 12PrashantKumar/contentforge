"""
agents/synthesis.py
Turns an EXTERNAL finding (news / paper) into a post, routed to the archetype
that FITS what the source actually is. Or skips it.

Two lessons, both learned the hard way:

  1. Don't force everything to TEARDOWN - abstracts have results, not mechanism.
  2. Don't force everything to TIL either - many strong papers are CRITIQUE or
     ARGUMENT papers whose value is a position, not a crisp number. TIL wants a
     hard fact; a critique paper has none, so the writer refuses. Those belong
     in CONTRARIAN_TAKE.

Routing:
  hard specific result / number / benchmark        -> TIL_SNIPPET
  a debatable position, critique, or "everyone
    thinks X but actually Y" argument               -> CONTRARIAN_TAKE
  genuinely detailed step-by-step mechanism (rare)  -> TEARDOWN_THREAD
  nothing worth posting                             -> None (skip)
still holds: be strict, most items skip. But when something IS worth
posting, route it to a format it can actually fill.

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

STEP 1 - worth posting at all?
Worth posting means a concrete, real artifact OR a genuinely interesting finding,
argument, or result. Rumors, funding rounds, and vague noise are NOT. Be strict -
most items should be skipped. If not worth it, say so.

STEP 2 - if worth posting, pick the archetype that FITS what this source actually is:

  TIL_SNIPPET - the source has a HARD, SPECIFIC FACT: a number, a benchmark score,
      a concrete measured result, a named technique with a crisp takeaway.
      Example: "achieves 78.3 on PosterBench", "runs in 40 min for under $3".
      Choose this when there is a specific fact a reader could quote.

  CONTRARIAN_TAKE - reserved for FIRST-PERSON opinions the author actually holds.
      Do NOT use this for papers or news: a contrarian take requires a position
      from the author's own experience and a condition under which they'd be
      wrong. You cannot honestly manufacture that from a source someone else
      wrote. If a paper's value is an argument rather than a number, express it
      as a TIL ("TIL: this paper argues/finds X") - that's honest, because the
      author really did learn it. Do not fake a personal opinion.

  TEARDOWN_THREAD - ONLY when the source has real step-by-step MECHANISM detail
      (specific components, data flows, how it works). Abstracts rarely do. If
      unsure, do NOT choose teardown.

Decision rule for external sources: almost everything worth posting becomes a
TIL_SNIPPET - a hard fact OR an interesting finding/argument, both framed as
"here's what I learned from this source". Use TEARDOWN only for real mechanism.
Do NOT use CONTRARIAN for external sources. If the source has no crisp,
quotable takeaway at all, skip it.

Return ONLY this JSON:
{"worth_it": true|false,
 "archetype": "TIL_SNIPPET" | "CONTRARIAN_TAKE" | "TEARDOWN_THREAD",
 "key_point": "the specific fact or the position to build the post around",
 "angle": "one line on the framing",
 "reason": "one line on why this archetype fits"}

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