# formats.md

> Loaded **one archetype at a time**, selected by the pipeline before generation.
> Never load all ten. Loading the whole file blurs the archetypes together and
> the generator produces an average of all of them.

Each archetype declares the ranking signal it targets. Those weights come from
X's open-sourced config: reply ≈ 27× a like, author-reply-back ≈ 150×,
profile click ≈ 24×, bookmark ≈ 20×, repost ≈ 2×, like = 1×. Write toward the
declared signal, not toward likes.

---

## 1. SHIP_LOG

**Target signal:** profile clicks (follows) · **Cadence:** 2–3× per week
**Length:** 180–280 chars · **Media:** screenshot or 15s screen capture

Highest-frequency unit. Proof that work is happening. Boring alone, compounding
in sequence.

```
{what shipped, stated flatly}

{the pipeline or mechanism, ideally as A → B → C}

{one detail that a builder would find non-obvious}
```

Illustrative shape (fill only with real work):

```
contentforge now routes drafts through an approval gate before anything posts.

Generator → critic → human approve/reject in Streamlit → queue.

The critic rejects ~40% of first drafts. Almost all rejections are the same
failure: correct facts, wrong register.
```

Rules: no number unless it was measured. Screenshot beats description. Never
explain why the project matters — the sequence does that over weeks. The third
element must be earned insight, not a formula — vary how you deliver it (a
reframe, a tradeoff, a constraint, a surprise, an opinion). Never open it with
the same stock phrase twice; if every ship log ends "the non-obvious part is…",
the feed reads as a template.
---

## 2. BUILD_ANNOUNCE

**Target signal:** profile clicks + reposts · **Cadence:** on real completion only
**Length:** hook ≤ 100 chars, body ≤ 250 · **Media:** demo video (<60s) strongly preferred

```
Built {thing} in {real timeframe}. {optional true constraint: "no framework",
"one file", "on free tier"}

{stack as a pipeline}

{what it actually does, one line, concrete}

{what surprised you}
```

Rules: the timeframe and constraint must be true. Never fire this for an
incremental change — overuse burns the format. Video with a hook in the first
2 seconds outperforms every other media type here.

---

## 3. TEARDOWN_THREAD

**Target signal:** bookmarks + dwell · **Cadence:** 1× per week
**Length:** 5–9 tweets, each 150–240 chars · **Media:** diagram or code screenshot on tweet 2 or 3

The credibility format. This is the one that gets read by people hiring for
LLM engineering roles.

```
T1  {specific claim or question about how a real system works — no "🧵",
     no "a thread", no "let's dive in". ≤ 120 chars.}
T2  {the setup: what problem this mechanism solves}
T3–T7 {one mechanism per tweet, in causal order. Each tweet must be
     independently true and independently interesting.}
T8  {the tradeoff or the part people get wrong}
T9  {optional: what you'd build differently — invites replies}
```

Rules: no tweet may be filler or transition. If a tweet only exists to set up
the next one, merge them. End on a tradeoff or open question, never a summary.
Links (repo, docs) go in a reply to T9, never inside the thread.

---

## 4. FAILURE_LESSON

**Target signal:** replies + bookmarks · **Cadence:** 1× per week
**Length:** 200–280 chars · **Media:** error screenshot if it exists

Highest trust-per-character format in the dev niche. Requires a real failure.

```
{what broke or what you got wrong, stated without drama}

{the actual cause — the specific, unglamorous reason}

{what you changed}
```

Rules: no moral, no "the lesson?", no closing wisdom. The reader extracts the
lesson. Never invent a failure to fill this slot — skip the day instead.

---

## 5. CONTRARIAN_TAKE

**Target signal:** replies (27×) · **Cadence:** 1–2× per week
**Length:** 120–240 chars · **Media:** none

The highest-value format per the ranking weights, and the easiest to get wrong.

```
{a specific technical position, narrow enough to be falsifiable}

{the reason, from your own experience}

{the condition under which you'd be wrong}
```

Rules: the take must be about a tool, technique, or engineering practice — never
about people, companies, or identity. It must be a position you actually hold.
The third line is mandatory; it converts an argument into a conversation.
"Most people are doing X wrong" is not a take, it is bait — reject it.

