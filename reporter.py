"""
reporter.py — Daily competitive intelligence brief generator.

Transforms collected + analyzed data into a polished markdown report.
Outputs both to stdout and to a dated file.
"""

from datetime import datetime
from typing import Dict, Any, List
from analyzer import analyze_all
from collector import collect_all


# ──────────────────────────────────────────────
# Formatting helpers
# ──────────────────────────────────────────────

def _sentiment_emoji(score: int) -> str:
    if score >= 2:
        return "🟢"
    elif score >= 0:
        return "🟡"
    return "🔴"


def _score_bar(score: float, width: int = 20) -> str:
    """Render a simple ASCII bar chart."""
    filled = int((score / 100) * width)
    return "█" * filled + "░" * (width - filled)


def _positioning_chart(scores: Dict[str, Any]) -> str:
    """Render a simple price-vs-features scatter grid."""
    rows = scores["scores"]
    # Build a primitive grid: features on X, price on Y
    lines = ["```", "Positions (Feature Breadth × Pricing Accessibility)", ""]
    lines.append(f"{'Competitor':30s} {'Breadth':>8s}  {'Price $':>8s}  {'Chart':>22s}")
    lines.append("-" * 70)
    for r in rows:
        name = r["competitor"][:28]
        chart = _score_bar(r["feature_breadth"], 20)
        lines.append(f"{name:30s} {r['feature_breadth']:>7.1f}%  {r['pricing_accessibility']:>7.1f}%  {chart}")
    lines.append("```")
    return "\n".join(lines)


# ──────────────────────────────────────────────
# Section builders
# ──────────────────────────────────────────────

def _executive_summary(data: Dict[str, Any], analysis: Dict[str, Any]) -> str:
    scores = analysis["scores"]["scores"]
    news = data["news"]
    gaps = analysis["feature_gaps"]["gaps_we_miss"]

    top = max(scores, key=lambda s: s["composite_score"])
    our = next(s for s in scores if "(Us)" in s["competitor"])
    top_threat = max((s for s in scores if "(Us)" not in s["competitor"]), key=lambda s: s["composite_score"])

    lines = [
        "## 🏁 Executive Summary",
        "",
        f"**Report generated:** {data['collected_at']}",
        f"**Competitors tracked:** {', '.join(c for c in data['competitors'])}",
        "",
        f"**Top-ranked competitor:** {top['competitor']} ({top['composite_score']}/100)",
        f"**Our score:** {our['composite_score']}/100",
        f"**Biggest competitive threat:** {top_threat['competitor']} ({top_threat['composite_score']}/100)",
        "",
        f"**News volume:** {len(news)} items in the tracking window.",
        f"**Critical gaps to address:** {len(gaps)} features competitors have that we lack.",
        "",
        "### Key Takeaways",
    ]

    # Generate takeaways
    takeaways = []

    # Takeaway: top gap
    if gaps:
        top_gap = gaps[0]
        takeaways.append(
            f"- **🔴 Gap:** Missing \"{top_gap['feature']}\" ({top_gap['category']}) — "
            f"offered by {top_gap['competitors_offering']} competitor(s). "
            f"{top_gap['notes']}"
        )

    # Takeaway: sentiment risk
    sent = analysis["sentiment"]
    neg_comps = [s for s in sent["by_competitor"] if s["sentiment_score"] < 0]
    if neg_comps:
        for nc in neg_comps:
            takeaways.append(
                f"- **⚠️ Sentiment risk:** {nc['competitor']} has "
                f"{nc['negative']} negative / {nc['positive']} positive articles "
                f"(score: {nc['sentiment_score']:+d})."
            )

    # Takeaway: hiring signal
    hiring = analysis["hiring"]
    aggro = [h for h in hiring["by_competitor"] if h["signal"] == "aggressive hiring"]
    if aggro:
        for a in aggro:
            takeaways.append(
                f"- **🚀 Aggressive hiring:** {a['competitor']} has {a['total_openings']} open roles "
                f"({a['remote_percent']}% remote) — likely expanding product or GTM."
            )

    if not takeaways:
        takeaways.append("- No significant changes detected this cycle.")

    lines.extend(takeaways)
    lines.append("")
    return "\n".join(lines)


def _score_summary(analysis: Dict[str, Any]) -> str:
    scores = analysis["scores"]["scores"]
    lines = [
        "## 📊 Competitive Scorecard",
        "",
        "Composite scores (0-100) weighted across feature breadth, quality, sentiment, pricing, and scale.",
        "",
        "| Competitor | Breadth | Quality | Sentiment | Pricing | Scale | **Composite** |",
        "|------------|---------|---------|-----------|---------|-------|---------------|",
    ]
    for s in scores:
        lines.append(
            f"| {s['competitor']:30s} | {s['feature_breadth']:>5.1f} | "
            f"{s['feature_quality']:>5.1f} | {s['sentiment']:>5.1f} | "
            f"{s['pricing_accessibility']:>5.1f} | {s['scale_funding']:>5.1f} | "
            f"**{s['composite_score']:>5.1f}** |"
        )
    lines.append("")
    return "\n".join(lines)


