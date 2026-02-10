"""Page 1: Content Performance — weekly trends, before/after, format breakdown."""

import streamlit as st

st.set_page_config(page_title="Content Performance", page_icon="📊", layout="wide")

import src.theme  # noqa: F401, E402

from src.auth import page_guard, render_profile_sidebar  # noqa: E402
from src.data.nicole_data import get_all_data  # noqa: E402
from src.viz.charts import combo_chart, grouped_bar, horizontal_bar  # noqa: E402
from src.viz.components import (  # noqa: E402
    chart_section,
    comparison_card,
    kpi_row,
    page_header,
    source_footer,
    styled_table,
)

page_guard()
render_profile_sidebar()

data = get_all_data()
posts = data["posts"]
weekly_posts = data["weekly_posts"]
top_posts = data["worksheet"]["top_posts"]

# ---------------------------------------------------------------------------
# Header + KPIs
# ---------------------------------------------------------------------------
page_header(
    "Content Performance",
    "How Nicole's LinkedIn content performs week-over-week, "
    "and the impact since Fimiliar's service began.",
)

avg_impressions = posts["Impressions"].mean()
avg_engagements = posts["Engagements"].mean()
avg_rate = posts["Engagement Rate (%)"].mean()

kpi_row([
    {"label": "Total Posts", "value": str(len(posts))},
    {"label": "Avg Impressions / Post", "value": f"{avg_impressions:,.0f}"},
    {"label": "Avg Engagements / Post", "value": f"{avg_engagements:,.0f}"},
    {"label": "Avg Engagement Rate", "value": f"{avg_rate:.2f}%"},
])

# ---------------------------------------------------------------------------
# Weekly combo chart
# ---------------------------------------------------------------------------
st.subheader("Weekly Performance")

if not weekly_posts.empty:
    fig_combo = combo_chart(
        weekly_posts,
        x="week",
        bar_y=["total_impressions", "total_engagements"],
        line_y=["avg_rate"],
        bar_names=["Impressions", "Engagements"],
        line_names=["Avg Engagement Rate (%)"],
        title="Weekly Impressions, Engagements & Rate",
    )
    chart_section(
        fig_combo,
        caption="Bars show total weekly volume; line shows average engagement rate per post.",
    )

# ---------------------------------------------------------------------------
# Before / After comparison
# ---------------------------------------------------------------------------
st.subheader("Before vs After Fimiliar")

before = top_posts[top_posts["period"] == "Before"]
after = top_posts[top_posts["period"] == "After"]

if not before.empty and not after.empty:
    b_avg_imp = before["impressions"].mean()
    a_avg_imp = after["impressions"].mean()
    b_top = before["impressions"].max()
    a_top = after["impressions"].max()
    b_count = len(before)
    a_count = len(after)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        comparison_card("Avg Impressions / Post", b_avg_imp, a_avg_imp)
    with c2:
        comparison_card("Top Post Impressions", b_top, a_top)
    with c3:
        comparison_card("Posts Tracked", b_count, a_count)
    with c4:
        comparison_card(
            "Total Impressions",
            before["impressions"].sum(),
            after["impressions"].sum(),
        )

# ---------------------------------------------------------------------------
# Format breakdown
# ---------------------------------------------------------------------------
st.subheader("Performance by Post Format")

format_agg = (
    posts.groupby("post_format")
    .agg(
        count=("Post ID", "count"),
        avg_imp=("Impressions", "mean"),
        avg_eng=("Engagements", "mean"),
    )
    .reset_index()
    .sort_values("avg_imp", ascending=False)
)

if not format_agg.empty:
    fig_format = horizontal_bar(
        format_agg,
        x="avg_imp",
        y="post_format",
        title="Average Impressions by Post Format",
    )
    chart_section(fig_format, caption="Which content formats drive the most visibility.")

# ---------------------------------------------------------------------------
# Top posts table
# ---------------------------------------------------------------------------
st.subheader("Top Posts")

top_display = posts.nlargest(10, "Impressions")[
    ["posted_at", "post_format", "Impressions", "Engagements", "Engagement Rate (%)", "Post URL"]
].copy()
top_display["posted_at"] = top_display["posted_at"].dt.strftime("%Y-%m-%d")

styled_table(top_display, link_columns=["Post URL"])

source_footer(
    source="Nicole's Daily Update + WorkSheet TOP POSTS",
    last_updated="2026-02-09",
    notes="Before period: Dec 2024 – Jan 2025. After period: Jan – Feb 2026.",
)
