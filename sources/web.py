from datetime import datetime, timezone
import re

from tavily import TavilyClient

from core.config import TAVILY_API_KEY
from core.models import Finding


client = TavilyClient(
    api_key=TAVILY_API_KEY
)


def clean_source_url(url: str) -> str:
    """
    Convert a Markdown URL into its canonical raw URL.

    Example:

    [https://example.com](https://example.com)

    becomes:

    https://example.com
    """

    url = url.strip()

    match = re.fullmatch(
        r"\[([^\]]+)\]\((https?://[^)]+)\)",
        url,
    )

    if match:
        return match.group(2).strip()

    return url


def fetch_news(days: int = 1) -> list[Finding]:
    """
    Fetch recent AI news and convert valid results
    into provenance-preserving Finding objects.
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

        content = (
            result.get("raw_content")
            or result.get("content")
            or ""
        ).strip()

        raw_url = (
            result.get("url")
            or ""
        ).strip()

        # Normalize the URL BEFORE it enters Finding.
        source_url = clean_source_url(
            raw_url
        )

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