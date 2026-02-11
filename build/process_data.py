"""Build step: process Excel data files into JSON for the static dashboard.

Run from the project root:
    python build/process_data.py
"""

import json
from pathlib import Path

import pandas as pd

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "raw"
OUTPUT_DIR = PROJECT_ROOT / "site" / "data"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

SERVICE_START_DATE = "2026-01-17"


def _find(prefix: str) -> Path:
    """Find the first Excel file matching a prefix."""
    matches = sorted(DATA_DIR.glob(f"{prefix}*.xlsx"))
    if not matches:
        raise FileNotFoundError(f"No file matching '{prefix}*' in {DATA_DIR}")
    return matches[0]


def _to_json(data: dict | list, name: str) -> None:
    """Write data to a JSON file in the output directory."""
    path = OUTPUT_DIR / name
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, default=str, ensure_ascii=False, indent=2)
    print(f"  -> {path.relative_to(PROJECT_ROOT)} ({path.stat().st_size:,} bytes)")


# ---------------------------------------------------------------------------
# Loaders
# ---------------------------------------------------------------------------

def load_contacts() -> pd.DataFrame:
    df = pd.read_excel(_find("Contacts-Enrich-Nicole"))
    df["profile_url"] = df["profile_url"].astype(str).str.strip().str.rstrip("/")
    df["is_icp"] = (
        (df["ICP Broad?"] == "Yes")
        | (df["ICP Global?"] == "Yes")
        | (df["ICP Specific?"] == "Yes")
    )

    def _tier(row):
        if row["ICP Specific?"] == "Yes":
            return "Specific"
        if row["ICP Global?"] == "Yes":
            return "Global"
        if row["ICP Broad?"] == "Yes":
            return "Broad"
        return "Non-ICP"

    df["icp_tier"] = df.apply(_tier, axis=1)
    return df


def load_engagement() -> pd.DataFrame:
    df = pd.read_excel(_find("Engagement-Nicole"))
    df["profile_url"] = df["profile_url"].astype(str).str.strip().str.rstrip("/")
    df["Normalized Date"] = pd.to_datetime(df["Normalized Date"], errors="coerce")
    df["week"] = df["Normalized Date"].dt.to_period("W").apply(lambda p: p.start_time)
    df["post_id"] = df["Formula"].astype(str).str.strip()
    return df


def load_posts() -> pd.DataFrame:
    df = pd.read_excel(_find("Nicole's-Daily-Update"))
    df["posted_at"] = pd.to_datetime(df["posted_at"], errors="coerce")
    df["week"] = df["posted_at"].dt.to_period("W").apply(lambda p: p.start_time)

    def _parse_cp(val):
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

    cp = df["Content Performance"].apply(_parse_cp)
    for reaction in ["LIKE", "PRAISE", "EMPATHY", "INTEREST", "APPRECIATION"]:
        df[f"cp_{reaction.lower()}"] = cp.apply(
            lambda d: d.get("reaction_counts", {}).get(reaction, 0) if isinstance(d, dict) else 0
        )
    return df


def load_worksheet() -> dict[str, pd.DataFrame]:
    filepath = _find("WorkSheet_Nicole")
    sheets: dict[str, pd.DataFrame] = {}

    # DISCOVERY
    sheets["discovery"] = pd.read_excel(filepath, sheet_name="DISCOVERY")

    # ENGAGEMENT (daily)
    eng = pd.read_excel(filepath, sheet_name="ENGAGEMENT")
    eng["Date"] = pd.to_datetime(eng["Date"], errors="coerce")
    sheets["engagement_daily"] = eng

    # TOP POSTS — custom parsing (header on row 2, before/after side by side)
    tp = pd.read_excel(filepath, sheet_name="TOP POSTS", header=None, skiprows=3)
    before = tp.iloc[:, :3].copy()
    before.columns = ["post_url", "publish_date", "impressions"]
    before["period"] = "Before"

    after = tp.iloc[:, 4:7].copy()
    after.columns = ["post_url", "publish_date", "impressions"]
    after["period"] = "After"

    before = before.dropna(subset=["post_url"])
    after = after.dropna(subset=["post_url"])
    before["publish_date"] = pd.to_datetime(before["publish_date"], errors="coerce")
    after["publish_date"] = pd.to_datetime(after["publish_date"], errors="coerce")
    before["impressions"] = pd.to_numeric(before["impressions"], errors="coerce")
    after["impressions"] = pd.to_numeric(after["impressions"], errors="coerce")
    sheets["top_posts"] = pd.concat([before, after], ignore_index=True)

    # FOLLOWERS
    fol = pd.read_excel(filepath, sheet_name="FOLLOWERS")
    fol["Date"] = pd.to_datetime(fol["Date"], errors="coerce")
    sheets["followers"] = fol

    # DEMOGRAPHICS
    sheets["demographics"] = pd.read_excel(filepath, sheet_name="DEMOGRAPHICS")

    return sheets


