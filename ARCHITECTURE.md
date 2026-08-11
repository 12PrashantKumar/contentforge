## Problem
An agent that posts about AI without grounding will confidently invent a
funding round, misattribute a paper, or overstate a benchmark - under my
name. The engineering problem is trustworthy generation, not posting.
 
## Core promise
No externally factual claim is published unless the system can show the
source it came from and the evidence that supports it.
 
## Sources
| Source | Contributes | Verification |
|----------|------------------------|-------------------------|
| Web news | releases, benchmarks | strict external |
| arXiv | papers, abstracts | strict external |
| Own work | bugs, tradeoffs | first-party; approval |
 
## Pipeline
policy -> supervisor -> [web | arxiv | own work] -> ranker ->
synthesis -> writer -> claim extractor -> verifier -> validators ->
approval queue -> publish
 
## Domain objects
Finding -> Insight -> Draft -> Claim[] -> VerificationResult ->
Approval -> PublishedPost
(source_url is carried from Finding all the way to Claim)
 
## What is LLM vs code
LLM: claim extraction, evidence judgement, synthesis, ranking, writing
Code: mix policy, char limits, URL checks, dedup, state transitions
 
## Draft states
draft -> verified | blocked_by_verifier
verified -> pending_approval -> approved | rejected
approved -> published
(blocked drafts are KEPT - they are the evidence the system works)
 
## Deliberately not in V1
accounts, billing, multi-tenancy, RBAC, a real frontend