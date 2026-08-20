"""

FastAPI wrapper around the automated pipeline paths, so a scheduler (n8n) can
trigger runs over HTTP instead of someone typing `python run_arxiv.py`.

Exposes ONLY the automated external paths (arxiv, news). The first-party
interview path needs a human at a keyboard (input()), so it stays a manual
`python run.py` and is deliberately NOT here.

Each run generates variants, verifies them, and saves to Postgres. The endpoint
returns a small summary - you then review and approve in the Streamlit queue.

Run locally:  uvicorn api:app --reload --port 8000

"""

from fastapi import FastAPI
from pydantic import BaseModel

from graph import build_arxiv_graph, build_news_graph
from storage.db import save_run
from services.cache import mark_seen


app = FastAPI(title="ContentForge API")

# build the graphs once at startup, not per request
_arxiv_graph = build_arxiv_graph()
_news_graph = build_news_graph()


class RunResult(BaseModel):
    status: str
    archetype: str | None = None
    variants: int = 0
    verified: int = 0
    blocked: int = 0
    run_id: str | None = None
    title: str | None = None
    error: str | None = None


def _execute(graph, initial: dict) -> RunResult:
    """Run a graph, persist if it produced a draft, return a summary."""
    final = graph.invoke(initial)
    status = final.get("status")

    # terminal non-ok states - nothing to save
    if status != "ok" and status != "all_blocked":
        return RunResult(status=status, error=final.get("error"))

    draft = final.get("draft")
    verifications = final.get("verifications", {})
    finding = final.get("finding")

    if not draft:
        return RunResult(status=status, error=final.get("error"))

    verified = sum(1 for v in verifications.values() if v.status in ("VERIFIED", "SKIPPED"))
    blocked = sum(1 for v in verifications.values() if v.status == "BLOCKED")

    run_id = save_run(finding, draft, verifications)

    return RunResult(
        status=status,
        archetype=draft.archetype,
        variants=len(draft.variants),
        verified=verified,
        blocked=blocked,
        run_id=run_id,
        title=finding.title if finding else None,
    )
@app.get("/")
def root():
    return {
        "service": "ContentForge",
        "description": "Multi-agent content pipeline with claim-level verification",
        "docs": "/docs",
        "health": "/health",
    }

@app.get("/health")
def health():
    return {"status": "ok", "service": "contentforge"}


@app.post("/run/arxiv", response_model=RunResult)
def run_arxiv():
    return _execute(_arxiv_graph, {})


@app.post("/run/news", response_model=RunResult)
def run_news():
    return _execute(_news_graph, {"days": 3})