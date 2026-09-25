"""
analyzer.py — Competitive analysis engine.

Takes collected data and produces structured analysis:
  - Positioning map (price vs. capability)
  - Feature gap analysis (what competitors have that we lack)
  - Sentiment trends across news
  - Hiring velocity / strategic signals
  - Pricing comparison (entry, mid, enterprise tiers)
  - Competitive advantage scoring
"""

from typing import Dict, Any, List, Tuple
from sample_data import get_our_product


# ──────────────────────────────────────────────
# Feature gap analysis
# ──────────────────────────────────────────────

def analyze_feature_gaps(data: Dict[str, Any]) -> Dict[str, Any]:
    """Identify features competitors offer that we lack, and vice versa.

    Returns:
        {
            "gaps_we_miss": [{"feature", "category", "competitors_offering", "best_quality", "notes"}, ...],
            "gaps_they_miss": [{"feature", "category"}, ...],
            "quality_advantages": [{"feature", "us_score", "avg_competitor_score", "margin"}, ...],
            "quality_disadvantages": [...]
        }
    """
    matrix = data["feature_matrix"]["matrix"]
    feature_stats = data["feature_matrix"]["feature_stats"]
    our_name = get_our_product().name

    us = matrix.get(our_name, {})
    competitors = {k: v for k, v in matrix.items() if k != our_name}

    gaps_we_miss: List[Dict] = []
    gaps_they_miss: List[Dict] = []

    # Gather all unique feature names
    all_features = list(us.keys())
    for fname in all_features:
        our_feat = us[fname]

        # Features we don't have
        if not our_feat["has_it"]:
            offering_comps = []
            best_quality = 0
            notes = ""
            for cname, cfeats in competitors.items():
                if fname in cfeats and cfeats[fname]["has_it"]:
                    offering_comps.append(cname)
                    qs = cfeats[fname]["quality_score"]
                    if qs > best_quality:
                        best_quality = qs
                        notes = cfeats[fname]["notes"]
            if offering_comps:
                gaps_we_miss.append({
                    "feature": fname,
                    "category": feature_stats.get(fname, {}).get("category", ""),
                    "competitors_offering": len(offering_comps),
                    "offering_competitors": offering_comps,
                    "best_quality_score": best_quality,
                    "notes": notes,
                })

        # Features we have that at least one competitor doesn't
        for cname, cfeats in competitors.items():
            if fname in cfeats and not cfeats[fname]["has_it"]:
                gaps_they_miss.append({
                    "feature": fname,
                    "category": feature_stats.get(fname, {}).get("category", ""),
                    "missing_at": cname,
                })

    # Quality score comparison
    quality_comparisons: List[Dict] = []
    for fname in all_features:
        our_score = us[fname]["quality_score"]
        comp_scores = []
        for cname, cfeats in competitors.items():
            if fname in cfeats and cfeats[fname]["has_it"]:
                comp_scores.append(cfeats[fname]["quality_score"])
        avg_comp = sum(comp_scores) / len(comp_scores) if comp_scores else 0
        margin = our_score - avg_comp
        if margin != 0:
            quality_comparisons.append({
                "feature": fname,
                "category": feature_stats.get(fname, {}).get("category", ""),
                "our_score": our_score,
                "avg_competitor_score": round(avg_comp, 1),
                "margin": round(margin, 1),
                "advantage": "us" if margin > 0 else "competitors",
            })

    quality_comparisons.sort(key=lambda x: abs(x["margin"]), reverse=True)
    advantages = [q for q in quality_comparisons if q["advantage"] == "us"]
    disadvantages = [q for q in quality_comparisons if q["advantage"] == "competitors"]

    # Remove duplicates from gaps_they_miss
    seen_gaps: set = set()
    unique_gaps_they_miss = []
    for g in gaps_they_miss:
        key = (g["feature"], g["missing_at"])
        if key not in seen_gaps:
            seen_gaps.add(key)
            unique_gaps_they_miss.append(g)

    gaps_we_miss.sort(key=lambda x: x["competitors_offering"], reverse=True)

    return {
        "gaps_we_miss": gaps_we_miss,
        "gaps_they_miss": unique_gaps_they_miss,
        "quality_advantages": advantages,
        "quality_disadvantages": disadvantages,
    }


