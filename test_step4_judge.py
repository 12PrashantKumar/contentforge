from agents.verifier import judge


TEST_CASES = [
    {
        "name": "Direct support",
        "claim": (
            "The model scores 82% on SWE-bench."
        ),
        "evidence": (
            "In internal testing it scored "
            "82% on SWE-bench Verified."
        ),
        "expected": "SUPPORTED",
    },

    {
        "name": "Different benchmark",
        "claim": (
            "The model scores 82% on MMLU."
        ),
        "evidence": (
            "In internal testing it scored "
            "82% on SWE-bench Verified."
        ),
        "expected": "UNSUPPORTED",
    },

    {
        "name": "Overstates benchmark scope",
        "claim": (
            "The model beats GPT-4 on all benchmarks."
        ),
        "evidence": (
            "In internal testing it scored "
            "82% on SWE-bench Verified."
        ),
        "expected": "UNSUPPORTED",
    },

    {
        "name": "Up to versus exact",
        "claim": (
            "Inference is exactly 3x faster."
        ),
        "evidence": (
            "The company said inference is "
            "up to 3x faster on long contexts."
        ),
        "expected": "UNSUPPORTED",
    },

    {
        "name": "Supported speed claim",
        "claim": (
            "Inference is up to 3x faster "
            "on long contexts."
        ),
        "evidence": (
            "The company said inference is "
            "up to 3x faster on long contexts."
        ),
        "expected": "SUPPORTED",
    },

    {
        "name": "Plans versus released",
        "claim": (
            "The company released the model."
        ),
        "evidence": (
            "The company plans to release "
            "the model next month."
        ),
        "expected": "UNSUPPORTED",
    },

    {
        "name": "Research preview versus production",
        "claim": (
            "The model is available in production."
        ),
        "evidence": (
            "The model is currently available "
            "as a research preview."
        ),
        "expected": "UNSUPPORTED",
    },

    {
        "name": "Direct factual support",
        "claim": (
            "The model was released on Tuesday."
        ),
        "evidence": (
            "Anthropic released the model on Tuesday."
        ),
        "expected": "SUPPORTED",
    },
]


print("=" * 70)
print("STEP 4 — CLAIM JUDGMENT")
print("=" * 70)


passed = 0


for index, case in enumerate(
    TEST_CASES,
    start=1,
):

    verdict = judge(
        case["claim"],
        case["evidence"],
    )

    correct = (
        verdict == case["expected"]
    )

    if correct:
        passed += 1

    status = (
        "PASS"
        if correct
        else "FAIL"
    )

    print(
        f"\n[{status}] Case {index}: "
        f"{case['name']}"
    )

    print(
        "Claim:",
        case["claim"],
    )

    print(
        "Evidence:",
        case["evidence"],
    )

    print(
        "Expected:",
        case["expected"],
    )

    print(
        "Got:",
        verdict,
    )


print("\n" + "=" * 70)

print(
    f"RESULT: {passed}/{len(TEST_CASES)} passed"
)


if passed != len(TEST_CASES):

    raise AssertionError(
        "Judge failed one or more cases. "
        "Do NOT proceed to Step 5."
    )


print(
    "Step 4 judge: ALL TESTS PASSED"
)