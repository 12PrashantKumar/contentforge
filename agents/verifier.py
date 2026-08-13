import json


from langchain_core.messages import (
    HumanMessage,
    SystemMessage,
)

from core.llm import invoke_llm
from services.validators import validate_variant


_EXTRACT_SYSTEM = """
You are a factual claim extraction system.

Your job is to extract factual claims from a
piece of text.

A factual claim is a statement that can be
verified against an external source.

EXTRACT claims such as:

- a company released a model
- a model scored a specific benchmark
- a product is 3x faster
- a feature launches on a specific date
- a study reported a specific result
- a company raised a specific amount

DO NOT extract:

- opinions
- predictions
- recommendations
- rhetorical questions
- subjective judgments
- value judgments
- personal experiences
- statements about what the writer personally did

IMPORTANT:

Extract the smallest meaningful factual claim.

For example:

"Anthropic's new model scores 82% on SWE-bench
and runs 3x faster than the previous version."

should become two claims:

1. "Anthropic's new model scores 82% on SWE-bench."
2. "Anthropic's new model runs 3x faster than the previous version."

Return ONLY valid JSON.

Format:

{
    "claims": [
        "claim one",
        "claim two"
    ]
}

If there are no factual claims:

{
    "claims": []
}
"""


def _parse_json(content: str) -> dict:
    """
    Parse JSON returned by the LLM.

    Handles accidental markdown code fences.
    """

    content = content.strip()

    if content.startswith("```json"):
        content = content[len("```json"):]

    elif content.startswith("```"):
        content = content[len("```"):]

    if content.endswith("```"):
        content = content[:-3]

    return json.loads(
        content.strip()
    )


def extract_claims(
    draft_text: str,
) -> list[str]:
    """
    Extract factual claims from draft text.

    Opinions, predictions, and personal experiences
    should not be returned.
    """

    messages = [
        SystemMessage(
            content=_EXTRACT_SYSTEM
        ),
        HumanMessage(
            content=draft_text
        ),
    ]

    response = invoke_llm(
        messages
    )

    result = _parse_json(
        response.content
    )

    claims = result.get(
        "claims",
        []
    )

    if not isinstance(
        claims,
        list,
    ):
        raise ValueError(
            "Claim extractor returned "
            "an invalid claims list."
        )

    cleaned_claims = []

    for claim in claims:

        if not isinstance(
            claim,
            str,
        ):
            continue

        claim = claim.strip()

        if claim:
            cleaned_claims.append(
                claim
            )

    return cleaned_claims

def find_evidence(
    claim: str,
    source_text: str,
) -> str:
    """
    Find the exact source text that supports a claim.

    Returns:
        Evidence text if found.
        Empty string if the source does not contain
        evidence for the claim.
    """

    system_prompt = """
You are an evidence retrieval system.

Your task is to find evidence for ONE factual claim
inside the supplied source text.

Rules:

1. Use ONLY the supplied source text.
2. Never use outside knowledge.
3. Never invent evidence.
4. Return the exact sentence or sentences from
   the source that directly support the claim.
5. Do not rewrite or paraphrase the evidence.
6. If the source does not contain evidence that
   supports or directly addresses the claim,
   return an empty string.

IMPORTANT:

The evidence must actually support the claim.

Do not treat related information as evidence.

Example:

Claim:
"Company raised $40M in Series B."

Source:
"The company released its new model on Tuesday."

Correct response:
""

Do NOT respond with a plausible funding statement.

Return ONLY valid JSON:

{
    "evidence": "exact sentence from source"
}

If there is no supporting evidence:

{
    "evidence": ""
}
"""

    user_prompt = f"""
CLAIM:
{claim}

SOURCE TEXT:
{source_text}
"""

    response = invoke_llm(
        [
            SystemMessage(
                content=system_prompt
            ),
            HumanMessage(
                content=user_prompt
            ),
        ]
    )

    result = _parse_json(
        response.content
    )

    evidence = result.get(
        "evidence",
        ""
    )

    if not isinstance(
        evidence,
        str,
    ):
        return ""

    return evidence.strip()

