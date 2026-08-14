# ContentForge

A multi-agent system that turns my own development work into platform-ready posts — and won't publish a factual claim it can't verify against a real source.

Built to solve a real problem: an AI that posts about tech will confidently invent a benchmark number, misattribute a release, or overstate a result — under your name. ContentForge treats trustworthy generation as the actual engineering problem, not the posting.

> **Status:** work in progress. The first-party path (my own work → verified, approved posts) is built and running. External sources (news, papers) and automated scheduling are planned — see the roadmap below.

---

## The idea

Two things make this more than a "post generator":

**A trust layer.** Every externally factual claim is extracted, checked against its cited source for supporting evidence, and blocked if unsupported. The verifier fails closed — no evidence means the claim does not publish. For first-party content ("I built X"), verification is skipped: you are the source of truth for your own work, and your own build updates aren't external facts to cite.

**An interview layer.** Instead of inventing expertise, the system reads my recent commits and *asks me* what actually happened — the bug, the tradeoff, the non-obvious detail. My answer becomes the post. Commit messages say *what* changed; the interview captures *why it mattered*.

Nothing publishes without a human approve / edit / reject gate.

---

## How it works (current, first-party path)

```
GitHub commits ─┐
                ├─> interview ─> strategy ─> write ─> verify ─> approval queue
your answer ────┘   (asks you)   (archetype   (3        (claim      (Streamlit:
                                  routing)     variants)  evidence,   approve /
                                                          fail-closed) edit / reject)
```

1. **Source** — reads my recent commits across repos (`sources/github_sources.py`).
2. **Interview** — shows me the week's work and asks what the interesting part was; my answer becomes a first-party finding (`sources/interview.py`).
3. **Strategy** — routes the finding to a content archetype, failing closed on external sources it can't yet safely handle (`writers/strategy.py`).
4. **Write** — generates three distinct variants in a defined voice, validated against deterministic rules (`writers/x_writer.py`).
5. **Verify** — extracts claims, finds evidence, judges each; skips external checks for first-party work (`agents/verifier.py`).
6. **Approve** — a Streamlit queue shows each variant with its verification trail; I approve, edit, or reject before anything posts (`approval_ui.py`).

The pipeline is an explicit LangGraph state machine — every node returns a status, so a failure surfaces as an error state instead of silently passing bad data downstream.

---

## Design principles

**LLM for judgment, code for rules.** Claim extraction, evidence judgment, synthesis, and writing use the LLM. Character limits, URL checks, content-mix policy, and validation are deterministic code — an LLM doing those badly is a bug that's hard to find.

**Fail closed.** The verifier blocks on missing or insufficient evidence rather than passing a clean-looking wrong answer.

**Provenance is mandatory.** A finding carries its source URL from the moment it enters the system; a claim without its source is treated as a bug.

---

## Stack

- **Python**, **LangGraph** (multi-agent orchestration)
- **Groq** (Llama 3.3 70B) via a single centralized LLM gateway with retry
- **PostgreSQL** (Neon) for drafts, verification trails, and posts
- **Streamlit** for the approval queue
- **Tavily** (web) and **PyGithub** (commits) as sources
- Deterministic validators for platform rules

---

## Project structure

```
contentforge/
├── run.py                    # runs the pipeline end to end, saves the run
├── approval_ui.py            # Streamlit approval queue
├── graph.py                  # LangGraph state machine
├── core/
│   ├── config.py             # env loading
│   ├── llm.py                # single Groq client + retry
│   ├── models.py             # Finding, Draft, Claim, VerificationResult...
│   └── state.py              # graph state
├── sources/
│   ├── web.py                # Tavily (news path, in progress)
│   ├── github_sources.py     # recent commits -> WorkItem
│   └── interview.py          # asks me about my week -> first-party Finding
├── writers/
│   ├── formats.md            # 10 post archetypes
│   ├── voice.md              # voice specification
│   ├── strategy.py           # archetype routing (fail-closed on external)
│   └── x_writer.py           # generate -> validate -> retry, 3 variants
├── agents/
│   └── verifier.py           # extract -> find evidence -> judge, fail-closed
├── services/
│   └── validators.py         # deterministic platform-rule checks
└── storage/
    ├── schema.sql            # drafts, verifications, posts
    └── db.py                 # persistence + approval-queue queries
```

---

## Roadmap

Built:
- First-party path: commits + interview → strategy → write → verify → approval queue
- Claim-level verification with stored evidence, fail-closed
- Postgres persistence and a human-in-the-loop approval UI

Planned:
- **Synthesis** — turn external news/papers into content an archetype can safely use
- **arXiv source** — research papers as input
- **Significance ranker** — filter signal from hype before writing
- **Redis** — seen-cache (no duplicate posts) + embedding cache
- **n8n scheduling** — hands-off runs on a cadence
- **Deployment** — containerized, with tracing and measured verifier precision/recall

---

## Notes

API keys and source data are not committed. Built as a learning project to understand multi-agent orchestration and trustworthy LLM generation end to end — the same evaluation discipline I applied to a production RAG system, aimed at a different problem: not "is the answer grounded?" but "can this claim be published under my name?"