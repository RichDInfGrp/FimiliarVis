"""Page 4: Engagement Targets — hot leads, recommended people & companies."""

import streamlit as st

st.set_page_config(page_title="Engagement Targets", page_icon="🔥", layout="wide")

import src.theme  # noqa: F401, E402

from src.auth import page_guard, render_profile_sidebar  # noqa: E402
from src.data.nicole_data import get_all_data  # noqa: E402
from src.viz.charts import line_chart  # noqa: E402
from src.viz.components import (  # noqa: E402
    chart_section,
    kpi_row,
    page_header,
    source_footer,
    styled_table,
)

page_guard()
render_profile_sidebar()

data = get_all_data()
engager_summary = data["engager_summary"]
weekly_icp = data["weekly_icp"]

# ---------------------------------------------------------------------------
# Sidebar filters
# ---------------------------------------------------------------------------
with st.sidebar:
    st.subheader("Filters")
    min_engagements = st.slider("Minimum engagements", 1, 20, 5)
    icp_only = st.checkbox("ICP contacts only", value=True)

# ---------------------------------------------------------------------------
# Filter
# ---------------------------------------------------------------------------
filtered = engager_summary[engager_summary["total_engagements"] >= min_engagements].copy()
if icp_only:
    filtered = filtered[filtered["is_icp"]]

# ---------------------------------------------------------------------------
# Header + KPIs
# ---------------------------------------------------------------------------
page_header(
    "Engagement Targets",
    "Actionable list of high-engagement contacts — hot leads for outreach.",
)

hot_leads = engager_summary[
    (engager_summary["total_engagements"] >= 5) & engager_summary["is_icp"]
]
all_hot = engager_summary[engager_summary["total_engagements"] >= 5]

kpi_row([
    {"label": f"Hot Leads (≥{min_engagements})", "value": str(len(filtered))},
    {"label": "ICP Hot Leads (≥5)", "value": str(len(hot_leads))},
    {"label": "All Hot Leads (≥5)", "value": str(len(all_hot))},
    {"label": "Avg Engagements (filtered)", "value": f"{filtered['total_engagements'].mean():.1f}" if not filtered.empty else "0"},
])

# ---------------------------------------------------------------------------
# People table
# ---------------------------------------------------------------------------
st.subheader("Recommended People")

if not filtered.empty:
    display_cols = [
        "full_name", "title", "company", "country",
        "total_engagements", "likes", "comments",
        "unique_posts", "last_engagement", "icp_tier",
    ]
    people_df = filtered[display_cols].copy()
    people_df["last_engagement"] = people_df["last_engagement"].dt.strftime("%Y-%m-%d")
    people_df.columns = [
        "Name", "Title", "Company", "Country",
        "Engagements", "Likes", "Comments",
        "Posts Engaged", "Last Active", "ICP Tier",
    ]
    styled_table(people_df, height=500)
else:
    st.info("No contacts match the current filters.")

# ---------------------------------------------------------------------------
# Companies table
# ---------------------------------------------------------------------------
st.subheader("Top Companies by Engagement")

company_agg = (
    filtered.groupby("company")
    .agg(
        total=("total_engagements", "sum"),
        people=("profile_url", "count"),
        avg=("total_engagements", "mean"),
    )
    .reset_index()
    .dropna(subset=["company"])
    .sort_values("total", ascending=False)
    .head(15)
)
company_agg.columns = ["Company", "Total Engagements", "People", "Avg per Person"]

if not company_agg.empty:
    styled_table(company_agg)

# ---------------------------------------------------------------------------
# ICP weekly trend
# ---------------------------------------------------------------------------
st.subheader("ICP Engagement Trend")

if not weekly_icp.empty:
    fig_trend = line_chart(
        weekly_icp,
        x="week",
        y="unique_icp_engagers",
        title="Weekly Unique ICP Engagers",
    )
    chart_section(fig_trend, caption="Number of unique ICP contacts engaging each week.")

source_footer(
    source="Engagement data enriched with Contacts",
    last_updated="2026-02-09",
    notes="Hot leads = contacts with 5+ engagements. Filter threshold adjustable via sidebar.",
)
