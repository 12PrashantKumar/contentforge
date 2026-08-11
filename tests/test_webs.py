from sources.web import fetch_news


findings = fetch_news(days=1)

print(f"Found {len(findings)} findings\n")

for i, finding in enumerate(findings, start=1):
    print("=" * 80)
    print(f"Finding #{i}")
    print(f"Title: {finding.title}")
    print(f"URL: {finding.source_url}")
    print(f"Type: {finding.source_type}")
    print(f"Content length: {len(finding.content)}")
    print(f"Content preview:\n{finding.content[:1000]}")
    print()