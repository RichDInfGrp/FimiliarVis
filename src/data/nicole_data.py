"""Fimiliar Vis — Nicole Bello data pipeline.

Central module that loads all 4 Excel data files, cleans and joins them,
and produces every derived DataFrame the dashboard pages need.
"""

import json
from pathlib import Path

import pandas as pd
import streamlit as st

from src.config import DATA_FILE_PREFIXES


# ---------------------------------------------------------------------------
# Individual loaders (cached — each reads from disk once)
# ---------------------------------------------------------------------------

@st.cache_data
def load_contacts() -> pd.DataFrame:
    """Load and clean the contacts/enrichment file."""
    df = _find_and_read(DATA_FILE_PREFIXES["contacts"])
    df["profile_url"] = df["profile_url"].astype(str).str.strip().str.rstrip("/")
    df["is_icp"] = (
        (df["ICP Broad?"] == "Yes")
        | (df["ICP Global?"] == "Yes")
        | (df["ICP Specific?"] == "Yes")
    )

    def _tier(row):
        if row.get("ICP Specific?") == "Yes":
            return "Specific"
        if row.get("ICP Global?") == "Yes":
            return "Global"
        if row.get("ICP Broad?") == "Yes":
            return "Broad"
        return "Non-ICP"

    df["icp_tier"] = df.apply(_tier, axis=1)
    return df


@st.cache_data
def load_engagement() -> pd.DataFrame:
    """Load and clean the engagement (post-interaction) file."""
    df = _find_and_read(DATA_FILE_PREFIXES["engagement"])
    df["profile_url"] = df["profile_url"].astype(str).str.strip().str.rstrip("/")
    df["Normalized Date"] = pd.to_datetime(df["Normalized Date"], errors="coerce")
    df["week"] = df["Normalized Date"].dt.to_period("W").apply(
        lambda p: p.start_time
    )
    df["post_id"] = df["Formula"].astype(str).str.strip()
    return df


@st.cache_data
def load_posts() -> pd.DataFrame:
    """Load the daily-update posts file and parse Content Performance JSON."""
    df = _find_and_read(DATA_FILE_PREFIXES["daily_update"])
    df["posted_at"] = pd.to_datetime(df["posted_at"], errors="coerce")
    df["week"] = df["posted_at"].dt.to_period("W").apply(lambda p: p.start_time)

    cp = df["Content Performance"].apply(_parse_content_performance)
    for key in ("LIKE", "PRAISE", "EMPATHY", "INTEREST", "APPRECIATION"):
        df[f"cp_{key.lower()}"] = cp.apply(
            lambda d, k=key: d.get("reaction_counts", {}).get(k, 0)
            if isinstance(d, dict)
            else 0
        )
    return df


@st.cache_data
def load_worksheet_data() -> dict[str, pd.DataFrame]:
    """Load all relevant sheets from the WorkSheet file."""
    filepath = _find_file(DATA_FILE_PREFIXES["worksheet"])
    sheets: dict[str, pd.DataFrame] = {}

    # DISCOVERY — summary KPIs
    sheets["discovery"] = pd.read_excel(filepath, sheet_name="DISCOVERY")

    # ENGAGEMENT — daily impressions & engagements
    eng = pd.read_excel(filepath, sheet_name="ENGAGEMENT")
    eng["Date"] = pd.to_datetime(eng["Date"], errors="coerce")
    sheets["engagement_daily"] = eng

    # TOP POSTS — before/after comparison (custom layout)
    tp = pd.read_excel(
        filepath, sheet_name="TOP POSTS", header=None, skiprows=3
    )
    before = tp.iloc[:, :3].copy()
    before.columns = ["post_url", "publish_date", "impressions"]
    before["period"] = "Before"

    after = tp.iloc[:, 4:7].copy()
    after.columns = ["post_url", "publish_date", "impressions"]
    after["period"] = "After"

    for part in (before, after):
        part["publish_date"] = pd.to_datetime(part["publish_date"], errors="coerce")
        part["impressions"] = pd.to_numeric(part["impressions"], errors="coerce")

    before = before.dropna(subset=["post_url"])
    after = after.dropna(subset=["post_url"])
    sheets["top_posts"] = pd.concat([before, after], ignore_index=True)

    # FOLLOWERS — daily new + total
    fol = pd.read_excel(filepath, sheet_name="FOLLOWERS")
    fol["Date"] = pd.to_datetime(fol["Date"], errors="coerce")
    sheets["followers"] = fol

    # DEMOGRAPHICS — job titles, locations, etc.
    sheets["demographics"] = pd.read_excel(filepath, sheet_name="DEMOGRAPHICS")

    return sheets


# ---------------------------------------------------------------------------
# Derived / enriched tables
# ---------------------------------------------------------------------------


