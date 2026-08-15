from graph import build_news_graph

graph = build_news_graph()
final = graph.invoke({"days": 3})

if final.get("status") != "ok":
    print("STATUS:", final.get("status"), "- run again, news changed")
else:
    finding = final["finding"]
    print("=" * 70)
    print("SOURCE TITLE:", finding.title)
    print("=" * 70)
    print("SOURCE CONTENT (what the verifier checks against):\n")
    print(finding.content[:1500])
    print("\n" + "=" * 70)
    print("CLAIMS + VERDICTS PER VARIANT:")
    print("=" * 70)
    for v in final["draft"].variants:
        result = final["verifications"][v.id]
        print(f"\n[{result.status}] {v.post}")
        for c in result.claims:
            print(f"    {c.verdict}: {c.claim_text}")
            if c.evidence_text:
                print(f"       evidence found: \"{c.evidence_text[:150]}\"")
            else:
                print(f"       evidence found: (none)")