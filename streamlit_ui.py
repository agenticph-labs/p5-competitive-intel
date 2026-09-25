#!/usr/bin/env python3
"""streamlit_ui.py — Web dashboard for the Competitive Intelligence Pipeline.

Usage:
    streamlit run streamlit_ui.py
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict

import streamlit as st

from collector import collect_all
from analyzer import analyze_all
from reporter import (
    generate_brief,
    _executive_summary,
    _score_summary,
    _feature_gap_section,
    _news_section,
    _hiring_section,
    _pricing_section,
    _recommendations,
    _positioning_chart,
)

st.set_page_config(
    page_title="InsightPulse — Competitive Intel",
    page_icon="📡",
    layout="wide",
)

# ── Session state ──────────────────────────────────────────────────────

if "brief_data" not in st.session_state:
    st.session_state.brief_data = None
if "brief_text" not in st.session_state:
    st.session_state.brief_text = None
if "collected_at" not in st.session_state:
    st.session_state.collected_at = None
if "competitors" not in st.session_state:
    st.session_state.competitors = []
if "gap_count" not in st.session_state:
    st.session_state.gap_count = 0
if "news_count" not in st.session_state:
    st.session_state.news_count = 0
if "job_count" not in st.session_state:
    st.session_state.job_count = 0
if "running" not in st.session_state:
    st.session_state.running = False


# ── Pipeline runner ────────────────────────────────────────────────────


def run_pipeline() -> Dict[str, Any]:
    """Execute collect → analyze → synthesize and return results."""
    data = collect_all()
    analysis = analyze_all(data)
    brief = generate_brief(data, analysis)

    st.session_state.collected_at = data["collected_at"]
    st.session_state.competitors = data["competitors"]
    st.session_state.news_count = len(data["news"])
    st.session_state.job_count = len(data["jobs"])
    st.session_state.gap_count = len(analysis["feature_gaps"]["gaps_we_miss"])
    st.session_state.brief_data = {"data": data, "analysis": analysis}
    st.session_state.brief_text = brief
    return st.session_state.brief_data


# ── UI ─────────────────────────────────────────────────────────────────

st.title("📡 InsightPulse — Competitive Intelligence Dashboard")
st.markdown("**Collect · Analyze · Synthesize · Report**")

# ── Sidebar ────────────────────────────────────────────────────────────

with st.sidebar:
    st.header("Controls")
    if st.button("🔄 Run New Analysis", type="primary", use_container_width=True):
        st.session_state.running = True
        with st.spinner("Running full pipeline..."):
            run_pipeline()
        st.session_state.running = False
        st.rerun()

    st.divider()
    st.subheader("About")
    st.markdown(
        "This dashboard runs the **InsightPulse** competitive intelligence "
        "pipeline. Data is simulated via `sample_data.py` — swap collectors "
        "for real API sources in production."
    )

    if st.session_state.brief_text:
        st.download_button(
            label="📥 Download Latest Brief (.md)",
            data=st.session_state.brief_text,
            file_name=f"brief_{datetime.utcnow().strftime('%Y-%m-%d')}.md",
            mime="text/markdown",
            use_container_width=True,
        )

# ── Run on first load if no data ───────────────────────────────────────

if st.session_state.brief_data is None and not st.session_state.running:
    with st.spinner("Running initial pipeline..."):
        run_pipeline()
    st.rerun()

# ── Dashboard content ──────────────────────────────────────────────────

bd = st.session_state.brief_data

if bd is None:
    st.info("Click **Run New Analysis** in the sidebar to generate a brief.")
    st.stop()

data: Dict[str, Any] = bd["data"]
analysis: Dict[str, Any] = bd["analysis"]
brief_text: str = st.session_state.brief_text

# ── KPI row ────────────────────────────────────────────────────────────

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
with kpi1:
    st.metric("Competitors Tracked", len(st.session_state.competitors))
with kpi2:
    st.metric("Feature Gaps", st.session_state.gap_count)
with kpi3:
    st.metric("News Items", st.session_state.news_count)
with kpi4:
    st.metric("Job Postings", st.session_state.job_count)

st.caption(f"Last collected: {st.session_state.collected_at}")
st.divider()

# ── Tabbed view of the brief sections ──────────────────────────────────

tabs = st.tabs([
    "🏁 Executive Summary",
    "📊 Scorecard",
    "🔍 Feature Gaps",
    "💰 Pricing",
    "📰 News",
    "💼 Hiring",
    "🎯 Recommendations",
    "📄 Full Brief",
])

with tabs[0]:
    st.markdown(_executive_summary(data, analysis))
    st.markdown("")
    st.markdown(_positioning_chart(analysis["scores"]))

with tabs[1]:
    st.markdown(_score_summary(analysis))

with tabs[2]:
    st.markdown(_feature_gap_section(analysis))

with tabs[3]:
    st.markdown(_pricing_section(analysis))

with tabs[4]:
    st.markdown(_news_section(analysis))

with tabs[5]:
    st.markdown(_hiring_section(analysis))

with tabs[6]:
    st.markdown(_recommendations(analysis))

with tabs[7]:
    st.markdown(brief_text)