# ──────────────────────────────────────────────
# Sentiment analysis
# ──────────────────────────────────────────────

def analyze_sentiment(data: Dict[str, Any]) -> Dict[str, Any]:
    """Aggregate news sentiment by competitor."""
    news = data["news"]
    by_competitor: Dict[str, Dict] = {}

    for item in news:
        comp = item["competitor"]
        by_competitor.setdefault(comp, {"positive": 0, "negative": 0, "neutral": 0, "total": 0, "items": []})
        sent = item["sentiment"]
        by_competitor[comp][sent] = by_competitor[comp].get(sent, 0) + 1
        by_competitor[comp]["total"] += 1
        by_competitor[comp]["items"].append(item)

    scored = []
    for comp, stats in by_competitor.items():
        score = stats["positive"] - stats["negative"]
        scored.append({
            "competitor": comp,
            "positive": stats["positive"],
            "negative": stats["negative"],
            "neutral": stats["neutral"],
            "total": stats["total"],
            "sentiment_score": score,
            "label": "strong" if score >= 2 else ("mixed" if score >= 0 else "concerning"),
            "items": stats["items"],
        })

    scored.sort(key=lambda x: x["sentiment_score"], reverse=True)
    return {
        "by_competitor": scored,
        "overall_positive": sum(s["positive"] for s in scored),
        "overall_negative": sum(s["negative"] for s in scored),
        "overall_neutral": sum(s["neutral"] for s in scored),
    }


# ──────────────────────────────────────────────
# Hiring signal analysis
# ──────────────────────────────────────────────

