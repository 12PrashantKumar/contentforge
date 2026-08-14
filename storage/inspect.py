from storage.db import list_pending, list_blocked

print("pending:", len(list_pending()))
print("blocked:", len(list_blocked()))

print("\n--- PENDING ---")
for r in list_pending():
    print(f"  [{r['variant_id']}] {r['status']}: {r['post_text'][:60]}")

print("\n--- BLOCKED ---")
for r in list_blocked():
    print(f"  [{r['variant_id']}]: {r['post_text'][:60]}")