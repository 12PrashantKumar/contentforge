from graph import build_graph


LINE = "=" * 78


def main():
    graph = build_graph()

    # single run, linear spine. archetype is fixed this week.
    initial = {"days": 1}
    final = graph.invoke(initial)

    status = final.get("status")

    print(LINE)
    print(f"FINAL STATUS: {status}")
    if final.get("error"):
        print(f"ERROR: {final['error']}")
    print(LINE)

    # explicit handling of every non-ok terminal state (no silent failure)
    if status == "no_findings":
        print("No findings returned. Check TAVILY_API_KEY / the query.")
        return
    if status == "no_archetype":
        print("Strategy found no valid archetype for this source. Nothing to write.")
        return
    if status == "insufficient_input":
        print("Writer judged the source insufficient. Nothing to verify.")
        return
    if status == "write_failed":
        print("Writer failed to produce valid variants.")
        return
    if status == "error":
        print("A node raised. See ERROR above.")
        return

    # --- source ---
    finding = final["finding"]
    print("\nSOURCE")
    print(f"  title: {finding.title}")
    print(f"  url:   {finding.source_url}")
    print(f"  chars: {len(finding.content)}")

    # --- draft + verification, per variant ---
    draft = final["draft"]
    verifications = final["verifications"]

    print(f"\nARCHETYPE: {draft.archetype}")
    print(f"VARIANTS:  {len(draft.variants)}")

    passed = 0
    for variant in draft.variants:
        result = verifications[variant.id]
        print("\n" + "-" * 78)
        print(f"VARIANT {variant.id}   [{result.status}]")
        print(f"  post: {variant.post}")

        if result.claims:
            for i, claim in enumerate(result.claims, 1):
                mark = "OK  " if claim.is_supported else "FAIL"
                print(f"\n    [{mark}] claim {i}: {claim.claim_text}")
                print(f"           verdict:  {claim.verdict}")
                if claim.evidence_text:
                    print(f"           evidence: \"{claim.evidence_text[:200]}\"")
                else:
                    print(f"           evidence: (none found)")
        else:
            print("    (no factual claims extracted)")

        if result.blocked_reasons:
            print("\n    BLOCKED:")
            for r in result.blocked_reasons:
                print(f"      - {r}")

        if result.status == "VERIFIED":
            passed += 1

    print("\n" + LINE)
    print(f"RESULT: {passed}/{len(draft.variants)} variants VERIFIED")
    if final.get("status") == "all_blocked":
        print("All variants blocked. Read the reasons — overstatement is common")
        print("and blocking it is correct, not a bug.")
    print(LINE)


if __name__ == "__main__":
    main()