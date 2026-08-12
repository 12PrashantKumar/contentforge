from writers.prompt_loader import (
    load_format,
)


format_text = load_format(
    "SHIP_LOG"
)


print(
    "Loaded format:"
)

print(
    format_text[:1000]
)


if "## 1. SHIP_LOG" not in format_text:

    raise AssertionError(
        "SHIP_LOG section was not loaded."
    )


if "## 2. BUILD_ANNOUNCE" in format_text:

    raise AssertionError(
        "Multiple archetypes were loaded."
    )


if "## 3. TEARDOWN_THREAD" in format_text:

    raise AssertionError(
        "Multiple archetypes were loaded."
    )


print(
    "\nPrompt loader test: PASSED"
)