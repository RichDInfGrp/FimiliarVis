"""Page 6: Acquisition Velocity — ICP per post, rolling averages, scatter."""

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Acquisition Velocity", page_icon="⚡", layout="wide")

import src.theme  # noqa: F401, E402

from src.auth import page_guard, render_profile_sidebar  # noqa: E402
from src.data.nicole_data import get_all_data  # noqa: E402
from src.viz.charts import horizontal_bar, line_chart, scatter  # noqa: E402
from src.viz.components import (  # noqa: E402
    chart_section,
    kpi_row,
    page_header,
    source_footer,
)

page_guard()
render_profile_sidebar()

data = get_all_data()
weekly_posts = data["weekly_posts"]
weekly_icp = data["weekly_icp"]
posts = data["posts"]
enriched = data["enriched"]

# ---------------------------------------------------------------------------
# Merge weekly data
# ---------------------------------------------------------------------------
weekly = weekly_posts.merge(weekly_icp, on="week", how="left").fillna(0)
weekly["icp_per_post"] = weekly["unique_icp_engagers"] / weekly["num_posts"].clip(lower=1)
weekly["rolling_icp"] = weekly["unique_icp_engagers"].rolling(4, min_periods=1).mean()
weekly["rolling_icp_per_post"] = weekly["icp_per_post"].rolling(4, min_periods=1).mean()

# ---------------------------------------------------------------------------
# KPIs
# ---------------------------------------------------------------------------
page_header(
    "Acquisition Velocity",
    "How efficiently content acquires ICP engagement — ICP contacts per post and rolling trends.",
)

total_icp_eng = int(weekly["unique_icp_engagers"].sum())
total_posts_count = int(weekly["num_posts"].sum())
overall_rate = total_icp_eng / max(total_posts_count, 1)

kpi_row([
    {"label": "Total ICP Engagers", "value": str(total_icp_eng)},
    {"label": "Total Posts", "value": str(total_posts_count)},
    {"label": "ICP per Post (overall)", "value": f"{overall_rate:.2f}"},
    {"label": "Weeks of Data", "value": str(len(weekly))},
])

# ---------------------------------------------------------------------------
# ICP per week bar + rolling average
# ---------------------------------------------------------------------------
st.subheader("Weekly ICP Engagers & Rolling Average")

if not weekly.empty:
    fig_vel = line_chart(
        weekly,
        x="week",
        y=["unique_icp_engagers", "rolling_icp"],
        title="ICP Engagers per Week (with 4-week rolling avg)",
    )
    chart_section(fig_vel, caption="Solid line shows 4-week rolling average of unique ICP engagers.")

# ---------------------------------------------------------------------------
# ICP per post trend
# ---------------------------------------------------------------------------
st.subheader("ICP per Post Efficiency")

if not weekly.empty:
    fig_eff = line_chart(
        weekly,
        x="week",
        y=["icp_per_post", "rolling_icp_per_post"],
        title="ICP Engagers per Post (with rolling avg)",
    )
    chart_section(fig_eff, caption="Efficiency metric: how many ICP contacts each post reaches.")

# ---------------------------------------------------------------------------
# Posts vs ICP scatter
# ---------------------------------------------------------------------------
st.subheader("Posts vs ICP Engagement")

if not weekly.empty and len(weekly) > 2:
    fig_scatter = scatter(
        weekly,
        x="num_posts",
        y="unique_icp_engagers",
        title="Weekly Posts vs ICP Engagers",
        trendline="ols",
        size="total_impressions",
    )
    chart_section(
        fig_scatter,
        caption="Does posting more lead to more ICP engagement? Bubble size = total impressions.",
    )

# ---------------------------------------------------------------------------
# Efficiency scorecards
# ---------------------------------------------------------------------------
st.subheader("Efficiency Scorecards")

if not weekly.empty:
    best_week = weekly.loc[weekly["icp_per_post"].idxmax()]
    most_icp = weekly.loc[weekly["unique_icp_engagers"].idxmax()]

    c1, c2, c3 = st.columns(3)
    c1.metric("Best ICP/Post Week", f"{best_week['icp_per_post']:.2f}", help=str(best_week["week"].date()))
    c2.metric("Most ICP Engagers Week", int(most_icp["unique_icp_engagers"]), help=str(most_icp["week"].date()))
    c3.metric("Avg Posts/Week", f"{weekly['num_posts'].mean():.1f}")

source_footer(
    source="Daily Update + Engagement data (enriched)",
    last_updated="2026-02-09",
    notes="ICP per post = unique ICP engagers / posts published that week.",
)
