"""
sample_data.py — Simulated competitor data sources.

Provides structured competitor profiles, feature matrices, pricing,
press/analyst mentions, and job-posting signals used by the pipeline.
All data is synthetic but representative of real competitive landscapes.
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from typing import List
import random

random.seed(42)


# ──────────────────────────────────────────────
# Data models
# ──────────────────────────────────────────────

@dataclass
class Feature:
    name: str
    category: str
    has_it: bool
    quality_score: int  # 1-10 subjective quality estimate
    notes: str = ""


@dataclass
class PricingTier:
    name: str
    price_monthly: float
    users_included: int
    key_limits: str
    contract: str  # "monthly" | "annual" | "enterprise"


@dataclass
class NewsItem:
    headline: str
    source: str
    date: str
    sentiment: str  # "positive" | "negative" | "neutral"
    summary: str


@dataclass
class JobPosting:
    title: str
    department: str
    posted: str
    remote: bool


@dataclass
class Competitor:
    name: str
    tagline: str
    category: str
    founded_year: int
    headquarters: str
    employees_estimate: int
    funding_total_m: float
    features: List[Feature]
    pricing: List[PricingTier]
    recent_news: List[NewsItem]
    job_postings: List[JobPosting]
    website: str

    def to_dict(self):
        return asdict(self)


# ──────────────────────────────────────────────
# Competitors
# ──────────────────────────────────────────────

COMPETITOR_A = Competitor(
    name="DataForge AI",
    tagline="Enterprise-grade AI-powered analytics for the modern data stack",
    category="AI Analytics Platform",
    founded_year=2019,
    headquarters="San Francisco, CA",
    employees_estimate=340,
    funding_total_m=124.0,
    website="https://dataforge-ai.example.com",
    features=[
        Feature("Natural-language querying", "Query", True, 9, "Best-in-class NL-to-SQL"),
        Feature("Dashboard builder", "Visualization", True, 8, "Drag-and-drop, 40+ chart types"),
        Feature("Automated insight detection", "Analytics", True, 8, "Anomaly & trend detection, weekly email"),
        Feature("Slack integration", "Integrations", True, 7, "Basic slash commands & alerts"),
        Feature("API access", "Platform", True, 9, "REST + GraphQL, generous rate limits"),
        Feature("Custom ML model hosting", "Platform", True, 7, "Limited to their AutoML models"),
        Feature("Collaboration / workspaces", "Collaboration", True, 9, "Real-time multi-user editing"),
        Feature("On-premise deployment", "Deployment", True, 6, "Kubernetes-based, requires their support"),
        Feature("Role-based access control", "Security", True, 8, "SSO/SAML, SCIM, granular roles"),
        Feature("Data source connectors", "Integrations", True, 9, "120+ native connectors"),
        Feature("Audit logging", "Security", True, 8, "90-day retention on standard plan"),
        Feature("Webhooks", "Integrations", True, 7, "Outbound on events"),
        Feature("Version history", "Collaboration", True, 6, "7 days on standard"),
    ],
    pricing=[
        PricingTier("Starter", 99.0, 5, "10k queries/month", "monthly"),
        PricingTier("Team", 499.0, 25, "100k queries/month", "monthly"),
        PricingTier("Enterprise", 0.0, 0, "Custom limits", "enterprise"),
    ],
    recent_news=[
        NewsItem("DataForge Raises $50M Series C for AI Analytics", "TechCrunch", "2025-08-10", "positive",
                  "DataForge AI closed a $50M Series C led by Sequoia to expand its NL-to-SQL product."),
        NewsItem("DataForge Launches Real-Time Dashboarding", "Analytics Today", "2025-07-22", "positive",
                  "New streaming data support enables sub-second dashboard refreshes."),
        NewsItem("DataForge Security Incident — API Key Leak", "SecurityWeek", "2025-06-14", "negative",
                  "Exposed API keys in error logs affected ~200 customers; rotated within 4 hours."),
        NewsItem("DataForge Hires Chief AI Officer from Google", "VentureBeat", "2025-05-18", "positive",
                  "Dr. Lina Zhou joins to lead foundation-model-powered analytics."),
    ],
    job_postings=[
        JobPosting("Staff Engineer, Query Engine", "Engineering", "2025-08-01", True),
        JobPosting("Product Manager, Platform", "Product", "2025-07-15", True),
        JobPosting("Solutions Architect", "Customer Success", "2025-07-30", False),
    ],
)

COMPETITOR_B = Competitor(
    name="QueryCraft",
    tagline="Lightning-fast dashboards your whole team will actually use",
    category="BI & Visualization",
    founded_year=2021,
    headquarters="Austin, TX",
    employees_estimate=85,
    funding_total_m=18.5,
    website="https://querycraft.example.com",
    features=[
        Feature("Natural-language querying", "Query", True, 6, "Keyword-based, less accurate than DataForge"),
        Feature("Dashboard builder", "Visualization", True, 9, "Beautiful, consumer-grade UI, 50+ chart types"),
        Feature("Automated insight detection", "Analytics", True, 5, "Basic anomaly flags only"),
        Feature("Slack integration", "Integrations", True, 8, "Rich unfurls, scheduled reports in Slack"),
        Feature("API access", "Platform", True, 5, "REST-only, tight rate limits"),
        Feature("Custom ML model hosting", "Platform", False, 0, ""),
        Feature("Collaboration / workspaces", "Collaboration", True, 8, "Comments, sharing, viewer-only seats"),
        Feature("On-premise deployment", "Deployment", False, 0, ""),
        Feature("Role-based access control", "Security", True, 6, "Basic SSO, no SCIM"),
        Feature("Data source connectors", "Integrations", True, 7, "45+ connectors"),
        Feature("Audit logging", "Security", True, 5, "7-day retention"),
        Feature("Webhooks", "Integrations", True, 6, "Limited event types"),
        Feature("Version history", "Collaboration", True, 7, "30 days across all plans"),
    ],
    pricing=[
        PricingTier("Free", 0.0, 3, "1 dashboard, 5k queries", "monthly"),
        PricingTier("Pro", 49.0, 10, "10 dashboards, 20k queries", "monthly"),
        PricingTier("Business", 199.0, 50, "Unlimited dashboards, 100k queries", "monthly"),
        PricingTier("Enterprise", 0.0, 0, "Custom", "enterprise"),
    ],
    recent_news=[
        NewsItem("QueryCraft Launches Free Tier, Attracts 10K Signups in Week", "ProductHunt", "2025-08-12", "positive",
                  "Free tier with 3 seats drives huge top-of-funnel growth for QueryCraft."),
        NewsItem("QueryCraft Partners with Snowflake for Native App", "Business Wire", "2025-07-05", "positive",
                  "Snowflake Native App lets customers run QueryCraft without data egress."),
        NewsItem("QueryCraft CEO Steps Down Amid Strategy Debate", "Bloomberg", "2025-06-28", "negative",
                  "Founder-CEO leaves after board disagreement over enterprise vs. SMB focus."),
    ],
    job_postings=[
        JobPosting("Senior Frontend Engineer", "Engineering", "2025-08-05", True),
        JobPosting("Head of Marketing", "Marketing", "2025-07-20", True),
    ],
)

COMPETITOR_C = Competitor(
    name="InsightGrid",
    tagline="The autonomous data analyst — ask anything, get answers instantly",
    category="AI-Native Analytics",
    founded_year=2023,
    headquarters="New York, NY",
    employees_estimate=42,
    funding_total_m=8.2,
    website="https://insightgrid.example.com",
    features=[
        Feature("Natural-language querying", "Query", True, 8, "Good accuracy, but SQL-only under the hood"),
        Feature("Dashboard builder", "Visualization", True, 5, "Basic charts, limited customization"),
        Feature("Automated insight detection", "Analytics", True, 9, "AI-powered weekly briefings, root-cause analysis"),
        Feature("Slack integration", "Integrations", True, 9, "Full conversational interface in Slack"),
        Feature("API access", "Platform", True, 6, "REST-only, docs incomplete"),
        Feature("Custom ML model hosting", "Platform", False, 0, ""),
        Feature("Collaboration / workspaces", "Collaboration", True, 5, "Basic sharing only"),
        Feature("On-premise deployment", "Deployment", False, 0, ""),
        Feature("Role-based access control", "Security", True, 4, "No SSO; basic email/password roles"),
        Feature("Data source connectors", "Integrations", True, 4, "15+ connectors, mostly cloud warehouses"),
        Feature("Audit logging", "Security", True, 3, "No customer-facing audit trail"),
        Feature("Webhooks", "Integrations", False, 0, ""),
        Feature("Version history", "Collaboration", True, 4, "Not versioned; overwrites on edit"),
    ],
    pricing=[
        PricingTier("Starter", 29.0, 5, "5k queries/mo", "monthly"),
        PricingTier("Growth", 149.0, 20, "50k queries/mo", "monthly"),
        PricingTier("Scale", 599.0, 100, "500k queries/mo", "monthly"),
    ],
    recent_news=[
        NewsItem("InsightGrid Wins 'Best New Tool' at Data Summit 2025", "DataSummit Blog", "2025-08-01", "positive",
                  "Judges praised its Slack-native conversational interface and insight automation."),
        NewsItem("InsightGrid Releases Open-Source NL-to-SQL Benchmark", "GitHub Trending", "2025-07-18", "positive",
                  "Benchmark dataset of 5,000 domain-specific queries released under Apache 2.0."),
        NewsItem("InsightGrid Security Audit Reveals Gaps in Auth System", "Security Blog", "2025-06-30", "negative",
                  "Penetration test found missing rate limiting and weak session management."),
    ],
    job_postings=[
        JobPosting("Founding Engineer (Backend)", "Engineering", "2025-08-10", True),
        JobPosting("Developer Relations Lead", "Marketing", "2025-08-01", True),
        JobPosting("Head of Sales", "Sales", "2025-07-25", False),
        JobPosting("ML Engineer — NLP", "Engineering", "2025-07-15", True),
    ],
)


# ──────────────────────────────────────────────
# Our own product (for comparison)
# ──────────────────────────────────────────────

OUR_PRODUCT = Competitor(
    name="InsightPulse (Us)",
    tagline="AI-driven competitive intelligence, automated daily",
    category="Competitive Intelligence Automation",
    founded_year=2024,
    headquarters="Remote-first",
    employees_estimate=18,
    funding_total_m=3.5,
    website="https://insightpulse.example.com",
    features=[
        Feature("Natural-language querying", "Query", True, 7, "Improving; behind DataForge"),
        Feature("Dashboard builder", "Visualization", True, 6, "Functional but needs UX polish"),
        Feature("Automated insight detection", "Analytics", True, 8, "Solid weekly trend reports"),
        Feature("Slack integration", "Integrations", True, 8, "Daily briefs + on-demand queries"),
        Feature("API access", "Platform", True, 7, "REST + WebSocket planned"),
        Feature("Custom ML model hosting", "Platform", False, 0, ""),
        Feature("Collaboration / workspaces", "Collaboration", True, 7, "Shared workspaces + comments"),
        Feature("On-premise deployment", "Deployment", False, 0, "Roadmap item for Q1"),
        Feature("Role-based access control", "Security", True, 7, "SSO in beta; basic RBAC shipped"),
        Feature("Data source connectors", "Integrations", True, 6, "30+ connectors; cloud + hybrid"),
        Feature("Audit logging", "Security", True, 6, "30-day retention"),
        Feature("Webhooks", "Integrations", True, 5, "Basic webhooks; roadmap to expand"),
        Feature("Version history", "Collaboration", True, 5, "Basic versioning on reports"),
    ],
    pricing=[
        PricingTier("Starter", 79.0, 5, "10k queries/mo", "monthly"),
        PricingTier("Growth", 299.0, 20, "75k queries/mo", "monthly"),
        PricingTier("Enterprise", 0.0, 0, "Custom", "enterprise"),
    ],
    recent_news=[
        NewsItem("InsightPulse Launches Automated Briefing Feature", "Our Blog", "2025-08-14", "positive",
                  "New daily competitive brief generation now available on Growth plan."),
    ],
    job_postings=[],
)

ALL_COMPETITORS = [COMPETITOR_A, COMPETITOR_B, COMPETITOR_C]
ALL_PROFILES = [*ALL_COMPETITORS, OUR_PRODUCT]


def get_all_competitors() -> List[Competitor]:
    """Return the list of competitor profiles."""
    return ALL_COMPETITORS


def get_our_product() -> Competitor:
    """Return our own product profile."""
    return OUR_PRODUCT


def get_all_profiles() -> List[Competitor]:
    """Return all profiles including our own."""
    return ALL_PROFILES


def print_summary():
    """Quick diagnostic print of loaded data."""
    for p in ALL_PROFILES:
        print(f"{p.name:25s} | {p.category:30s} | {p.employees_estimate:4d} emp | ${p.funding_total_m:<6.1f}M")


if __name__ == "__main__":
    print("=== Competitor Data Summary ===\n")
    print_summary()
