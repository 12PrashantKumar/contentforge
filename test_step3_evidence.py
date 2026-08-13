from agents.verifier import find_evidence


SOURCE = """
Anthropic released the model on Tuesday.

In internal testing it scored 82% on SWE-bench
Verified, up from 71%.

The company said inference is up to 3x faster
on long contexts.
"""


print("=" * 70)
print("STEP 3 — EVIDENCE RETRIEVAL")
print("=" * 70)


# ==========================================
# CASE A — DIRECTLY SUPPORTED
# ==========================================

claim_a = (
    "scores 82% on SWE-bench"
)

evidence_a = find_evidence(
    claim_a,
    SOURCE,
)

print("\nA — SWE-bench claim")
print("Evidence:")
print(repr(evidence_a))


# ==========================================
# CASE B — DIRECTLY SUPPORTED
# ==========================================

claim_b = (
    "inference is up to 3x faster "
    "on long contexts"
)

evidence_b = find_evidence(
    claim_b,
    SOURCE,
)

print("\nB — inference speed claim")
print("Evidence:")
print(repr(evidence_b))


# ==========================================
# CASE C — NOT IN SOURCE
# ==========================================

claim_c = (
    "raised $40M in Series B"
)

evidence_c = find_evidence(
    claim_c,
    SOURCE,
)

print("\nC — funding claim")
print("Evidence:")
print(repr(evidence_c))


# ==========================================
# BASIC CHECKS
# ==========================================

assert evidence_a
assert evidence_b

assert (
    evidence_c == ""
    or evidence_c is None
)


print(
    "\nStep 3 evidence retrieval: PASSED"
)