def judge(
    claim: str,
    evidence: str,
) -> str:
    """
    Determine whether the evidence directly supports
    the claim.

    Returns:
        SUPPORTED
        UNSUPPORTED
    """

    if not evidence.strip():
        return "UNSUPPORTED"

    system_prompt = """
You are a strict factual verification judge.

Your ONLY task is to determine whether the supplied
evidence directly supports the supplied claim.

Return exactly one verdict:

SUPPORTED
UNSUPPORTED


CORE RULE:

The claim must be supported by the evidence.

However, do not reject a claim merely because it
uses a slightly broader, commonly used name for the
same specific subject.

Evaluate semantic meaning, not only exact wording.


SUPPORTED:

A claim is SUPPORTED when the evidence clearly
establishes the same factual meaning.

Examples:

Evidence:
"In internal testing it scored 82% on SWE-bench Verified."

Claim:
"The model scores 82% on SWE-bench."

Verdict:
SUPPORTED

Reason:
"SWE-bench Verified" is a specific evaluation within
the SWE-bench benchmark family. The evidence directly
establishes the model's SWE-bench performance.


UNSUPPORTED:

A claim is UNSUPPORTED when it adds information,
scope, certainty, magnitude, comparison, or implication
that the evidence does not establish.


IMPORTANT OVERSTATEMENT RULES:

1. A specific benchmark does NOT support a claim about
   all benchmarks.

Evidence:
"Scored 82% on SWE-bench Verified."

Claim:
"Scores 82% on all benchmarks."

Verdict:
UNSUPPORTED


2. "Up to 3x faster" does NOT mean "exactly 3x faster."

Evidence:
"Inference is up to 3x faster."

Claim:
"Inference is exactly 3x faster."

Verdict:
UNSUPPORTED


3. "Plans to release" does NOT mean "released."

Evidence:
"The company plans to release the model."

Claim:
"The company released the model."

Verdict:
UNSUPPORTED


4. "Research preview" does NOT mean "production."

Evidence:
"The model is currently available as a research preview."

Claim:
"The model is available in production."

Verdict:
UNSUPPORTED


5. Evidence about one metric does not support a claim
   about a different metric.

Evidence:
"82% on SWE-bench."

Claim:
"82% on MMLU."

Verdict:
UNSUPPORTED


6. Evidence about one company does not support a claim
   about another company.

7. Evidence about one date does not support a different
   date.

8. Evidence about one product/version does not
   automatically support a claim about another product
   or version.

9. Do not use outside knowledge.

10. Do not fill in missing information.

11. If the evidence is ambiguous or insufficient,
    return UNSUPPORTED.

12. Do not require exact word-for-word matching.
    Judge whether the evidence establishes the factual
    meaning of the claim.

Return ONLY valid JSON:

{
    "verdict": "SUPPORTED"
}

or:

{
    "verdict": "UNSUPPORTED"
}
"""

    user_prompt = f"""
CLAIM:
{claim}

EVIDENCE:
{evidence}
"""

    response = invoke_llm(
        [
            SystemMessage(
                content=system_prompt
            ),
            HumanMessage(
                content=user_prompt
            ),
        ]
    )

    result = _parse_json(
        response.content
    )

    verdict = result.get(
        "verdict",
        "",
    ).strip().upper()

    if verdict not in {
        "SUPPORTED",
        "UNSUPPORTED",
    }:
        raise ValueError(
            f"Invalid judge verdict: {verdict}"
        )

    return verdict

from core.models import (
    Claim,
    VerificationResult,
)
def verify_variant(
    variant: dict,
    source_text: str,
    source_url: str,
    model_name: str,
) -> VerificationResult:

    blocked_reasons: list[str] = []

    # --------------------------------------------------
    # 1. Deterministic validation
    # --------------------------------------------------

    try:
        validate_variant(
            variant,
            source_url,
        )

    except ValueError as exc:

        blocked_reasons.append(
            str(exc)
        )

        return VerificationResult(
            status="BLOCKED",
            claims=[],
            blocked_reasons=blocked_reasons,
        )

    # --------------------------------------------------
    # 2. Source content check
    # --------------------------------------------------

    if not source_text.strip():

        return VerificationResult(
            status="BLOCKED",
            claims=[],
            blocked_reasons=[
                "Source contains no usable content."
            ],
        )

    # --------------------------------------------------
    # 3. Extract factual claims
    # --------------------------------------------------

    post = variant["post"]

    claims_text = extract_claims(
        post
    )

    claims: list[Claim] = []

    # --------------------------------------------------
    # 4. Verify every factual claim
    # --------------------------------------------------

    for claim_text in claims_text:

        evidence = find_evidence(
            claim_text,
            source_text,
        )

        # ----------------------------------------------
        # No evidence → fail closed
        # ----------------------------------------------

        if not evidence:

            claims.append(
                Claim(
                    claim_text=claim_text,
                    source_url=source_url,
                    evidence_text="",
                    evidence_location="",
                    verdict="NO_EVIDENCE",
                    judged_by=model_name,
                )
            )

            continue

        # ----------------------------------------------
        # Judge evidence
        # ----------------------------------------------

        verdict = judge(
            claim_text,
            evidence,
        )

        claims.append(
            Claim(
                claim_text=claim_text,
                source_url=source_url,
                evidence_text=evidence,
                evidence_location="source content",
                verdict=verdict,
                judged_by=model_name,
            )
        )

    # --------------------------------------------------
    # 5. Fail closed
    # --------------------------------------------------

    unsupported_claims = [
        claim
        for claim in claims
        if not claim.is_supported
    ]

    if unsupported_claims:

        blocked_reasons = [
            (
                f"Unsupported claim: "
                f"{claim.claim_text}"
            )
            for claim in unsupported_claims
        ]

        return VerificationResult(
            status="BLOCKED",
            claims=claims,
            blocked_reasons=blocked_reasons,
        )

    # --------------------------------------------------
    # 6. Everything passed
    # --------------------------------------------------

    return VerificationResult(
        status="VERIFIED",
        claims=claims,
        blocked_reasons=[],
    )