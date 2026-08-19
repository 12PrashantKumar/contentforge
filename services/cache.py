"""


Seen-cache: stops the pipeline re-posting a finding it already handled.

Design : one String key per finding, each with its own 30-day TTL.
  key:    contentforge:seen:<source_id or source_url>
  value:  "1"
  expiry: 30 days, per key (so each finding expires on its own timer)

  mark_seen(finding)  -> SET key "1" EX 2592000
  is_seen(finding)    -> EXISTS key

Why key on source_id first: for arXiv it's the stable paper id; for news it's
the url. source_id falls back to source_url when empty.

If Redis is unreachable, we FAIL OPEN (treat as not-seen) rather than crash the
pipeline - a dedup miss is annoying, a hard crash is worse. The approval gate is
the backstop anyway.
"""

import redis

from core.config import REDIS_URL


_TTL_SECONDS = 30 * 24 * 60 * 60          # 30 days
_PREFIX = "contentforge:seen:"

_client = redis.from_url(REDIS_URL, decode_responses=True)


def _key(finding) -> str:
    ident = finding.source_id or finding.source_url
    return f"{_PREFIX}{ident}"


def is_seen(finding) -> bool:
    """True if this finding was already handled within the TTL window."""
    try:
        return _client.exists(_key(finding)) == 1
    except redis.RedisError as exc:
        print(f"[cache] redis unavailable ({exc}); treating as not-seen")
        return False          # fail open


def mark_seen(finding) -> None:
    """Record this finding as handled, with a 30-day expiry."""
    try:
        _client.set(_key(finding), "1", ex=_TTL_SECONDS)
    except redis.RedisError as exc:
        print(f"[cache] could not mark seen ({exc})")


def filter_unseen(findings: list) -> list:
    """Drop findings already handled. Used before ranking so the ranker
    picks the best UNSEEN item, not the best item you already posted."""
    return [f for f in findings if not is_seen(f)]