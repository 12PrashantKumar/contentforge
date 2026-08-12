from services.validators import (
    validate_generation,
)


SOURCE_URL = (
    "https://example.com/article"
)


def make_valid_variant(
    post: str,
) -> dict:

    return {
        "id": "a",
        "post": post,
        "thread": [],
        "first_reply": (
            "Source: "
            + SOURCE_URL
        ),
        "media_suggestion": None,
        "alt_text": None,

        # This value is intentionally included
        # for compatibility with the current JSON
        # contract.
        #
        # Python, not the LLM, is responsible for
        # determining the real character count.
        "char_count": len(post),

        "reply_surface": (
            "The engineering tradeoff "
            "between approach A and B."
        ),
    }


# ==========================================
# VALID GENERATION
# ==========================================

post = (
    "The interesting part of this "
    "architecture is where the retrieval "
    "boundary sits."
)


result = {
    "status": "ok",
    "archetype": "TIL_SNIPPET",
    "variants": [
        make_valid_variant(
            post + " A"
        ),
        make_valid_variant(
            post + " B"
        ),
        make_valid_variant(
            post + " C"
        ),
    ],
    "rejected_angle": None,
    "notes": None,
}


validate_generation(
    result,
    SOURCE_URL,
)


print(
    "Valid generation test: PASSED"
)


# ==========================================
# CHARACTER COUNT
# ==========================================
#
# The LLM's char_count is NOT trusted.
# Python calculates len(post) itself.
#
# Therefore an incorrect LLM-provided
# char_count must NOT cause validation
# to fail.
# ==========================================

bad_variant = make_valid_variant(
    post
)

bad_variant["char_count"] = 999


bad_result = {
    "status": "ok",
    "archetype": "TIL_SNIPPET",
    "variants": [
        bad_variant,
        make_valid_variant(
            post + " A"
        ),
        make_valid_variant(
            post + " B"
        ),
    ],
    "rejected_angle": None,
    "notes": None,
}


validate_generation(
    bad_result,
    SOURCE_URL,
)


print(
    "char_count test: PASSED "
    "(LLM value ignored)"
)


# ==========================================
# URL IN POST
# ==========================================

bad_post = (
    "This post contains "
    "https://example.com"
)


bad_url_variant = make_valid_variant(
    bad_post
)


bad_url_result = {
    "status": "ok",
    "archetype": "TIL_SNIPPET",
    "variants": [
        bad_url_variant,
        make_valid_variant(
            post + " A"
        ),
        make_valid_variant(
            post + " B"
        ),
    ],
    "rejected_angle": None,
    "notes": None,
}


try:

    validate_generation(
        bad_url_result,
        SOURCE_URL,
    )

    print(
        "URL test: FAILED"
    )

except ValueError:

    print(
        "URL test: PASSED"
    )