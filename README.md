# 📋 Daily Competitive Intelligence Brief

**Portfolio Project 5** — An automated agentic workflow that monitors competitors and produces a daily intelligence brief.

[![Status: Live](https://img.shields.io/badge/status-live-22c55e.svg)](https://github.com/agenticph-labs/p5-competitive-intel)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## Overview

This project implements a complete **collect → analyze → synthesize → report** pipeline for competitive intelligence. It ingests structured competitor data (simulating API calls to NewsAPI, LinkedIn, Crunchbase, etc.), runs multi-dimensional analysis, and outputs a polished daily brief in Markdown.

### What it does

| Stage | Module | Description |
|-------|--------|-------------|
| **Collect** | `collector.py` | Gathers competitor profiles, news, job postings, feature matrices, and pricing tiers from simulated public sources |
| **Analyze** | `analyzer.py` | Runs 5 analysis engines: feature gaps, sentiment scoring, hiring signals, pricing comparison, composite competitive scoring |
| **Synthesize** | `reporter.py` | Assembles findings into a structured daily brief with executive summary, scorecards, positioning chart, and recommended actions |
| **Orchestrate** | `pipeline.py` | CLI entry point that chains all three stages and outputs the brief |

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     pipeline.py                          │
│         Orchestrates collect → analyze → report          │
└────┬────────────────┬──────────────────┬─────────────────┘
     │                │                  │
     ▼                ▼                  ▼
┌──────────┐   ┌──────────────┐   ┌──────────────┐
│collector │──▶│  analyzer    │──▶│  reporter    │
│.py       │   │  .py         │   │  .py         │
└────┬─────┘   └──────┬───────┘   └──────┬───────┘
     │                │                  │
     ▼                ▼                  ▼
┌──────────┐   ┌──────────────┐   ┌──────────────┐
│sample    │   │ Feature Gap  │   │ Markdown     │
│data.py   │   │ Sentiment    │   │ Brief        │
│          │   │ Hiring       │   │ (stdout +    │
│(3 comps  │   │ Pricing      │   │  .md file)   │
│ + us)    │   │ Scorecard    │   │              │
└──────────┘   └──────────────┘   └──────────────┘
```

### Key design decisions

- **Simulated data** (`sample_data.py`): Three realistic AI-analytics competitors (DataForge AI, QueryCraft, InsightGrid) plus our own product profile — each with 13 features, 3-4 pricing tiers, recent news, and job postings.
- **Modular collectors**: Each source (news, jobs, features, pricing, fundamentals) is an independent function — swap in real APIs without touching the rest.
- **Weighted scoring**: Composite scores use 5 weighted factors: feature breadth (30%), quality (25%), sentiment (15%), pricing accessibility (15%), scale (15%).
- **Actionable output**: Every brief ends with prioritized recommendations built from the data.

---

## Quick Start

```bash
# Clone
git clone https://github.com/agenticph-labs/p5-competitive-intel.git
cd p5-competitive-intel

# Run the pipeline (stdout + saved file)
python pipeline.py

# Print-only mode
python pipeline.py --stdout-only

# JSON output for downstream tooling
python pipeline.py --json

# Launch the Streamlit web dashboard
pip install -r requirements.txt
streamlit run streamlit_ui.py
```

No dependencies beyond the Python 3.13+ standard library.

---

## Sample Output (abridged)

### Executive Summary

```
🏁 Executive Summary

Top-ranked competitor:  DataForge AI (80.1/100)
Our score:              65.8/100
Biggest threat:         DataForge AI (80.1/100)

Key Takeaways:
  🔴 Gap: Missing "Custom ML model hosting" — offered by 1 competitor
  🚀 InsightGrid has 4 open roles — likely expanding product or GTM
  ⚠️ DataForge AI: 3 positive / 1 negative articles (security incident)
```

### Competitive Scorecard

| Competitor | Breadth | Quality | Sentiment | Pricing | Scale | **Composite** |
|------------|---------|---------|-----------|---------|-------|---------------|
| DataForge AI | 100.0 | 77.7 | 70.0 | 50.5 | 84.0 | **80.1** |
| QueryCraft | 84.6 | 65.5 | 60.0 | 85.0 | 27.0 | **67.5** |
| InsightPulse (Us) | 84.6 | 65.5 | 50.0 | 60.5 | 50.0 | **65.8** |
| InsightGrid | 76.9 | 57.0 | 60.0 | 85.5 | 12.4 | **61.0** |

### Pricing Comparison

| Competitor | Free Tier | Entry Price | Mid Price |
|------------|:---------:|------------:|----------:|
| InsightGrid | ❌ | $29/mo | $149/mo |
| QueryCraft | ✅ | $49/mo | $199/mo |
| InsightPulse (Us) | ❌ | $79/mo | $299/mo |
| DataForge AI | ❌ | $99/mo | $499/mo |

### Recommended Actions

1. **Prioritize "Custom ML model hosting"** — 1 of 2 tracked competitors offer it.
2. **Investigate "On-premise deployment"** — second most common gap.
3. **Improve Custom ML model hosting quality** — currently 0/10 vs competitor avg 7.0/10.
4. **Monitor free-tier threat** — QueryCraft's free tier pressures SMB acquisition costs.

---

## Extending the Pipeline

### Adding a real data source

Each collector in `collector.py` returns a flat list of dicts. Replace a simulated collector with an API call:

```python
def collect_news(competitors, days_back=90):
    """Production version using NewsAPI."""
    import requests
    api_key = os.environ["NEWSAPI_KEY"]
    all_articles = []
    for comp in competitors:
        resp = requests.get(
            "https://newsapi.org/v2/everything",
            params={"q": comp.name, "from": ..., "apiKey": api_key}
        )
        # map response to expected schema ...
    return all_articles
```

### Adding a new analysis module

1. Write a function in `analyzer.py` that takes the collected `data` dict.
2. Add it to `analyze_all()`.
3. Add a section function in `reporter.py` and call it from `generate_brief()`.

---

## File Reference

| File | Purpose |
|------|---------|
| `pipeline.py` | CLI orchestrator — entry point |
| `collector.py` | Data collection from sources |
| `analyzer.py` | Analysis engines (gaps, sentiment, hiring, pricing, scoring) |
| `reporter.py` | Markdown brief generation |
| `sample_data.py` | Simulated competitor data (3 competitors + us) |
| `brief_YYYY-MM-DD.md` | Generated daily brief |

---

## License

MIT — see `LICENSE`.

---

*Portfolio Project 5 — [AgenticPH Labs](https://agenticph-labs.github.io/portfolio)*
