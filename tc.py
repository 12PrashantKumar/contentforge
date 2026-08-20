from dataclasses import dataclass
from services.cache import is_seen, mark_seen

@dataclass
class Fake:
    source_id: str
    source_url: str = ""

f = Fake(source_id="test:upstash:123")

print("before:", is_seen(f))   # expect False
mark_seen(f)
print("after: ", is_seen(f))   # expect True