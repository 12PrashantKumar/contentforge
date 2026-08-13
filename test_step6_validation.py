from agents.verifier import verify_variant


SOURCE_URL = (
    "https://example.com/source"
)


SOURCE_TEXT = """
The model scored 82% on SWE-bench.
"""


def make_variant(
    post: str,
) -> dict:

    return {
        "id": "test-1",
        "post": post,
        "thread": [],
        "first_reply": (
            "Source: "
            + SOURCE_URL
        ),
        "media_suggestion": None,
        "alt_text": None,
        "char_count": len(post),
        "reply_surface": (
            "The engineering tradeoff "
            "between model performance "
            "and inference speed."
        ),
    }


# ==================================================
# TEST 1 — VALID VARIANT
# ==================================================

valid_variant = make_variant(
    "Anthropic's new model scored 82% "
    "on SWE-bench in internal testing, "
    "according to the source."
)


result = verify_variant(
    variant=valid_variant,
    source_text=SOURCE_TEXT,
    source_url=SOURCE_URL,
    model_name="groq",
)


print(
    "Valid variant:"
)

print(
    result.status
)

print(
    "Blocked reasons:",
    result.blocked_reasons,
)


assert result.status == "VERIFIED"

print(
    "Valid variant: PASSED"
)


# ==================================================
# TEST 2 — URL INSIDE POST
# ==================================================

bad_url_variant = make_variant(
    "Anthropic's new model scored 82% "
    "on SWE-bench in internal testing. "
    "Read the full source here: "
    "https://example.com"
)


result = verify_variant(
    variant=bad_url_variant,
    source_text=SOURCE_TEXT,
    source_url=SOURCE_URL,
    model_name="groq",
)


print(
    "\nURL-in-post variant:"
)

print(
    result.status
)

print(
    result.blocked_reasons
)


assert result.status == "BLOCKED"


assert any(
    "URL" in reason
    or "url" in reason
    for reason in result.blocked_reasons
)


print(
    "URL validation: PASSED"
)


# ==================================================
# TEST 3 — OVERSIZED POST
# ==================================================

long_variant = make_variant(
    "A" * 281
)


result = verify_variant(
    variant=long_variant,
    source_text=SOURCE_TEXT,
    source_url=SOURCE_URL,
    model_name="groq",
)


print(
    "\nLong post:"
)

print(
    result.status
)

print(
    result.blocked_reasons
)


assert result.status == "BLOCKED"


print(
    "Length validation: PASSED"
)


# ==================================================
# FINAL RESULT
# ==================================================

print(
    "\nStep 6 deterministic gate: "
    "ALL TESTS PASSED"
)