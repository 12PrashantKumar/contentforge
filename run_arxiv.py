from graph import build_arxiv_graph

final = build_arxiv_graph().invoke({})
status = final.get("status")
print("STATUS:", status)
if final.get("error"):
    print("ERROR:", final["error"])

if status == "ok":
    draft = final["draft"]
    print(f"\nARCHETYPE: {draft.archetype}")
    for v in draft.variants:
        print(f"\n[{final['verifications'][v.id].status}] {v.post}")