---

## 6. TIL_SNIPPET

**Target signal:** bookmarks · **Cadence:** 2–4× per week
**Length:** 90–180 chars · **Media:** code screenshot if it fits in 10 lines

Cheapest format to produce. Fills gap days without diluting the feed.

Two valid forms:

**Form A — a hands-on fact from your own work** (has a named API/flag/parameter):
```
TIL: {one specific technical fact, with the API/flag/parameter named}

{the consequence in one line}
```

**Form B — a concrete finding from a paper or source you read** (no API needed,
but must be a specific, quotable result or finding — not a vague vibe):
```
TIL: {the specific finding, result, or claim from the source, stated concretely}

{why it matters in one line}
```

Rules: Form A must be something learned in actual work this week. Form B must be
a real, specific finding you can point to in the source — a measured result, a
concrete observation, or a named effect ("task order changes the outcome"), not a
vague summary ("this paper is interesting"). If the source has no specific finding
worth stating plainly, skip it — do not pad. No generic tips. If it fits in one
line, use one line.
---

## 7. BENCHMARK_COMPARISON

**Target signal:** bookmarks + reposts · **Cadence:** 1–2× per month
**Length:** 200–280 chars, or a 5-tweet thread · **Media:** table or chart screenshot — mandatory

An asset — the kind of post that gets re-shared for months.

```
{Tool A} vs {Tool B} for {narrow, specific task}. Ran both.

{the setup: dataset size, metric, hardware — enough to be reproducible}

{the result, as numbers}

{the caveat that makes it honest}
```

Rules: every number must come from a run that actually happened. State the
sample size. If you did not measure it, this archetype is unavailable — do not
substitute published numbers and present them as your test.

---

## 8. PROMPT_ARTIFACT

**Target signal:** bookmarks · **Cadence:** 1× per week
**Length:** ≤ 200 chars caption + screenshot · **Media:** screenshot of the prompt or config

```
{what this prompt/config/snippet does, one line}

{the non-obvious part of why it works}

Full thing below.
```

Rules: the artifact goes in the first reply as a screenshot or plain text,
never as a link in the post body. Must be something in actual use.

---

## 9. WEEKLY_RECAP

**Target signal:** profile clicks · **Cadence:** 1× per week, same day each week
**Length:** 4–6 tweets, 120–200 chars each · **Media:** none needed

```
T1  Week {n} building {project}.
T2  Shipped: {2–3 concrete items}
T3  Broke: {what failed, honestly}
T4  Learned: {one specific thing}
T5  Next: {one committed item}
```

Rules: small numbers are fine and more credible than vague progress. Skipping
a week is better than padding one. This format only works if the week number
is real and continuous.

---

## 10. ORIGIN_NOTE

**Target signal:** follows · **Cadence:** maximum 1× per month
**Length:** 150–280 chars · **Media:** none

```
{a true then-vs-now, with real timeframes}

{one concrete thing that changed the trajectory}
```

Rules: strictly factual timeline. No inspiration framing, no advice appended.
Overuse turns the account into a motivation account — enforce the monthly cap
in the scheduler, not in the prompt.

---

## Weekly composition

The scheduler, not the generator, owns this distribution.

| Day | Archetype | Slot (IST) |
|---|---|---|
| Mon | TIL_SNIPPET or PROMPT_ARTIFACT | 19:00 |
| Tue | TEARDOWN_THREAD | 19:00 |
| Wed | SHIP_LOG | 19:30 |
| Thu | CONTRARIAN_TAKE | 19:00 |
| Fri | BUILD_ANNOUNCE or demo video | 19:00 |
| Sat | TIL_SNIPPET | 20:00 |
| Sun | WEEKLY_RECAP | 19:00 |

Evening IST ≈ US-morning, the strongest window for a US/global tech audience.
Constraints: max 2 originals per day, minimum 4 hours apart (X attenuates
repeated same-author posts in one feed). Never run the same archetype on
consecutive days. Rotate FAILURE_LESSON and BENCHMARK_COMPARISON in whenever
real material exists — they outrank the scheduled slot.

Posting is roughly 30% of the growth engine. The other 70% is 20–40 replies
per day to accounts 2–10× your size, which the pipeline does not generate.