def enrich_engagement(
    engagement: pd.DataFrame, contacts: pd.DataFrame
) -> pd.DataFrame:
    """Left-join engagement with contacts on profile_url to add ICP info."""
    contact_cols = [
        "profile_url",
        "full_name",
        "Title Test",
        "Country person",
        "Company Name Test",
        "Company Industry",
        "Size",
        "is_icp",
        "icp_tier",
    ]
    contacts_slim = contacts[contact_cols].drop_duplicates(subset=["profile_url"])
    merged = engagement.merge(contacts_slim, on="profile_url", how="left")
    merged["is_icp"] = merged["is_icp"].fillna(False)
    merged["icp_tier"] = merged["icp_tier"].fillna("Unknown")
    return merged


def build_engager_summary(enriched: pd.DataFrame) -> pd.DataFrame:
    """Group engagement by person: total, likes, comments, dates."""
    agg = (
        enriched.groupby("profile_url")
        .agg(
            total_engagements=("reactionType", "count"),
            likes=("reactionType", lambda x: (x == "LIKE").sum()),
            comments=("reactionType", lambda x: (x == "COMMENT").sum()),
            first_engagement=("Normalized Date", "min"),
            last_engagement=("Normalized Date", "max"),
            unique_posts=("post_id", "nunique"),
            full_name=("full_name", "first"),
            title=("Title Test", "first"),
            company=("Company Name Test", "first"),
            country=("Country person", "first"),
            is_icp=("is_icp", "first"),
            icp_tier=("icp_tier", "first"),
        )
        .reset_index()
    )
    return agg.sort_values("total_engagements", ascending=False)


def build_weekly_posts(posts: pd.DataFrame) -> pd.DataFrame:
    """Aggregate posts by week."""
    weekly = (
        posts.groupby("week")
        .agg(
            num_posts=("Post ID", "count"),
            total_impressions=("Impressions", "sum"),
            total_engagements=("Engagements", "sum"),
            avg_impressions=("Impressions", "mean"),
            avg_engagements=("Engagements", "mean"),
            avg_rate=("Engagement Rate (%)", "mean"),
            total_comments=("comments_latest", "sum"),
            total_reactions=("reactions_latest", "sum"),
            total_reposts=("reposts_latest", "sum"),
        )
        .reset_index()
        .sort_values("week")
    )
    return weekly


def build_weekly_icp_engagement(enriched: pd.DataFrame) -> pd.DataFrame:
    """Weekly ICP engagement summary."""
    icp_only = enriched[enriched["is_icp"]].copy()
    if icp_only.empty:
        return pd.DataFrame(columns=["week", "icp_engagements", "unique_icp_engagers"])
    return (
        icp_only.groupby("week")
        .agg(
            icp_engagements=("reactionType", "count"),
            unique_icp_engagers=("profile_url", "nunique"),
        )
        .reset_index()
        .sort_values("week")
    )


def build_icp_first_seen(enriched: pd.DataFrame) -> pd.DataFrame:
    """For each ICP contact, find their first engagement date."""
    icp_only = enriched[enriched["is_icp"]].copy()
    if icp_only.empty:
        return pd.DataFrame()
    return (
        icp_only.groupby("profile_url")
        .agg(
            first_engagement=("Normalized Date", "min"),
            full_name=("full_name", "first"),
            company=("Company Name Test", "first"),
            title=("Title Test", "first"),
            icp_tier=("icp_tier", "first"),
        )
        .reset_index()
        .sort_values("first_engagement")
    )


# ---------------------------------------------------------------------------
# Master orchestrator
# ---------------------------------------------------------------------------


@st.cache_data
def get_all_data() -> dict:
    """Load and process all data. Returns dict of DataFrames."""
    contacts = load_contacts()
    engagement = load_engagement()
    posts = load_posts()
    worksheet = load_worksheet_data()

    enriched = enrich_engagement(engagement, contacts)
    engager_summary = build_engager_summary(enriched)
    weekly_posts = build_weekly_posts(posts)
    weekly_icp = build_weekly_icp_engagement(enriched)
    icp_first_seen = build_icp_first_seen(enriched)

    return {
        "contacts": contacts,
        "engagement": engagement,
        "posts": posts,
        "worksheet": worksheet,
        "enriched": enriched,
        "engager_summary": engager_summary,
        "weekly_posts": weekly_posts,
        "weekly_icp": weekly_icp,
        "icp_first_seen": icp_first_seen,
    }


# ---------------------------------------------------------------------------
# Helpers (private)
# ---------------------------------------------------------------------------

_DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "raw"


def _find_file(prefix: str) -> Path:
    """Find a file by prefix using glob."""
    matches = sorted(_DATA_DIR.glob(f"{prefix}*.xlsx"))
    if not matches:
        raise FileNotFoundError(
            f"No .xlsx file matching prefix '{prefix}' in {_DATA_DIR}"
        )
    return matches[0]


def _find_and_read(prefix: str, **kwargs) -> pd.DataFrame:
    """Find an Excel file by prefix and read it."""
    return pd.read_excel(_find_file(prefix), **kwargs)


def _parse_content_performance(val) -> dict:
    """Parse Content Performance JSON column."""
    if pd.isna(val):
        return {}
    try:
        data = json.loads(val) if isinstance(val, str) else val
        if isinstance(data, list) and len(data) > 0:
            return data[0]
        if isinstance(data, dict):
            return data
    except (json.JSONDecodeError, TypeError):
        pass
    return {}
