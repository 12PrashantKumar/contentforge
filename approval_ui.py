"""
The human-in-the-loop approval queue. Reads pending variants from Postgres,
shows each with its verification trail, and lets you approve / edit / reject.

Run:  streamlit run approval_ui.py

Design notes:
  - own_work variants come through as SKIPPED (no claims) - the UI just shows
    the post and the buttons.
  - external variants (news/paper, later) come with claims + evidence - the UI
    renders each claim with its verdict so you approve seeing WHY it's trusted.
  - editing before approving is logged (db.approve stores edited_text). Since
    you have no published posts yet, YOUR edits are the first real signal of
    your actual voice.
"""

import json

import streamlit as st

from storage.db import approve, list_blocked, list_pending, reject


st.set_page_config(page_title="ContentForge - Approval Queue", layout="centered")


def _load_claims(raw):
    """claims come back from Postgres as JSON (or already-parsed list)."""
    if not raw:
        return []
    if isinstance(raw, list):
        return raw
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return []


def render_verification(row):
    """Show the verification trail, if any."""
    verify_status = row.get("verify_status")
    claims = _load_claims(row.get("claims"))

    if verify_status == "SKIPPED":
        st.caption("verification skipped - first-party work (you are the source of truth)")
        return

    if not claims:
        st.caption("no factual claims extracted")
        return

    st.markdown("**verification**")
    for c in claims:
        verdict = c.get("verdict", "?")
        icon = "✅" if verdict == "SUPPORTED" else "❌"
        st.markdown(f"{icon} `{verdict}` — {c.get('claim_text','')}")
        ev = c.get("evidence_text", "")
        if ev:
            st.caption(f"evidence: \"{ev[:200]}\"")


def pending_tab():
    rows = list_pending()

    if not rows:
        st.success("Queue empty. Nothing pending. Run the pipeline to generate drafts.")
        return

    st.caption(f"{len(rows)} variant(s) awaiting review")

    for row in rows:
        with st.container(border=True):
            st.markdown(f"**{row['archetype']}** · variant `{row['variant_id']}` · "
                        f"`{row['source_type']}`")

            # editable post text - this is where you fix register/typos
            edited = st.text_area(
                "post",
                value=row["post_text"],
                key=f"text_{row['id']}",
                height=110,
            )

            if row.get("first_reply"):
                st.caption(f"first reply: {row['first_reply']}")

            st.markdown(f"[source]({row['source_url']})")

            render_verification(row)

            col1, col2, col3 = st.columns(3)

            with col1:
                if st.button("Approve", key=f"ok_{row['id']}", type="primary"):
                    # if you changed the text, log the edit; else approve as-is
                    edit = edited if edited.strip() != row["post_text"].strip() else None
                    approve(row["id"], edited_text=edit)
                    st.rerun()

            with col2:
                if st.button("Approve + copy", key=f"copy_{row['id']}"):
                    edit = edited if edited.strip() != row["post_text"].strip() else None
                    approve(row["id"], edited_text=edit)
                    st.session_state["to_copy"] = edited
                    st.rerun()

            with col3:
                if st.button("Reject", key=f"no_{row['id']}"):
                    reject(row["id"])
                    st.rerun()

    # show the last approved text for manual posting to X
    if st.session_state.get("to_copy"):
        st.divider()
        st.markdown("**approved — copy this and paste to X:**")
        st.code(st.session_state["to_copy"], language=None)


def blocked_tab():
    rows = list_blocked()
    if not rows:
        st.info("Nothing blocked by the verifier.")
        return

    st.caption(f"{len(rows)} variant(s) blocked by the verifier — proof the trust layer works")
    for row in rows:
        with st.container(border=True):
            st.markdown(f"**{row['archetype']}** · variant `{row['variant_id']}`")
            st.text(row["post_text"])
            reasons = _load_claims(row.get("blocked_reasons"))
            for r in reasons:
                st.markdown(f"🚫 {r}")


st.title("ContentForge")
st.caption("Approval queue — nothing posts without your sign-off.")

tab1, tab2 = st.tabs(["Pending", "Blocked"])
with tab1:
    pending_tab()
with tab2:
    blocked_tab()