from sources.web import fetch_news
from writers.x_writer import write


print(
    "Fetching recent AI news..."
)

findings = fetch_news(
    days=1
)

if not findings:

    raise RuntimeError(
        "No findings returned."
    )


finding = findings[0]


print("\n" + "=" * 80)

print(
    "SELECTED FINDING"
)

print("=" * 80)

print(
    f"Title: {finding.title}"
)

print(
    f"URL: {finding.source_url}"
)

print(
    f"Type: {finding.source_type}"
)

print(
    f"Content length: "
    f"{len(finding.content)}"
)


# IMPORTANT:
# For an external news Finding, we are testing
# a manually selected archetype only if the source
# actually supports it.
#
# Do NOT use SHIP_LOG for external news.
archetype = "TEARDOWN_THREAD"


print("\n" + "=" * 80)

print(
    f"GENERATING: {archetype}"
)

print("=" * 80)


draft = write(
    finding,
    archetype=archetype,
)


print(
    f"\nStatus: {draft.status}"
)

print(
    f"Archetype: {draft.archetype}"
)

print(
    f"Source URL: {draft.source_url}"
)


if draft.status == "insufficient_input":

    print(
        "\nInsufficient input:"
    )

    print(
        draft.notes
    )

    raise SystemExit(0)


print(
    "\nRejected angle:"
)

print(
    draft.rejected_angle
)


for variant in draft.variants:

    print("\n")

    print(
        "=" * 80
    )

    print(
        f"VARIANT {variant.id}"
    )

    print(
        "=" * 80
    )

    print(
        "\nPOST:"
    )

    print(
        variant.post
    )

    print(
        "\nCHAR COUNT:"
    )

    print(
        variant.char_count
    )

    print(
        "\nTHREAD:"
    )

    for index, tweet in enumerate(
        variant.thread,
        start=1,
    ):

        print(
            f"T{index}: {tweet}"
        )

    print(
        "\nFIRST REPLY:"
    )

    print(
        variant.first_reply
    )

    print(
        "\nMEDIA:"
    )

    print(
        variant.media_suggestion
    )

    print(
        "\nALT TEXT:"
    )

    print(
        variant.alt_text
    )

    print(
        "\nREPLY SURFACE:"
    )

    print(
        variant.reply_surface
    )