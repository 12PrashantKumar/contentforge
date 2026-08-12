import re
from urllib.parse import urlparse


MAX_X_LENGTH = 280
MIN_X_LENGTH = 70


BANNED_PHRASES = [
    "RT if",
    "reply YES",
    "follow for more",
    "drop a",
    "comment 'X' and I'll send it",
    "bookmark this",
    "most devs don't know this",
    "steal this before I delete it",
]


def validate_url(
    source_url: str,
) -> None:

    if not source_url:
        raise ValueError(
            "Missing source URL."
        )

    parsed = urlparse(source_url)

    if parsed.scheme not in {
        "http",
        "https",
    }:
        raise ValueError(
            "Source URL must use HTTP or HTTPS."
        )

    if not parsed.netloc:
        raise ValueError(
            "Source URL is missing a domain."
        )


def validate_length(
    text: str,
) -> None:

    length = len(text)

    if length > MAX_X_LENGTH:
        raise ValueError(
            f"Post exceeds {MAX_X_LENGTH} characters. "
            f"Actual: {length}"
        )

    if length < MIN_X_LENGTH:
        raise ValueError(
            f"Post is below the recommended "
            f"{MIN_X_LENGTH}-character minimum. "
            f"Actual: {length}"
        )


def validate_no_url_in_post(
    text: str,
) -> None:

    url_pattern = re.compile(
        r"(https?://|www\.)\S+",
        re.IGNORECASE,
    )

    if url_pattern.search(text):
        raise ValueError(
            "Post body contains a URL. "
            "URLs belong in first_reply."
        )


def validate_no_emojis(
    text: str,
) -> None:

    # Broad emoji/symbol ranges.
    emoji_pattern = re.compile(
        "["
        "\U0001F300-\U0001FAFF"
        "\U00002700-\U000027BF"
        "\U0001F1E6-\U0001F1FF"
        "]"
    )

    if emoji_pattern.search(text):
        raise ValueError(
            "Post contains an emoji."
        )


def validate_hashtag_count(
    text: str,
) -> None:

    count = text.count("#")

    if count > 1:
        raise ValueError(
            "Post contains more than one hashtag."
        )


def validate_banned_phrases(
    text: str,
) -> None:

    lowered = text.lower()

    for phrase in BANNED_PHRASES:

        if phrase.lower() in lowered:
            raise ValueError(
                f"Post contains banned phrase: "
                f"{phrase}"
            )


def validate_mentions(
    text: str,
    allowed_mentions: list[str] | None = None,
) -> None:

    allowed_mentions = (
        allowed_mentions or []
    )

    mentions = re.findall(
        r"@[A-Za-z0-9_]+",
        text,
    )

    for mention in mentions:

        if mention not in allowed_mentions:
            raise ValueError(
                f"Unauthorized mention: {mention}"
            )


def validate_first_reply(
    first_reply: str | None,
) -> None:

    if first_reply is None:
        return

    if len(first_reply) > 280:
        raise ValueError(
            "first_reply exceeds 280 characters."
        )


def validate_reply_surface(
    reply_surface: str,
) -> None:

    if not reply_surface.strip():
        raise ValueError(
            "Missing reply_surface."
        )


def validate_variant(
    variant: dict,
    source_url: str,
) -> None:

    required_fields = {
        "id",
        "post",
        "thread",
        "first_reply",
        "media_suggestion",
        "alt_text",
        "char_count",
        "reply_surface",
    }

    missing = (
        required_fields
        - variant.keys()
    )

    if missing:
        raise ValueError(
            f"Variant missing fields: "
            f"{sorted(missing)}"
        )

    post = variant["post"]

    if not isinstance(post, str):
        raise ValueError(
            "Variant post must be a string."
        )

    # IMPORTANT:
    # char_count is calculated by Python.
    actual_char_count = len(post)

   

    validate_length(post)
    validate_no_url_in_post(post)
    validate_no_emojis(post)
    validate_hashtag_count(post)
    validate_banned_phrases(post)
    validate_mentions(post)
    validate_first_reply(
        variant["first_reply"]
    )
    validate_reply_surface(
        variant["reply_surface"]
    )

    validate_url(source_url)


def validate_generation(
    result: dict,
    source_url: str,
) -> None:

    if result.get("status") == "insufficient_input":
        return

    if result.get("status") != "ok":
        raise ValueError(
            "Generation status must be 'ok' "
            "or 'insufficient_input'."
        )

    if not result.get("archetype"):
        raise ValueError(
            "Missing archetype."
        )

    variants = result.get(
        "variants"
    )

    if not isinstance(variants, list):
        raise ValueError(
            "variants must be a list."
        )

    if len(variants) != 3:
        raise ValueError(
            "Exactly 3 variants are required."
        )

    for variant in variants:

        validate_variant(
            variant,
            source_url,
        )

    rejected_angle = result.get(
        "rejected_angle"
    )

    if rejected_angle is not None:
        if not isinstance(
            rejected_angle,
            str,
        ):
            raise ValueError(
                "rejected_angle must be "
                "a string or null."
            )