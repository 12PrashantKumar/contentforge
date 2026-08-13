from agents.verifier import verify_variant


SOURCE_URL = (
    "https://example.com/anthropic"
)


SOURCE_TEXT = """
Anthropic released the model on Tuesday.

In internal testing it scored 82% on SWE-bench
Verified, up from 71%.

The company said inference is up to 3x faster
on long contexts.

The model is currently available as a research
preview.
"""


VARIANT = {
    "id": "test-1",

    "post": (
        "Anthropic's new model scores 82% on "
        "SWE-bench and has inference up to 3x "
        "faster on long contexts."
    ),

    "thread": [],

    "first_reply": (
        "Source: "
        + SOURCE_URL
    ),

    "media_suggestion": None,

    "alt_text": None,

    "char_count": 118,

    "reply_surface": (
        "The engineering implications "
        "of faster inference."
    ),
}


print("=" * 80)
print("STEP 5 — END-TO-END VERIFICATION")
print("=" * 80)


result = verify_variant(
    variant=VARIANT,
    source_text=SOURCE_TEXT,
    source_url=SOURCE_URL,
    model_name="groq",
)


print(
    "\nSTATUS:",
    result.status,
)


print(
    "\nCLAIMS:"
)


for index, claim in enumerate(
    result.claims,
    start=1,
):

    print(
        "\n" + "-" * 60
    )

    print(
        f"Claim #{index}:"
    )

    print(
        claim.claim_text
    )

    print(
        "\nEvidence:"
    )

    print(
        claim.evidence_text
    )

    print(
        "\nVerdict:"
    )

    print(
        claim.verdict
    )

    print(
        "\nSource:"
    )

    print(
        claim.source_url
    )

    print(
        "\nJudged by:"
    )

    print(
        claim.judged_by
    )


print(
    "\n" + "=" * 80
)


if result.blocked_reasons:

    print(
        "BLOCKED REASONS:"
    )

    for reason in result.blocked_reasons:

        print(
            "-",
            reason,
        )


print(
    "\nVerified:",
    result.is_verified,
)