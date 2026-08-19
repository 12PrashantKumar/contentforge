from graph import build_arxiv_graph

final = build_arxiv_graph().invoke({})
print("STATUS:", final.get("status"))

finding = final.get("finding")
if finding:
    print("\nSOURCE ABSTRACT:\n", finding.content[:1200])

draft = final.get("draft")
if draft:
    print("\n" + "="*70)
    for v in draft.variants:
        result = final["verifications"][v.id]
        print(f"\n[{result.status}] {v.post}")
        for c in result.claims:
            print(f"    {c.verdict}: {c.claim_text}")
            print(f"       evidence: {c.evidence_text[:150] if c.evidence_text else '(none found)'}")