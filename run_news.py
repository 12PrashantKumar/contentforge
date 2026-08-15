from graph import build_news_graph

graph = build_news_graph()
final = graph.invoke({"days": 3})

status = final.get("status")
print("STATUS:", status)
if final.get("error"):
    print("ERROR:", final["error"])

if status == "nothing_interesting":
    print("Synthesis rejected the finding — not teardown-worthy. (This is normal and correct.)")
elif status == "ok":
    draft = final["draft"]
    print(f"\nARCHETYPE: {draft.archetype}")
    for v in draft.variants:
        print(f"\n[{final['verifications'][v.id].status}] {v.post}")