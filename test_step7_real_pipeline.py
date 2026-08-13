from sources.web import fetch_news
from writers.x_writer import write
from services.validators import validate_variant
from agents.verifier import verify_variant


# ============================================================
# CONFIG
# ============================================================

ARCHETYPE = "TIL_SNIPPET"


# ============================================================
# 1. FETCH FINDING
# ============================================================

print("=" * 80)
print("STEP 7 — REAL CONTENTFORGE VERIFICATION PIPELINE")
print("=" * 80)

print("\nFetching recent AI news...")

findings = fetch_news(days=1)

if not findings:
    raise RuntimeError(
        "No findings returned from Tavily."
    )


finding = findings[0]


print("\n" + "=" * 80)
print("SELECTED FINDING")
print("=" * 80)

print(
    f"Title: {finding.title}"
)

print(
    f"URL: {finding.source_url}"
)

print(
    f"Content length: {len(finding.content)}"
)


# ============================================================
# 2. GENERATE X DRAFT
# ============================================================

print("\n" + "=" * 80)
print("GENERATING X DRAFT")
print("=" * 80)

draft = write(
    finding=finding,
    archetype=ARCHETYPE,
)


print(
    f"\nStatus: {draft.status}"
)

print(
    f"Archetype: {draft.archetype}"
)

print(
    f"Variants: {len(draft.variants)}"
)

print(
    f"Source URL preserved: "
    f"{draft.source_url == finding.source_url}"
)


# ============================================================
# 3. HANDLE INSUFFICIENT INPUT
# ============================================================

if draft.status == "insufficient_input":

    print(
        "\nWriter reported insufficient input."
    )

    print(
        f"Reason: {draft.notes}"
    )

    raise SystemExit(0)


# ============================================================
# 4. VERIFY EVERY VARIANT
# ============================================================

verification_results = []


for index, variant in enumerate(
    draft.variants,
    start=1,
):

    print("\n" + "=" * 80)

    print(
        f"VARIANT {index} — {variant.id}"
    )

    print("=" * 80)

    print(
        "\nPOST:"
    )

    print(
        variant.post
    )

    print(
        f"\nCharacter count: "
        f"{variant.char_count}"
    )

    print(
        "\nFirst reply:"
    )

    print(
        variant.first_reply
    )

    # --------------------------------------------------------
    # Convert typed DraftVariant to the dictionary shape
    # expected by validate_variant() and verify_variant()
    # --------------------------------------------------------

    variant_dict = {
        "id": variant.id,
        "post": variant.post,
        "thread": variant.thread,
        "first_reply": variant.first_reply,
        "media_suggestion": variant.media_suggestion,
        "alt_text": variant.alt_text,
        "char_count": variant.char_count,
        "reply_surface": variant.reply_surface,
    }

    # --------------------------------------------------------
    # Deterministic validation
    # --------------------------------------------------------

    print(
        "\nDeterministic validation:"
    )

    try:

        validate_variant(
            variant_dict,
            finding.source_url,
        )

        print(
            "PASSED"
        )

    except ValueError as exc:

        print(
            "BLOCKED"
        )

        print(
            f"Reason: {exc}"
        )

        verification_results.append(
            None
        )

        continue

    # --------------------------------------------------------
    # Claim-level verification
    # --------------------------------------------------------

    print(
        "\nClaim verification:"
    )

    verification = verify_variant(
        variant=variant_dict,
        source_text=finding.content,
        source_url=finding.source_url,
        model_name="groq",
    )

    verification_results.append(
        verification
    )

    # --------------------------------------------------------
    # Print claims
    # --------------------------------------------------------

    if not verification.claims:

        print(
            "No factual claims extracted."
        )

    else:

        for claim_index, claim in enumerate(
            verification.claims,
            start=1,
        ):

            print(
                f"\nClaim #{claim_index}:"
            )

            print(
                f"  Claim: "
                f"{claim.claim_text}"
            )

            print(
                f"  Verdict: "
                f"{claim.verdict}"
            )

            print(
                f"  Evidence: "
                f"{claim.evidence_text}"
            )

            print(
                f"  Source: "
                f"{claim.source_url}"
            )

            print(
                f"  Judged by: "
                f"{claim.judged_by}"
            )

    # --------------------------------------------------------
    # Final variant status
    # --------------------------------------------------------

    print(
        "\nFINAL VARIANT STATUS:"
    )

    print(
        verification.status
    )

    if verification.blocked_reasons:

        print(
            "\nBlocked reasons:"
        )

        for reason in (
            verification.blocked_reasons
        ):

            print(
                f"  - {reason}"
            )


# ============================================================
# 5. FINAL SUMMARY
# ============================================================

print("\n" + "=" * 80)
print("STEP 7 SUMMARY")
print("=" * 80)


verified_count = sum(
    1
    for result in verification_results
    if result is not None
    and result.is_verified
)


blocked_count = len(
    verification_results
) - verified_count


print(
    f"Total variants: "
    f"{len(draft.variants)}"
)

print(
    f"Verified variants: "
    f"{verified_count}"
)

print(
    f"Blocked variants: "
    f"{blocked_count}"
)


print(
    "\nStep 7 real pipeline: COMPLETE"
)