# ---------------------------------------------------------------------------
# Derived tables
# ---------------------------------------------------------------------------

def enrich_engagement(engagement: pd.DataFrame, contacts: pd.DataFrame) -> pd.DataFrame:
    contact_cols = [
        "profile_url", "full_name", "Title Test", "Country person",
        "Company Name Test", "Company Industry", "Size", "is_icp", "icp_tier",
    ]
    contacts_slim = contacts[contact_cols].drop_duplicates(subset=["profile_url"])
    merged = engagement.merge(contacts_slim, on="profile_url", how="left")
    merged["is_icp"] = merged["is_icp"].fillna(False)
    merged["icp_tier"] = merged["icp_tier"].fillna("Unknown")
    return merged


def build_engager_summary(enriched: pd.DataFrame) -> pd.DataFrame:
    agg = enriched.groupby("profile_url").agg(
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
    ).reset_index()
    return agg.sort_values("total_engagements", ascending=False)


def build_weekly_posts(posts: pd.DataFrame) -> pd.DataFrame:
    weekly = posts.groupby("week").agg(
        num_posts=("Post ID", "count"),
        total_impressions=("Impressions", "sum"),
        total_engagements=("Engagements", "sum"),
        avg_impressions=("Impressions", "mean"),
        avg_engagements=("Engagements", "mean"),
        avg_rate=("Engagement Rate (%)", "mean"),
        total_comments=("comments_latest", "sum"),
        total_reactions=("reactions_latest", "sum"),
        total_reposts=("reposts_latest", "sum"),
    ).reset_index()
    return weekly.sort_values("week")


def build_weekly_icp(enriched: pd.DataFrame) -> pd.DataFrame:
    icp_only = enriched[enriched["is_icp"] == True].copy()
    if icp_only.empty:
        return pd.DataFrame(columns=["week", "icp_engagements", "unique_icp_engagers"])
    weekly = icp_only.groupby("week").agg(
        icp_engagements=("reactionType", "count"),
        unique_icp_engagers=("profile_url", "nunique"),
    ).reset_index().sort_values("week")
    return weekly


