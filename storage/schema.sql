-- Run once against the contentforge Neon database.
--
-- Three tables:
--   drafts        - one row per variant produced by a run
--   verifications - the claim/evidence trail for each variant (JSON)
--   posts         - what actually went out to X
--
-- Blocked variants are KEPT (status = 'blocked_by_verifier'). They are
-- evidence the system works and the best demo material - never discarded.

CREATE TABLE IF NOT EXISTS drafts (
    id            BIGSERIAL PRIMARY KEY,
    run_id        TEXT NOT NULL,              -- groups variants from one run
    variant_id    TEXT NOT NULL,              -- 'a' | 'b' | 'c'
    archetype     TEXT NOT NULL,              -- SHIP_LOG, etc.
    source_type   TEXT NOT NULL,              -- own_work | news | paper
    source_url    TEXT NOT NULL,
    post_text     TEXT NOT NULL,              -- the variant's main post
    thread        JSONB DEFAULT '[]'::jsonb,  -- thread tweets if any
    first_reply   TEXT,                       -- link reply if any
    status        TEXT NOT NULL DEFAULT 'pending',
                  -- pending | approved | rejected | posted | blocked_by_verifier
    edited_text   TEXT,                       -- set when you edit before approving
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    decided_at    TIMESTAMPTZ                 -- when you approved/rejected
);

CREATE INDEX IF NOT EXISTS idx_drafts_status ON drafts(status);
CREATE INDEX IF NOT EXISTS idx_drafts_run    ON drafts(run_id);

CREATE TABLE IF NOT EXISTS verifications (
    id            BIGSERIAL PRIMARY KEY,
    draft_id      BIGINT NOT NULL REFERENCES drafts(id) ON DELETE CASCADE,
    status        TEXT NOT NULL,              -- VERIFIED | BLOCKED | SKIPPED
    claims        JSONB NOT NULL DEFAULT '[]'::jsonb,  -- full claim+evidence trail
    blocked_reasons JSONB DEFAULT '[]'::jsonb,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_verif_draft ON verifications(draft_id);

CREATE TABLE IF NOT EXISTS posts (
    id            BIGSERIAL PRIMARY KEY,
    draft_id      BIGINT NOT NULL REFERENCES drafts(id) ON DELETE CASCADE,
    platform      TEXT NOT NULL DEFAULT 'x',
    external_id   TEXT,                       -- the X post id, once posted
    posted_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);