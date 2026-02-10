"""Page 2: Audience Growth — followers, impressions, ICP vs Non-ICP."""

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Audience Growth", page_icon="📈", layout="wide")

import src.theme  # noqa: F401, E402

from src.auth import page_guard, render_profile_sidebar  # noqa: E402
from src.data.nicole_data import get_all_data  # noqa: E402
from src.viz.charts import donut, line_chart  # noqa: E402
from src.viz.components import (  # noqa: E402
    chart_section,
    kpi_row,
    page_header,
    source_footer,
)

page_guard()
render_profile_sidebar()

data = get_all_data()
discovery = data["worksheet"]["discovery"]
followers = data["worksheet"]["followers"]
engagement_daily = data["worksheet"]["engagement_daily"]
contacts = data["contacts"]
engager_summary = data["engager_summary"]
posts = data["posts"]

# ---------------------------------------------------------------------------
# KPIs
# ---------------------------------------------------------------------------
page_header(
    "Audience Growth",
    "Tracking follower growth, reach, and the composition of Nicole's engaged audience.",
)

impressions_total = discovery.iloc[0, 1]
members_reached = discovery.iloc[1, 1]
latest_followers = int(followers["Total Followers"].iloc[-1]) if not followers.empty else 0
start_followers = int(followers["Total Followers"].iloc[0]) if not followers.empty else 0
new_followers = int(followers["New followers"].sum()) if not followers.empty else 0
total_engagers = len(engager_summary)
icp_engagers = int(engager_summary["is_icp"].sum())
total_posts = len(posts)

kpi_row([
    {"label": "Impressions", "value": f"{impressions_total:,}"},
    {"label": "Members Reached", "value": f"{members_reached:,}"},
    {"label": "Followers", "value": f"{latest_followers:,}", "delta": f"+{new_followers}"},
    {"label": "Total Posts", "value": str(total_posts)},
])

st.markdown("")

kpi_row([
    {"label": "New Followers (24d)", "value": f"+{new_followers}"},
    {"label": "Unique Engagers", "value": f"{total_engagers:,}"},
    {"label": "ICP Engagers", "value": str(icp_engagers)},
    {"label": "ICP % of Engagers", "value": f"{icp_engagers/max(total_engagers,1)*100:.1f}%"},
])

# ---------------------------------------------------------------------------
# Followers trend
# ---------------------------------------------------------------------------
st.subheader("Follower Growth (24-Day Window)")

if not followers.empty:
    fig_fol = line_chart(
        followers,
        x="Date",
        y="Total Followers",
        title="Total Followers Over Time",
    )
    chart_section(
        fig_fol,
        caption=f"Followers grew from {start_followers:,} to {latest_followers:,} (+{new_followers}).",
    )

# ---------------------------------------------------------------------------
# ICP vs Non-ICP donut
# ---------------------------------------------------------------------------
left, right = st.columns(2)

with left:
    st.subheader("Engager Composition")
    icp_donut_df = pd.DataFrame({
        "Category": ["ICP", "Non-ICP"],
        "Count": [icp_engagers, total_engagers - icp_engagers],
    })
    fig_donut = donut(icp_donut_df, values="Count", names="Category", title="ICP vs Non-ICP Engagers")
    chart_section(fig_donut, caption=f"{icp_engagers} of {total_engagers} unique engagers are ICP contacts.")

# ---------------------------------------------------------------------------
# Daily impressions & engagements
# ---------------------------------------------------------------------------
with right:
    st.subheader("Daily Impressions & Engagements")
    if not engagement_daily.empty:
        fig_daily = line_chart(
            engagement_daily,
            x="Date",
            y=["Impressions", "Engagements"],
            title="Daily Impressions & Engagements",
        )
        chart_section(fig_daily, caption="Daily performance from the WorkSheet engagement data.")

source_footer(
    source="WorkSheet (DISCOVERY, FOLLOWERS, ENGAGEMENT) + Engagement data",
    last_updated="2026-02-09",
    notes="Follower data covers a 24-day window. ICP classification based on Fimiliar enrichment.",
)
