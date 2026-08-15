"""
Turns an EXTERNAL finding (news / paper) into teardown-ready material - or
decides it isn't worth posting.

Design (Option B): external sources are RARE, high-quality teardowns, not a
news feed. Most news is noise. So synthesis is deliberately strict: it only
green-lights a finding that is genuinely significant AND has an explainable
mechanism worth a TEARDOWN_THREAD. Everything else returns None -> the run
ends cleanly with 'nothing_interesting'.

First-party (own_work) findings never reach synthesis - they route directly
through strategy. This module is external-only.
"""

import json
import re
from dataclasses import dataclass

from core.llm import invoke_llm


@dataclass
class Insight:
    """What synthesis extracted from an external finding."""
    archetype: str          # currently always TEARDOWN_THREAD for external
    key_point: str          # the core mechanism/idea to explain
    angle: str              # the specific framing for the teardown


def _text(response) -> str:
    """invoke_llm returns a LangChain message object; text is on .content."""
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


_SYNTH_SYSTEM = """You are a strict editor deciding whether an AI/tech news item is
worth writing a technical teardown thread about.

A TEARDOWN is worth writing ONLY when ALL of these hold:
  - There is a concrete, real artifact: a released model, a published paper, a
    shipped system, a benchmark result. Not a rumor, not "plans to", not a
    funding round, not an opinion piece.
  - There is an explainable MECHANISM - something about HOW it works that an
    engineer would learn from. A teardown explains machinery; if there's no
    machinery to explain, skip it.
  - It is genuinely significant, not the fourth incremental release this week.

Be strict. Most items should be REJECTED. A mediocre teardown of a minor release
dilutes the feed. When in doubt, reject.

Return ONLY this JSON:
{"worth_it": true|false, "reason": "one line",
 "key_point": "the core mechanism to explain, if worth_it",
 "angle": "the specific framing for the teardown, if worth_it"}

If worth_it is false, key_point and angle may be empty."""


def synthesize(finding) -> Insight | None:
    """
    Judge an external finding. Return an Insight if it's teardown-worthy,
    or None to skip.
    """
    if finding.source_type == "own_work":
        # defensive: first-party should never reach here
        return None

    user = (
        f"TITLE: {finding.title}\n\n"
        f"CONTENT:\n{finding.content[:4000]}\n\n"
        f"Decide whether this is worth a technical teardown thread."
    )

    messages = [
        {"role": "system", "content": _SYNTH_SYSTEM},
        {"role": "user", "content": user},
    ]

    raw = _text(invoke_llm(messages))
    decision = _parse_json(raw)

    if not decision.get("worth_it"):
        return None

    return Insight(
        archetype="TEARDOWN_THREAD",
        key_point=str(decision.get("key_point", "")).strip(),
        angle=str(decision.get("angle", "")).strip(),
    )