"""Page 3: Audience Quality — ICP engagers, reaction types, top people & companies."""

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Audience Quality", page_icon="🎯", layout="wide")

import src.theme  # noqa: F401, E402

from src.auth import page_guard, render_profile_sidebar  # noqa: E402
from src.data.nicole_data import get_all_data  # noqa: E402
from src.viz.charts import horizontal_bar, line_chart  # noqa: E402
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
enriched = data["enriched"]
engager_summary = data["engager_summary"]
weekly_icp = data["weekly_icp"]
contacts = data["contacts"]

# ---------------------------------------------------------------------------
# KPIs
# ---------------------------------------------------------------------------
page_header(
    "Audience Quality",
    "Measuring the quality of engagement through ICP (Ideal Customer Profile) contacts.",
)

icp_engagers = engager_summary[engager_summary["is_icp"]]
total_icp_engagements = int(enriched[enriched["is_icp"]]["reactionType"].count())
unique_icp = len(icp_engagers)
total_engagers = len(engager_summary)
icp_companies = icp_engagers["company"].dropna().nunique()

kpi_row([
    {"label": "Unique ICP Engagers", "value": str(unique_icp)},
    {"label": "Total ICP Engagements", "value": f"{total_icp_engagements:,}"},
    {"label": "ICP % of Engagers", "value": f"{unique_icp/max(total_engagers,1)*100:.1f}%"},
    {"label": "ICP Companies", "value": str(icp_companies)},
])

# ---------------------------------------------------------------------------
# ICP engagement trend
# ---------------------------------------------------------------------------
st.subheader("ICP Engagement Over Time")

if not weekly_icp.empty:
    fig_trend = line_chart(
        weekly_icp,
        x="week",
        y=["icp_engagements", "unique_icp_engagers"],
        title="Weekly ICP Engagements & Unique Engagers",
    )
    chart_section(fig_trend, caption="Weekly count of ICP engagements and unique ICP people engaging.")

# ---------------------------------------------------------------------------
# Reaction type breakdown (ICP only)
# ---------------------------------------------------------------------------
st.subheader("ICP Engagement by Reaction Type")

icp_reactions = enriched[enriched["is_icp"]].copy()
if not icp_reactions.empty:
    reaction_counts = (
        icp_reactions.groupby("reactionType")
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
    )
    fig_reactions = horizontal_bar(
        reaction_counts,
        x="count",
        y="reactionType",
        title="ICP Engagements by Reaction Type",
    )
    chart_section(fig_reactions, caption="What types of reactions ICP contacts are leaving.")

# ---------------------------------------------------------------------------
# Top ICP engagers table
# ---------------------------------------------------------------------------
left, right = st.columns(2)

with left:
    st.subheader("Top ICP Engagers")
    if not icp_engagers.empty:
        top_icp = icp_engagers.head(20)[
            ["full_name", "title", "company", "total_engagements", "likes", "comments", "icp_tier"]
        ].copy()
        styled_table(top_icp)

# ---------------------------------------------------------------------------
# Top ICP companies
# ---------------------------------------------------------------------------
with right:
    st.subheader("Top ICP Companies")
    if not icp_engagers.empty:
        company_agg = (
            icp_engagers.groupby("company")
            .agg(
                total=("total_engagements", "sum"),
                people=("profile_url", "count"),
            )
            .reset_index()
            .sort_values("total", ascending=False)
            .head(15)
        )
        company_agg.columns = ["Company", "Total Engagements", "People"]
        styled_table(company_agg)

source_footer(
    source="Engagement data joined with Contacts enrichment",
    last_updated="2026-02-09",
    notes="ICP = contacts matching Broad, Global, or Specific ICP criteria.",
)