def build_icp_first_seen(enriched: pd.DataFrame) -> pd.DataFrame:
    icp_only = enriched[enriched["is_icp"] == True].copy()
    if icp_only.empty:
        return pd.DataFrame()
    first_seen = icp_only.groupby("profile_url").agg(
        first_engagement=("Normalized Date", "min"),
        full_name=("full_name", "first"),
        company=("Company Name Test", "first"),
        title=("Title Test", "first"),
        icp_tier=("icp_tier", "first"),
    ).reset_index().sort_values("first_engagement")
    return first_seen


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("Loading source data...")
    contacts = load_contacts()
    engagement = load_engagement()
    posts = load_posts()
    worksheet = load_worksheet()

    print("Building derived tables...")
    enriched = enrich_engagement(engagement, contacts)
    engager_summary = build_engager_summary(enriched)
    weekly_posts = build_weekly_posts(posts)
    weekly_icp = build_weekly_icp(enriched)
    icp_first_seen = build_icp_first_seen(enriched)

    print(f"\nWriting JSON to {OUTPUT_DIR.relative_to(PROJECT_ROOT)}/...")

    # 1. KPIs
    discovery = worksheet["discovery"]
    followers = worksheet["followers"]
    icp_engagers = engager_summary[engager_summary["is_icp"] == True]

    _to_json({
        "impressions_total": int(discovery.iloc[0, 1]),
        "members_reached": int(discovery.iloc[1, 1]),
        "total_posts": len(posts),
        "total_engagements": int(posts["Engagements"].sum()),
        "icp_contacts": int(contacts["is_icp"].sum()),
        "unique_engagers": len(engager_summary),
        "icp_engagers": len(icp_engagers),
        "latest_followers": int(followers["Total Followers"].iloc[-1]) if not followers.empty else 0,
        "new_followers": int(followers["New followers"].sum()) if not followers.empty else 0,
        "start_followers": int(followers["Total Followers"].iloc[0]) if not followers.empty else 0,
        "avg_engagement_rate": round(float(posts["Engagement Rate (%)"].mean()), 2),
        "avg_impressions": round(float(posts["Impressions"].mean()), 0),
        "avg_engagements_per_post": round(float(posts["Engagements"].mean()), 0),
        "service_start_date": SERVICE_START_DATE,
    }, "kpis.json")

    # 2. Posts
    posts_out = posts[[
        "Post URL", "Post ID", "Engagements", "Impressions",
        "comments_latest", "reposts_latest", "reactions_latest",
        "Engagement Rate (%)", "post_format", "posted_at", "week", "Text",
    ]].copy()
    posts_out.columns = [
        "post_url", "post_id", "engagements", "impressions",
        "comments", "reposts", "reactions",
        "engagement_rate", "post_format", "posted_at", "week", "text",
    ]
    _to_json(posts_out.to_dict(orient="records"), "posts.json")

    # 3. Weekly posts
    _to_json(weekly_posts.to_dict(orient="records"), "weekly_posts.json")

    # 4. ICP contacts
    icp_contacts = contacts[contacts["is_icp"]][[
        "full_name", "profile_url", "Title Test", "Country person",
        "Company Name Test", "Company Industry", "Size", "icp_tier",
    ]].copy()
    icp_contacts.columns = [
        "name", "profile_url", "title", "country", "company", "industry", "size", "icp_tier",
    ]
    _to_json(icp_contacts.to_dict(orient="records"), "contacts_icp.json")

    # 5. Engager summary
    es_out = engager_summary[[
        "profile_url", "full_name", "title", "company", "country",
        "total_engagements", "likes", "comments", "unique_posts",
        "first_engagement", "last_engagement", "is_icp", "icp_tier",
    ]].copy()
    _to_json(es_out.to_dict(orient="records"), "engager_summary.json")

    # 6. Weekly ICP
    _to_json(weekly_icp.to_dict(orient="records"), "weekly_icp.json")

    # 7. ICP first seen
    _to_json(icp_first_seen.to_dict(orient="records"), "icp_first_seen.json")

    # 8. Top posts (before/after)
    tp = worksheet["top_posts"]
    _to_json(tp.to_dict(orient="records"), "top_posts.json")

    # 9. Followers
    _to_json(worksheet["followers"].to_dict(orient="records"), "followers.json")

    # 10. Daily engagement
    _to_json(worksheet["engagement_daily"].to_dict(orient="records"), "engagement_daily.json")

    # 11. Demographics
    _to_json(worksheet["demographics"].to_dict(orient="records"), "demographics.json")

    # 12. Enriched reactions (ICP only, aggregated by type)
    icp_reactions = enriched[enriched["is_icp"] == True].copy()
    if not icp_reactions.empty:
        reaction_counts = (
            icp_reactions.groupby("reactionType")
            .size()
            .reset_index(name="count")
            .sort_values("count", ascending=False)
        )
        _to_json(reaction_counts.to_dict(orient="records"), "enriched_reactions.json")
    else:
        _to_json([], "enriched_reactions.json")

    # 13. Weekly all engagement (ICP vs Non-ICP for share chart)
    weekly_all = (
        enriched.groupby(["week", "is_icp"])
        .agg(engagements=("reactionType", "count"))
        .reset_index()
    )
    weekly_all["category"] = weekly_all["is_icp"].map({True: "ICP", False: "Non-ICP"})
    _to_json(weekly_all[["week", "category", "engagements"]].to_dict(orient="records"), "weekly_share.json")

    print(f"\nDone! {len(list(OUTPUT_DIR.glob('*.json')))} JSON files generated.")


if __name__ == "__main__":
    main()
