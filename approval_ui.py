"""

The approval queue, rebuilt to match the landing page and to be clear instead
of dense. One run at a time; its variants read as alternatives you choose
between; verification is skimmable; one obvious action per variant.

Run:  streamlit run approval_ui.py
"""

import json
from collections import defaultdict

import streamlit as st

from storage.db import approve, list_blocked, list_pending, reject


st.set_page_config(page_title="ContentForge · Approval", layout="centered")

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600&family=IBM+Plex+Mono:wght@400;500&family=Inter:wght@400;500;600&display=swap');
  :root{
    --ink:#14181f; --paper:#f6f4ee; --slate:#5b6672; --line:#d9d5c9;
    --verified:#2f7d57; --blocked:#c0392b; --amber:#b5892b; --card:#fffdf8;
  }
  .stApp{ background:var(--paper); }
   
  header[data-testid="stHeader"]{ display:none; }
  .block-container{ max-width:760px; padding-top:3.5rem; }
  h1,h2,h3{ font-family:'Fraunces',serif !important; color:var(--ink) !important; letter-spacing:-.01em; }
  .cf-title{ font-family:'Fraunces',serif; font-weight:600; font-size:30px; color:var(--ink); }
  .cf-title span{ color:var(--verified); }
  .cf-sub{ font-family:'IBM Plex Mono',monospace; font-size:12px; letter-spacing:.12em;
           text-transform:uppercase; color:var(--slate); margin-bottom:6px; }
  .run-head{ font-family:'IBM Plex Mono',monospace; font-size:12.5px; color:var(--slate);
             margin:26px 0 4px; padding-bottom:8px; border-bottom:1px solid var(--line); }
  .run-head b{ color:var(--ink); }
  .pill{ display:inline-flex; align-items:center; gap:6px; font-family:'IBM Plex Mono',monospace;
         font-size:11px; font-weight:500; letter-spacing:.05em; padding:3px 9px; border-radius:2px; }
  .p-ok{ color:var(--verified); background:rgba(47,125,87,.10); }
  .p-skip{ color:var(--amber); background:rgba(181,137,43,.10); }
  .p-no{ color:var(--blocked); background:rgba(192,57,43,.10); }
  .claimline{ font-family:'IBM Plex Mono',monospace; font-size:12.5px; color:var(--slate);
              line-height:1.5; margin:3px 0; }
  .ev{ padding-left:12px; border-left:2px solid var(--line); color:var(--slate); font-size:12px; }
  .stButton>button{ font-family:'Inter',sans-serif !important; font-weight:600;
                    border-radius:2px; border:1.5px solid var(--ink); }
  div[data-testid="stTextArea"] textarea{
    font-family:'Inter',sans-serif; font-size:15px; background:#fff; border:1px solid var(--line); }
  .empty{ text-align:center; padding:60px 20px; color:var(--slate);
          font-family:'Fraunces',serif; font-size:20px; }
  .copybox{ background:var(--ink); color:var(--paper); font-family:'IBM Plex Mono',monospace;
            font-size:13px; padding:14px 16px; border-radius:3px; line-height:1.5; white-space:pre-wrap; }
</style>
""", unsafe_allow_html=True)


def _load(raw):
    if not raw:
        return []
    if isinstance(raw, list):
        return raw
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return []


def verdict_pill(status):
    if status == "SKIPPED":
        return '<span class="pill p-skip">◇ OWN WORK · no external check</span>'
    if status == "BLOCKED":
        return '<span class="pill p-no">✕ BLOCKED</span>'
    return '<span class="pill p-ok">✓ VERIFIED</span>'


def render_verification(row):
    status = row.get("verify_status")
    claims = _load(row.get("claims"))
    st.markdown(verdict_pill(status), unsafe_allow_html=True)

    if status == "SKIPPED":
        st.markdown('<div class="claimline">Your own work — you\'re the source of truth, '
                    'so no external fact-check runs. Just give it a read.</div>', unsafe_allow_html=True)
        return
    if not claims:
        st.markdown('<div class="claimline">No factual claims to verify.</div>', unsafe_allow_html=True)
        return
    for c in claims:
        v = c.get("verdict", "?")
        icon = "✓" if v == "SUPPORTED" else "✕"
        st.markdown(f'<div class="claimline"><b>{icon} {v}</b> — {c.get("claim_text","")}</div>',
                    unsafe_allow_html=True)
        ev = c.get("evidence_text", "")
        if ev:
            st.markdown(f'<div class="claimline ev">{ev[:200]}</div>', unsafe_allow_html=True)


def pending_tab():
    rows = list_pending()
    if not rows:
        st.markdown('<div class="empty">Queue\'s clear. Nothing waiting.<br>'
                    'Run the pipeline to generate drafts.</div>', unsafe_allow_html=True)
        return

    runs = defaultdict(list)
    for r in rows:
        runs[r["run_id"]].append(r)

    st.caption(f"{len(rows)} draft(s) across {len(runs)} run(s) · pick one variant per run, edit if needed, approve")

    for run_id, variants in runs.items():
        v0 = variants[0]
        st.markdown(f'<div class="run-head"><b>{v0["archetype"]}</b> · '
                    f'{v0["source_type"]} · <a href="{v0["source_url"]}" target="_blank">source</a> · '
                    f'run {run_id}</div>', unsafe_allow_html=True)

        for row in variants:
            with st.container(border=True):
                st.markdown(f"**Variant {row['variant_id']}**")
                render_verification(row)
                edited = st.text_area(
                    "post text",
                    value=row["post_text"],
                    key=f"t_{row['id']}",
                    height=100,
                    label_visibility="collapsed",
                )
                c1, c2 = st.columns([1, 1])
                with c1:
                    if st.button("Approve + copy", key=f"ok_{row['id']}",
                                 type="primary", use_container_width=True):
                        edit = edited if edited.strip() != row["post_text"].strip() else None
                        approve(row["id"], edited_text=edit)
                        st.session_state["copied"] = edited
                        st.rerun()
                with c2:
                    if st.button("Reject", key=f"no_{row['id']}", use_container_width=True):
                        reject(row["id"])
                        st.rerun()

    if st.session_state.get("copied"):
        st.divider()
        st.markdown("**Approved — copy this, paste to X:**")
        st.markdown(f'<div class="copybox">{st.session_state["copied"]}</div>', unsafe_allow_html=True)


def blocked_tab():
    rows = list_blocked()
    if not rows:
        st.markdown('<div class="empty">Nothing blocked.</div>', unsafe_allow_html=True)
        return
    st.caption(f"{len(rows)} variant(s) the verifier stopped — the system catching itself")
    for row in rows:
        with st.container(border=True):
            st.markdown(f"**{row['archetype']}** · variant {row['variant_id']}")
            st.markdown('<span class="pill p-no">✕ BLOCKED</span>', unsafe_allow_html=True)
            st.markdown(f'<div class="claimline">{row["post_text"]}</div>', unsafe_allow_html=True)
            for r in _load(row.get("blocked_reasons")):
                st.markdown(f'<div class="claimline ev">{r}</div>', unsafe_allow_html=True)


st.markdown('<div class="cf-title">Content<span>Forge</span> · approvals</div>', unsafe_allow_html=True)
st.caption("Human in the loop — nothing posts without your sign-off")
st.write("")

tab1, tab2 = st.tabs(["Pending", "Blocked"])
with tab1:
    pending_tab()
with tab2:
    blocked_tab()