from core.models import (
    Claim,
    VerificationResult,
)


# ==========================================
# TEST 1
# ==========================================

claim = Claim(
    claim_text="Model scores 82% on SWE-bench.",
    source_url="https://example.com/source",
)


assert claim.verdict == "NO_EVIDENCE"
assert claim.is_supported is False


print(
    "Claim default state: PASSED"
)


# ==========================================
# TEST 2
# ==========================================

claim.verdict = "SUPPORTED"

assert claim.is_supported is True

print(
    "Supported claim: PASSED"
)


# ==========================================
# TEST 3
# ==========================================

unsupported_claim = Claim(
    claim_text="Company raised $40M.",
    source_url="https://example.com/source",
    evidence_text="No funding information appears.",
    verdict="UNSUPPORTED",
    judged_by="test-model",
)

assert (
    unsupported_claim.is_supported
    is False
)

print(
    "Unsupported claim: PASSED"
)


# ==========================================
# TEST 4
# ==========================================

no_evidence_claim = Claim(
    claim_text="Company raised $40M.",
    source_url="https://example.com/source",
)

result = VerificationResult(
    status="BLOCKED",
    claims=[
        claim,
        unsupported_claim,
        no_evidence_claim,
    ],
    blocked_reasons=[
        "Unsupported factual claim."
    ],
)

assert result.is_verified is False

print(
    "Fail-closed verification: PASSED"
)


print(
    "\nStep 1 models: ALL TESTS PASSED"
)