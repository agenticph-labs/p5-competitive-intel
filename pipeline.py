#!/usr/bin/env python3
"""
pipeline.py — Daily Competitive Intelligence Brief Pipeline.

Orchestrates the full workflow:
  1. COLLECT  — Gather competitor data from public sources (simulated via sample_data.py)
  2. ANALYZE  — Feature gaps, sentiment, hiring signals, pricing, composite scoring
  3. SYNTHESIZE — Generate a structured daily brief in Markdown
  4. REPORT   — Output to stdout + saved file

Usage:
    python pipeline.py                        # Run full pipeline
    python pipeline.py --stdout-only          # Print report, no file
    python pipeline.py --json                 # Output analysis as JSON
    python pipeline.py --watch                # Stub: continuous monitoring loop
"""

import sys
import json
import argparse
from datetime import datetime


def banner():
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║   InsightPulse — Daily Competitive Intelligence Brief      ║")
    print("║   Collect · Analyze · Synthesize · Report                  ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print()


def step(label: str):
    print(f"  ⏳ [{datetime.utcnow().strftime('%H:%M:%S')}] {label} ...")


def done(label: str):
    print(f"  ✅ [{datetime.utcnow().strftime('%H:%M:%S')}] {label}")
    print()


def run_pipeline(stdout_only: bool = False) -> dict:
    """Execute the full pipeline and return results."""

    # ── Step 1: Collect ──
    step("COLLECT: Gathering competitor data from sources")
    from collector import collect_all
    data = collect_all()
    done(f"COLLECT: {len(data['competitors'])} competitors, "
         f"{len(data['news'])} news items, {len(data['jobs'])} job postings")

    # ── Step 2: Analyze ──
    step("ANALYZE: Running feature gap, sentiment, hiring, pricing analyses")
    from analyzer import analyze_all
    analysis = analyze_all(data)
    scores = analysis["scores"]["scores"]
    gaps = analysis["feature_gaps"]["gaps_we_miss"]
    done(f"ANALYZE: {len(scores)} competitors scored, {len(gaps)} feature gaps identified")

    # ── Step 3: Synthesize ──
    step("SYNTHESIZE: Generating daily intelligence brief")
    from reporter import generate_brief
    brief = generate_brief(data, analysis)
    done(f"SYNTHESIZE: Brief assembled ({len(brief.splitlines())} lines)")

    # ── Step 4: Report ──
    step("REPORT: Outputting results")
    print()
    print(brief)
    print()

    if not stdout_only:
        date_str = datetime.utcnow().strftime("%Y-%m-%d")
        out_path = f"brief_{date_str}.md"
        with open(out_path, "w") as f:
            f.write(brief)
        done(f"REPORT: Saved to {out_path}")
    else:
        done("REPORT: Stdout only (--stdout-only)")

    return {"data": data, "analysis": analysis, "brief": brief}


def run_as_json():
    """Output analysis as JSON (useful for downstream tooling)."""
    from collector import collect_all
    from analyzer import analyze_all
    data = collect_all()
    analysis = analyze_all(data)
    output = {
        "pipeline": "insightpulse-daily-brief",
        "collected_at": data["collected_at"],
        "competitors": data["competitors"],
        "scores": analysis["scores"]["scores"],
        "feature_gaps": analysis["feature_gaps"]["gaps_we_miss"],
        "sentiment": analysis["sentiment"],
        "hiring": analysis["hiring"],
        "pricing": analysis["pricing"],
    }
    print(json.dumps(output, indent=2))


def main():
    parser = argparse.ArgumentParser(
        description="InsightPulse — Daily Competitive Intelligence Brief Pipeline"
    )
    parser.add_argument("--stdout-only", action="store_true",
                        help="Print report to stdout without saving a file")
    parser.add_argument("--json", action="store_true",
                        help="Output structured analysis as JSON (no report)")
    parser.add_argument("--watch", action="store_true",
                        help="(Stub) Run in continuous monitoring mode")
    args = parser.parse_args()

    if args.watch:
        print("⚠️  Watch mode not yet implemented. Run `python pipeline.py` for a single brief.")
        sys.exit(0)

    if args.json:
        run_as_json()
        return

    banner()
    result = run_pipeline(stdout_only=args.stdout_only)
    print()
    print("  ✅ Pipeline complete.")
    print(f"     Competitors analyzed: {len(result['analysis']['scores']['scores'])}")
    print(f"     Feature gaps found:   {len(result['analysis']['feature_gaps']['gaps_we_miss'])}")
    print(f"     News items tracked:   {len(result['data']['news'])}")
    print()


if __name__ == "__main__":
    main()
