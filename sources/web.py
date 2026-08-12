from datetime import datetime, timezone

from tavily import TavilyClient

from core.config import TAVILY_API_KEY
from core.models import Finding


# One Tavily client for this research adapter.
client = TavilyClient(
    api_key=TAVILY_API_KEY
)


def fetch_news(days: int = 1) -> list[Finding]:
    """
    Fetch recent AI news and convert valid results
    into provenance-preserving Finding objects.

    Every Finding must have:
    - title
    - usable content
    - raw source URL
    - source type
    - fetch timestamp
    """

    response = client.search(
        query="latest AI news",
        topic="news",
        days=days,
        max_results=5,
        include_raw_content=True,
    )

    findings: list[Finding] = []

    for result in response.get(
        "results",
        [],
    ):

        title = (
            result.get("title")
            or ""
        ).strip()

        # Prefer Tavily's raw content because
        # the verifier will eventually need enough
        # source text to verify claims.
        content = (
            result.get("raw_content")
            or result.get("content")
            or ""
        ).strip()

        # IMPORTANT:
        # Keep this as the original URL.
        #
        # Correct:
        # https://example.com/article
        #
        # NOT:
        # [https://example.com/article](https://example.com/article)
        source_url = (
            result.get("url")
            or ""
        ).strip()

        # Reject malformed findings.
        if not title:
            continue

        if not source_url:
            continue

        if not content:
            continue

        finding = Finding(
            title=title,
            content=content,
            source_url=source_url,
            source_type="news",
            fetched_at=datetime.now(
                timezone.utc
            ),
            source_id=source_url,
        )

        findings.append(finding)

    return findings