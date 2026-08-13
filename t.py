from sources.github_source import fetch_my_work

items = fetch_my_work(days=14)
print(f"found {len(items)} repos\n")
for item in items:
    print(item.summary())
    print("-" * 50)