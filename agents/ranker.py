"""

Picks the most interesting finding from a batch.

Lesson from v1: scoring each finding in ISOLATION made everything score 9 -
an arXiv batch is all legitimately-good papers, so "is this a 1-10?" gets a 9
every time and the ranker doesn't actually choose. The fix is COMPARATIVE
ranking: show the model the whole batch at once and make it pick the single
most interesting item, forcing a real relative judgment.

Returns the winner, or None if the whole batch is below the quality floor.
"""

import json
import re

from core.llm import invoke_llm


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


_RANK_SYSTEM = """You are choosing the single most interesting item from a batch, for a
developer audience that follows people for real technical substance.

You will see a numbered list of items (title + summary). Compare them AGAINST EACH
OTHER and pick the ONE a builder would most want to read about.

Prefer, in order:
  - a concrete, surprising, or novel method/result with specifics an engineer
    would bookmark
  - broad practical relevance (agents, LLMs, retrieval, systems) over narrow
    theory that only a few specialists care about
  - specific numbers, benchmarks, or a real technique over vague claims

Even in a strong batch, they are NOT equal - force a real ranking. Break ties by
practical usefulness to a working AI engineer.

Also give the winner an honest quality score 1-10 (most real papers are 6-8; a 9-10
is genuinely remarkable; reserve it).

Return ONLY:
{"winner_index": <the number of the item you picked>,
 "score": <1-10 honest quality of the winner>,
 "reason": "one line on why this one over the others"}"""


def pick_best(findings: list, min_score: int = 5):
    """
    Comparative ranking over the whole batch. Returns (finding, score), or
    (None, score) if even the winner is below min_score.
    """
    if not findings:
        return None, 0
    if len(findings) == 1:
        return findings[0], 7   # nothing to compare against; let it through

    # build the numbered batch
    lines = []
    for i, f in enumerate(findings):
        summary = (f.content or "")[:400].replace("\n", " ")
        lines.append(f"[{i}] {f.title}\n    {summary}")
    batch = "\n\n".join(lines)

    messages = [
        {"role": "system", "content": _RANK_SYSTEM},
        {"role": "user", "content": f"Batch:\n\n{batch}\n\nPick the most interesting one."},
    ]

    try:
        decision = _parse_json(_text(invoke_llm(messages)))
        idx = int(decision.get("winner_index", 0))
        score = int(decision.get("score", 0))
        reason = str(decision.get("reason", "")).strip()
    except Exception as exc:
        print(f"  [ranker] parse failed ({exc}); falling back to first item")
        return findings[0], 6

    if idx < 0 or idx >= len(findings):
        idx = 0
    score = max(0, min(10, score))

    print(f"  [ranker] winner: [{idx}] score {score} - {reason}")

    if score < min_score:
        return None, score

    return findings[idx], score