def _feature_gap_section(analysis: Dict[str, Any]) -> str:
    gaps = analysis["feature_gaps"]["gaps_we_miss"]
    disadv = analysis["feature_gaps"]["quality_disadvantages"]
    advantages = analysis["feature_gaps"]["quality_advantages"]

    lines = ["## 🔍 Feature Gap Analysis", ""]

    if gaps:
        lines.append("### Features We're Missing (Competitors Have Them)")
        lines.append("")
        lines.append("| Feature | Category | Competitors Offering | Best Quality | Notes |")
        lines.append("|---------|----------|--------------------:|-------------:|-------|")
        for g in gaps[:10]:
            comps = ", ".join(g["offering_competitors"])
            lines.append(f"| {g['feature']} | {g['category']} | {g['competitors_offering']} | {g['best_quality_score']}/10 | {g['notes']} |")
        lines.append("")
    else:
        lines.append("_No feature gaps detected — we match or exceed competitors on all tracked features._")
        lines.append("")

    if disadv:
        lines.append("### Quality Disadvantages (Competitors Score Higher)")
        lines.append("")
        lines.append("| Feature | Our Score | Avg Competitor | Gap |")
        lines.append("|---------|----------:|---------------:|----:|")
        for d in disadv[:5]:
            lines.append(f"| {d['feature']} | {d['our_score']}/10 | {d['avg_competitor_score']}/10 | -{abs(d['margin'])} |")
        lines.append("")

    if advantages:
        lines.append("### Quality Advantages (We Score Higher)")
        lines.append("")
        lines.append("| Feature | Our Score | Avg Competitor | Margin |")
        lines.append("|---------|----------:|---------------:|------:|")
        for a in advantages[:5]:
            lines.append(f"| {a['feature']} | {a['our_score']}/10 | {a['avg_competitor_score']}/10 | +{a['margin']} |")
        lines.append("")

    return "\n".join(lines)


def _news_section(analysis: Dict[str, Any]) -> str:
    sent = analysis["sentiment"]
    lines = [
        "## 📰 Media & Press Sentiment",
        "",
        f"Overall: {sent['overall_positive']} positive, {sent['overall_negative']} negative, "
        f"{sent['overall_neutral']} neutral articles.",
        "",
        "| Competitor | 👍 Positive | 👎 Negative | ➖ Neutral | Score | Label |",
        "|------------|-----------:|-----------:|----------:|-----:|-------|",
    ]
    for s in sent["by_competitor"]:
        emoji = _sentiment_emoji(s["sentiment_score"])
        lines.append(
            f"| {emoji} {s['competitor']:28s} | {s['positive']} | {s['negative']} | "
            f"{s['neutral']} | {s['sentiment_score']:+d} | {s['label']} |"
        )
    lines.append("")

    # Top stories
    lines.append("### Top Stories by Competitor")
    lines.append("")
    for s in sent["by_competitor"]:
        if s["items"]:
            lines.append(f"**{s['competitor']}**")
            for item in s["items"][:3]:
                emoji = "🟢" if item["sentiment"] == "positive" else ("🔴" if item["sentiment"] == "negative" else "🟡")
                lines.append(f"- {emoji} **{item['headline']}** — _{item['source']} ({item['date']})_")
                lines.append(f"  {item['summary']}")
            lines.append("")

    return "\n".join(lines)


def _hiring_section(analysis: Dict[str, Any]) -> str:
    hiring = analysis["hiring"]
    lines = [
        "## 💼 Hiring Signals",
        "",
        f"**Total open positions tracked:** {hiring['total_openings']}",
        "",
        "| Competitor | Openings | Departments | Remote % | Signal |",
        "|------------|---------:|-------------|---------:|--------|",
    ]
    for h in hiring["by_competitor"]:
        dept_str = ", ".join(f"{d} ({c})" for d, c in h["departments"].items())
        signal_emoji = {"aggressive hiring": "🔴", "steady": "🟡", "quiet": "🟢"}.get(h["signal"], "⚪")
        lines.append(
            f"| {h['competitor']:30s} | {h['total_openings']} | {dept_str} | "
            f"{h['remote_percent']}% | {signal_emoji} {h['signal']} |"
        )
    lines.append("")
    return "\n".join(lines)


