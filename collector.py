"""
collector.py — Data collection layer.

Simulates gathering competitive intelligence from multiple public sources:
  - News / press mentions (via simulated RSS/API)
  - Job postings (via simulated LinkedIn/company career pages)
  - Feature/price updates (via simulated product pages)
  - Social / community signals (via simulated Reddit, Hacker News, X)

Each collector function returns structured dicts. In production these
would hit real APIs (NewsAPI, Greenhouse, Crunchbase, etc.).
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any
from sample_data import get_all_competitors, get_our_product, Competitor


# ──────────────────────────────────────────────
# Collector: News
# ──────────────────────────────────────────────

def collect_news(competitors: List[Competitor],
                 days_back: int = 90) -> List[Dict[str, Any]]:
    """Return recent news items from each competitor's news feed.

    In production this would call NewsAPI, GDELT, or similar.
    """
    collected: List[Dict[str, Any]] = []
    for comp in competitors:
        for item in comp.recent_news:
            collected.append({
                "competitor": comp.name,
                "headline": item.headline,
                "source": item.source,
                "date": item.date,
                "sentiment": item.sentiment,
                "summary": item.summary,
            })
    # Sort by date descending
    collected.sort(key=lambda x: x["date"], reverse=True)
    return collected


# ──────────────────────────────────────────────
# Collector: Job Postings
# ──────────────────────────────────────────────

def collect_jobs(competitors: List[Competitor]) -> List[Dict[str, Any]]:
    """Return recent job postings.

    In production this would scrape career pages or call Greenhouse/Lever APIs.
    """
    collected: List[Dict[str, Any]] = []
    for comp in competitors:
        for job in comp.job_postings:
            collected.append({
                "competitor": comp.name,
                "title": job.title,
                "department": job.department,
                "posted": job.posted,
                "remote": job.remote,
            })
    collected.sort(key=lambda x: x["posted"], reverse=True)
    return collected


# ──────────────────────────────────────────────
# Collector: Feature / Pricing Matrix
# ──────────────────────────────────────────────

def collect_feature_matrix(competitors: List[Competitor]) -> Dict[str, Any]:
    """Build a structured feature-by-competitor matrix.

    Returns:
        {
            "features": [feature_name, ...],
            "categories": {category_name: [feature_name, ...]},
            "matrix": {
                competitor_name: {
                    feature_name: {"has_it": bool, "quality_score": int, "notes": str}
                }
            }
        }
    """
    all_features: Dict[str, Dict] = {}
    categories: Dict[str, List[str]] = {}

    for comp in competitors:
        for feat in comp.features:
            all_features.setdefault(feat.name, {
                "category": feat.category,
                "competitors_offering": 0,
            })
            categories.setdefault(feat.category, [])
            if feat.name not in categories[feat.category]:
                categories[feat.category].append(feat.name)

    # Count how many competitors offer each feature
    for comp in competitors:
        offered = {f.name for f in comp.features if f.has_it}
        for fname in all_features:
            if fname in offered:
                all_features[fname]["competitors_offering"] += 1

    # Build matrix
    matrix: Dict[str, Dict] = {}
    for comp in competitors:
        comp_row = {}
        for feat in comp.features:
            comp_row[feat.name] = {
                "has_it": feat.has_it,
                "quality_score": feat.quality_score,
                "notes": feat.notes,
            }
        matrix[comp.name] = comp_row

    return {
        "features": list(all_features.keys()),
        "categories": categories,
        "feature_stats": all_features,
        "matrix": matrix,
    }


# ──────────────────────────────────────────────
# Collector: Pricing
# ──────────────────────────────────────────────

def collect_pricing(competitors: List[Competitor]) -> List[Dict[str, Any]]:
    """Return pricing tier data for each competitor."""
    collected: List[Dict[str, Any]] = []
    for comp in competitors:
        for tier in comp.pricing:
            collected.append({
                "competitor": comp.name,
                "plan": tier.name,
                "price_monthly": tier.price_monthly,
                "users_included": tier.users_included,
                "key_limits": tier.key_limits,
                "contract": tier.contract,
            })
    return collected


# ──────────────────────────────────────────────
# Collector: Company fundamentals
# ──────────────────────────────────────────────

def collect_fundamentals(competitors: List[Competitor]) -> List[Dict[str, Any]]:
    """Return high-level company info."""
    return [
        {
            "name": comp.name,
            "category": comp.category,
            "tagline": comp.tagline,
            "founded_year": comp.founded_year,
            "headquarters": comp.headquarters,
            "employees_estimate": comp.employees_estimate,
            "funding_total_m": comp.funding_total_m,
            "website": comp.website,
        }
        for comp in competitors
    ]


# ──────────────────────────────────────────────
# Unified collector
# ──────────────────────────────────────────────

def collect_all() -> Dict[str, Any]:
    """Run all collectors and return a unified data payload."""
    competitors = get_all_competitors()
    return {
        "collected_at": datetime.utcnow().isoformat() + "Z",
        "competitors": [c.name for c in competitors],
        "fundamentals": collect_fundamentals(competitors),
        "news": collect_news(competitors),
        "jobs": collect_jobs(competitors),
        "feature_matrix": collect_feature_matrix(competitors + [get_our_product()]),
        "pricing": collect_pricing(competitors + [get_our_product()]),
    }


if __name__ == "__main__":
    from pprint import pprint
    data = collect_all()
    print(f"Collected at: {data['collected_at']}")
    print(f"Competitors: {data['competitors']}")
    print(f"News items:  {len(data['news'])}")
    print(f"Jobs:        {len(data['jobs'])}")
    print(f"Features:    {len(data['feature_matrix']['features'])}")
    print(f"Pricing:     {len(data['pricing'])} tiers")
