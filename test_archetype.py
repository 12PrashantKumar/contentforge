from sources.arxiv_source import fetch_papers
from writers.x_writer import write

papers = fetch_papers(max_results=5)
finding = papers[0]
print("PAPER:", finding.title)
print("ABSTRACT LEN:", len(finding.content), "\n")

# try the same abstract against different archetypes
for archetype in ["TIL_SNIPPET", "BENCHMARK_COMPARISON", "CONTRARIAN_TAKE", "TEARDOWN_THREAD"]:
    print("=" * 60)
    print(f"ARCHETYPE: {archetype}")
    try:
        draft = write(finding, archetype)
        print(f"  status: {draft.status}")
        if draft.status == "ok":
            for v in draft.variants:
                print(f"  - {v.post[:150]}")
        else:
            print(f"  notes: {draft.notes}")
    except Exception as e:
        print(f"  raised: {e}")