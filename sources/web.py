from datetime import datetime, timezone

from tavily import TavilyClient

from core.config import TAVILY_API_KEY
from core.models import Finding


def fetch_news(days: int = 1) -> list[Finding]:
    client = TavilyClient(api_key=TAVILY_API_KEY)

    response = client.search(
        query="latest AI news",
        topic="news",
        days=days,
        max_results=5,
        include_raw_content=True,
    )

    findings = []

    for result in response.get("results", []):
        title = result.get("title", "").strip()
        content = result.get("raw_content") or result.get("content", "")
        source_url = result.get("url", "").strip()

        if not source_url or not content.strip():
            continue

        finding = Finding(
            title=title,
            content=content,
            source_url=source_url,
            source_type="news",
            fetched_at=datetime.now(timezone.utc),
            source_id=source_url,
        )

        findings.append(finding)

    return findings