def analyze_hiring(data: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze job postings for strategic signals.

    Key signals: hiring velocity, new departments, remote ratio, seniority.
    """
    jobs = data["jobs"]
    by_competitor: Dict[str, List] = {}
    for job in jobs:
        by_competitor.setdefault(job["competitor"], []).append(job)

    results = []
    for comp, postings in by_competitor.items():
        depts = {}
        for j in postings:
            depts[j["department"]] = depts.get(j["department"], 0) + 1
        remote_count = sum(1 for j in postings if j["remote"])
        results.append({
            "competitor": comp,
            "total_openings": len(postings),
            "departments": depts,
            "remote_percent": round(remote_count / len(postings) * 100) if postings else 0,
            "signal": "aggressive hiring" if len(postings) >= 3 else "steady"
                        if len(postings) >= 1 else "quiet",
        })

    results.sort(key=lambda x: x["total_openings"], reverse=True)
    return {
        "by_competitor": results,
        "total_openings": len(jobs),
    }


# ──────────────────────────────────────────────
# Pricing comparison
# ──────────────────────────────────────────────

def analyze_pricing(data: Dict[str, Any]) -> Dict[str, Any]:
    """Compare entry-level and growth-tier pricing across competitors."""
    pricing = data["pricing"]

    # Find entry tier and mid tier for each competitor
    analysis = {}
    for p in pricing:
        comp = p["competitor"]
        analysis.setdefault(comp, {"entry": None, "mid": None, "has_free": False})
        if p["contract"] == "enterprise":
            continue
        if p["plan"].lower() == "free":
            analysis[comp]["has_free"] = True
        elif analysis[comp]["entry"] is None or p["price_monthly"] < analysis[comp]["entry"]["price_monthly"]:
            analysis[comp]["entry"] = p
        elif analysis[comp]["mid"] is None and p["price_monthly"] > 0:
            analysis[comp]["mid"] = p

    # Build comparable table
    rows = []
    for comp, info in analysis.items():
        entry = info["entry"]
        mid = info["mid"]
        rows.append({
            "competitor": comp,
            "has_free_tier": info["has_free"],
            "entry_price": entry["price_monthly"] if entry else None,
            "entry_plan": entry["plan"] if entry else "N/A",
            "entry_users": entry["users_included"] if entry else 0,
            "mid_price": mid["price_monthly"] if mid else "Only entry + enterprise",
            "mid_plan": mid["plan"] if mid else "N/A",
            "mid_users": mid["users_included"] if mid else 0,
        })

    rows.sort(key=lambda r: r["entry_price"] if r["entry_price"] is not None else 9999)
    return {"tiers": rows}


# ──────────────────────────────────────────────
# Overall competitive scoring
# ──────────────────────────────────────────────

def compute_scores(data: Dict[str, Any]) -> Dict[str, Any]:
    """Compute a composite competitive score for each competitor.

    Factors (weight):
      - Feature breadth (30%)
      - Feature quality (25%)
      - Sentiment (15%)
      - Pricing accessibility (15%)
      - Funding / scale (15%)
    """
    matrix = data["feature_matrix"]["matrix"]
    feature_stats = data["feature_matrix"]["feature_stats"]
    sentiment = analyze_sentiment(data)
    pricing = analyze_pricing(data)
    fundamentals = {f["name"]: f for f in data["fundamentals"]}

    total_features = len(feature_stats)
    scores = []

    for comp_name, feats in matrix.items():
        # --- Feature breadth (0-100) ---
        offered = sum(1 for f in feats.values() if f["has_it"])
        breadth = (offered / total_features) * 100

        # --- Feature quality (0-100) ---
        quality_scores = [f["quality_score"] for f in feats.values() if f["has_it"]]
        avg_quality = (sum(quality_scores) / len(quality_scores) * 10) if quality_scores else 0

        # --- Sentiment (0-100) ---
        sent_data = next((s for s in sentiment["by_competitor"] if s["competitor"] == comp_name), None)
        if sent_data:
            sent_norm = max(0, min(100, 50 + sent_data["sentiment_score"] * 10))
        else:
            sent_norm = 50

        # --- Pricing (0-100) ---
        price_data = next((r for r in pricing["tiers"] if r["competitor"] == comp_name), None)
        if price_data and price_data["entry_price"] is not None:
            # Lower entry price = higher score (inverse linear capped at $200)
            price_score = max(0, 100 - (price_data["entry_price"] / 200) * 100)
            if price_data["has_free_tier"]:
                price_score = max(price_score, 85)
        else:
            price_score = 50

        # --- Scale (0-100) ---
        fund_data = fundamentals.get(comp_name)
        if fund_data:
            emp = fund_data["employees_estimate"]
            funding = fund_data["funding_total_m"]
            scale_emp = min(100, emp / 5)           # 500+ = 100
            scale_funding = min(100, funding * 2)   # $50M+ = 100
            scale_score = (scale_emp + scale_funding) / 2
        else:
            scale_score = 50

        composite = (
            breadth * 0.30
            + avg_quality * 0.25
            + sent_norm * 0.15
            + price_score * 0.15
            + scale_score * 0.15
        )

        scores.append({
            "competitor": comp_name,
            "feature_breadth": round(breadth, 1),
            "feature_quality": round(avg_quality, 1),
            "sentiment": round(sent_norm, 1),
            "pricing_accessibility": round(price_score, 1),
            "scale_funding": round(scale_score, 1),
            "composite_score": round(composite, 1),
        })

    scores.sort(key=lambda x: x["composite_score"], reverse=True)
    return {"scores": scores}


# ──────────────────────────────────────────────
# Run all analyses
# ──────────────────────────────────────────────

def analyze_all(data: Dict[str, Any]) -> Dict[str, Any]:
    """Execute all analysis modules and return combined results."""
    return {
        "feature_gaps": analyze_feature_gaps(data),
        "sentiment": analyze_sentiment(data),
        "hiring": analyze_hiring(data),
        "pricing": analyze_pricing(data),
        "scores": compute_scores(data),
    }


if __name__ == "__main__":
    from collector import collect_all
    from pprint import pprint

    raw = collect_all()
    analysis = analyze_all(raw)

    print("=== COMPETITIVE SCORES ===")
    for s in analysis["scores"]["scores"]:
        print(f"  {s['competitor']:30s}  {s['composite_score']:5.1f}")

    print("\n=== FEATURE GAPS (We Miss) ===")
    for g in analysis["feature_gaps"]["gaps_we_miss"][:5]:
        print(f"  {g['feature']:40s}  offered by {g['competitors_offering']} competitor(s)")

    print("\n=== SENTIMENT ===")
    for s in analysis["sentiment"]["by_competitor"]:
        print(f"  {s['competitor']:30s}  {s['sentiment_score']:+d}  ({s['label']})")

    print("\n=== HIRING SIGNALS ===")
    for h in analysis["hiring"]["by_competitor"]:
        print(f"  {h['competitor']:30s}  {h['total_openings']} openings  ({h['signal']})")
