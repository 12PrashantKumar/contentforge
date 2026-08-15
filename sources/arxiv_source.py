"""
Recent AI papers as Findings. Feeds the SAME external path as news
(synthesis -> teardown), but paper abstracts contain real mechanism detail,
so they teardown far better than thin news snippets.


"""

from datetime import datetime, timezone

import arxiv

from core.models import Finding


# categories worth pulling for an LLM/AI-engineering audience
DEFAULT_CATEGORIES = ["cs.CL", "cs.AI", "cs.LG"]


def fetch_papers(
    categories: list[str] = None,
    max_results: int = 5,
) -> list[Finding]:
    """
    Recent papers from the given arXiv categories, newest first.

    Returns provenance-preserving Findings with source_type='paper'.
    The abstract becomes the content the verifier grounds claims against.
    """
    categories = categories or DEFAULT_CATEGORIES

    # build an OR query across categories:  cat:cs.CL OR cat:cs.AI OR cat:cs.LG
    query = " OR ".join(f"cat:{c}" for c in categories)

    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate,   # newest first
    )

    client = arxiv.Client()
    findings: list[Finding] = []

    for result in client.results(search):
        title = (result.title or "").strip()
        abstract = (result.summary or "").strip()
        url = result.entry_id  # the arXiv abs URL

        # reject malformed
        if not title or not abstract or not url:
            continue

        findings.append(
            Finding(
                title=title,
                content=abstract,
                source_url=url,
                source_type="paper",
                fetched_at=datetime.now(timezone.utc),
                source_id=result.get_short_id(),
            )
        )

    return findings