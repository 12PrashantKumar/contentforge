"""
Persistence for ContentForge. Saves each run's variants + their verification
trail, and exposes the queries the approval UI needs.

save_run()      - store all variants from one run (called after verify)
list_pending()  - variants awaiting your review
approve()/reject()/mark_edited()/mark_posted() - status transitions
init_db()       - create tables (run once)
"""

import json
import uuid
from dataclasses import asdict, is_dataclass

import psycopg
from psycopg.rows import dict_row

from core.config import CONTENTFORGE_DATABASE_URL


def _conn():
    return psycopg.connect(CONTENTFORGE_DATABASE_URL, row_factory=dict_row)


def init_db(schema_path: str = "storage/schema.sql") -> None:
    """Create the tables. Run once."""
    with open(schema_path, "r", encoding="utf-8") as f:
        sql = f.read()
    with _conn() as conn:
        conn.execute(sql)
        conn.commit()
    print("tables created.")


def _claims_to_json(verification) -> str:
    """Serialize a VerificationResult's claims (list of Claim dataclasses)."""
    claims = []
    for c in verification.claims:
        claims.append(asdict(c) if is_dataclass(c) else dict(c))
    return json.dumps(claims)


def save_run(finding, draft, verifications: dict) -> str:
    """
    Persist every variant of one run.

    finding        - the Finding it was written from
    draft          - the Draft (has .variants, .archetype)
    verifications  - {variant_id: VerificationResult}

    Returns the run_id.
    """
    run_id = str(uuid.uuid4())[:8]

    with _conn() as conn:
        for variant in draft.variants:
            vr = verifications.get(variant.id)

            # map verification status -> draft status
            if vr is None:
                draft_status = "pending"
            elif vr.status == "BLOCKED":
                draft_status = "blocked_by_verifier"
            else:
                draft_status = "pending"     # VERIFIED/SKIPPED -> awaits your review

            row = conn.execute(
                """
                INSERT INTO drafts
                  (run_id, variant_id, archetype, source_type, source_url,
                   post_text, thread, first_reply, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
                """,
                (
                    run_id,
                    variant.id,
                    draft.archetype,
                    finding.source_type,
                    finding.source_url,
                    variant.post,
                    json.dumps(getattr(variant, "thread", []) or []),
                    getattr(variant, "first_reply", None),
                    draft_status,
                ),
            ).fetchone()
            draft_id = row["id"]

            if vr is not None:
                conn.execute(
                    """
                    INSERT INTO verifications
                      (draft_id, status, claims, blocked_reasons)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (
                        draft_id,
                        vr.status,
                        _claims_to_json(vr),
                        json.dumps(vr.blocked_reasons or []),
                    ),
                )
        conn.commit()

    return run_id


def list_pending() -> list[dict]:
    """Variants awaiting review, newest first, with their verification trail."""
    with _conn() as conn:
        return conn.execute(
            """
            SELECT d.*, v.status AS verify_status, v.claims, v.blocked_reasons
            FROM drafts d
            LEFT JOIN verifications v ON v.draft_id = d.id
            WHERE d.status = 'pending'
            ORDER BY d.created_at DESC
            """
        ).fetchall()


def list_blocked() -> list[dict]:
    """Variants the verifier blocked - your proof + demo material."""
    with _conn() as conn:
        return conn.execute(
            """
            SELECT d.*, v.claims, v.blocked_reasons
            FROM drafts d
            LEFT JOIN verifications v ON v.draft_id = d.id
            WHERE d.status = 'blocked_by_verifier'
            ORDER BY d.created_at DESC
            """
        ).fetchall()


def approve(draft_id: int, edited_text: str | None = None) -> None:
    with _conn() as conn:
        conn.execute(
            """UPDATE drafts
               SET status='approved', edited_text=%s, decided_at=now()
               WHERE id=%s""",
            (edited_text, draft_id),
        )
        conn.commit()


def reject(draft_id: int) -> None:
    with _conn() as conn:
        conn.execute(
            "UPDATE drafts SET status='rejected', decided_at=now() WHERE id=%s",
            (draft_id,),
        )
        conn.commit()


def mark_posted(draft_id: int, external_id: str | None = None) -> None:
    with _conn() as conn:
        conn.execute(
            "UPDATE drafts SET status='posted' WHERE id=%s", (draft_id,)
        )
        conn.execute(
            "INSERT INTO posts (draft_id, external_id) VALUES (%s, %s)",
            (draft_id, external_id),
        )
        conn.commit()