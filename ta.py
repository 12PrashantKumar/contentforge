from sources.arxiv_source import fetch_papers

papers = fetch_papers(max_results=5)
print(f"found {len(papers)} papers\n")
for p in papers:
    print(p.title)
    print(f"  {p.source_url}")
    print(f"  abstract: {len(p.content)} chars\n")