def _pricing_section(analysis: Dict[str, Any]) -> str:
    pricing = analysis["pricing"]["tiers"]
    lines = [
        "## 💰 Pricing Comparison",
        "",
        "| Competitor | Free Tier | Entry Price | Entry Users | Mid Price | Mid Users |",
        "|------------|:---------:|-----------:|:-----------:|----------:|:---------:|",
    ]
    for p in pricing:
        free = "✅" if p["has_free_tier"] else "❌"
        entry_price = f"${p['entry_price']:.0f}/mo" if p["entry_price"] else "Enterprise"
        mid_price = f"${p['mid_price']:.0f}/mo" if isinstance(p["mid_price"], (int, float)) else str(p["mid_price"])
        lines.append(
            f"| {p['competitor']:30s} | {free} | {entry_price:>10s} | {p['entry_users']:>3d} | "
            f"{mid_price:>10s} | {p['mid_users']:>3d} |"
        )
    lines.append("")
    return "\n".join(lines)


def _recommendations(analysis: Dict[str, Any]) -> str:
    gaps = analysis["feature_gaps"]["gaps_we_miss"]
    disadv = analysis["feature_gaps"]["quality_disadvantages"]

    lines = ["## 🎯 Recommended Actions", ""]
    actions = []

    # Prioritize by feature gap
    if gaps:
        top_gap = gaps[0]
        actions.append(
            f"1. **Prioritize \"{top_gap['feature']}\"** — {top_gap['competitors_offering']} of "
            f"{len(gaps)} tracked competitors offer it. Category: {top_gap['category']}. "
            f"Best-in-class quality: {top_gap['best_quality_score']}/10."
        )
    if len(gaps) > 1:
        actions.append(
            f"2. **Investigate \"{gaps[1]['feature']}\"** — second most common gap, "
            f"offered by {gaps[1]['competitors_offering']} competitor(s)."
        )

    # Quality improvements
    if disadv:
        for i, d in enumerate(disadv[:2]):
            actions.append(
                f"{len(actions)+1}. **Improve {d['feature']} quality** — currently {d['our_score']}/10 "
                f"vs competitor average {d['avg_competitor_score']}/10."
            )

    # Pricing threat
    pricing = analysis["pricing"]["tiers"]
    free_tiers = [p for p in pricing if p["has_free_tier"] and "(Us)" not in p["competitor"]]
    if free_tiers:
        names = ", ".join(p["competitor"] for p in free_tiers)
        actions.append(
            f"{len(actions)+1}. **Monitor free-tier threat** — {names} offer free tiers, "
            f"which may pressure SMB acquisition costs."
        )

    # Sentiment watch
    sent = analysis["sentiment"]
    neg = [s for s in sent["by_competitor"] if s["sentiment_score"] < -1]
    if neg:
        for n in neg:
            actions.append(
                f"{len(actions)+1}. **Watch {n['competitor']}** — recent negative press "
                f"(score: {n['sentiment_score']:+d}) may signal vulnerability we can exploit "
                f"in competitive deals."
            )

    if not actions:
        actions.append("No urgent actions identified this cycle.")

    lines.extend(actions)
    lines.append("")
    return "\n".join(lines)


# ──────────────────────────────────────────────
# Full report builder
# ──────────────────────────────────────────────

def generate_brief(data: Dict[str, Any], analysis: Dict[str, Any]) -> str:
    """Assemble the full daily competitive intelligence brief in Markdown."""
    today = datetime.utcnow().strftime("%Y-%m-%d")

    sections = [
        f"# 📋 Daily Competitive Intelligence Brief — {today}",
        "",
        _executive_summary(data, analysis),
        _positioning_chart(analysis["scores"]),
        _score_summary(analysis),
        _feature_gap_section(analysis),
        _pricing_section(analysis),
        _news_section(analysis),
        _hiring_section(analysis),
        _recommendations(analysis),
        "---",
        f"_Generated by InsightPulse Competitive Intelligence Pipeline · {data['collected_at']}_",
        "",
    ]

    return "\n".join(sections)


# ──────────────────────────────────────────────
# Entry point
# ──────────────────────────────────────────────

def run_pipeline() -> Dict[str, str]:
    """Run the full pipeline: collect → analyze → report.

    Returns:
        {"brief": markdown string, "path": file path, "collected_at": iso timestamp}
    """
    data = collect_all()
    analysis = analyze_all(data)
    brief = generate_brief(data, analysis)

    # Write to file
    date_str = datetime.utcnow().strftime("%Y-%m-%d")
    out_path = f"brief_{date_str}.md"
    with open(out_path, "w") as f:
        f.write(brief)

    return {"brief": brief, "path": out_path, "collected_at": data["collected_at"]}


if __name__ == "__main__":
    result = run_pipeline()
    print(f"✅ Brief generated: {result['path']}")
    print(f"   Collected at: {result['collected_at']}")
    print()
    # Print a truncated preview
    lines = result["brief"].split("\n")
    preview = "\n".join(lines[:25])
    print(preview)
    print(f"\n... ({len(lines)} total lines)")
