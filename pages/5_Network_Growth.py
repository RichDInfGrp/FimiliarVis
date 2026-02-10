"""Page 5: Network Growth — cumulative ICP engagers, share, waterfall."""

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Network Growth", page_icon="🌐", layout="wide")

import src.theme  # noqa: F401, E402

from src.auth import page_guard, render_profile_sidebar  # noqa: E402
from src.data.nicole_data import get_all_data  # noqa: E402
from src.viz.charts import area_chart, line_chart, waterfall_chart  # noqa: E402
from src.viz.components import (  # noqa: E402
    chart_section,
    kpi_row,
    page_header,
    source_footer,
)

page_guard()
render_profile_sidebar()

data = get_all_data()
icp_first_seen = data["icp_first_seen"]
weekly_icp = data["weekly_icp"]
enriched = data["enriched"]

# ---------------------------------------------------------------------------
# KPIs
# ---------------------------------------------------------------------------
page_header(
    "Network Growth",
    "How Nicole's ICP network is expanding over time — based on first engagement date "
    "as a proxy for when contacts entered her orbit.",
)

total_icp_ever = len(icp_first_seen)
if not icp_first_seen.empty:
    earliest = icp_first_seen["first_engagement"].min()
    latest = icp_first_seen["first_engagement"].max()
    span_days = max((latest - earliest).days, 1)
    rate = total_icp_ever / span_days * 7
else:
    rate = 0

kpi_row([
    {"label": "Total ICP Engagers", "value": str(total_icp_ever)},
    {"label": "ICP per Week (avg)", "value": f"{rate:.1f}"},
    {"label": "Weeks of Data", "value": str(len(weekly_icp))},
    {"label": "Latest ICP Engagement", "value": latest.strftime("%Y-%m-%d") if not icp_first_seen.empty else "N/A"},
])

# ---------------------------------------------------------------------------
# Cumulative ICP engagers
# ---------------------------------------------------------------------------
st.subheader("Cumulative ICP Engagers Over Time")

if not icp_first_seen.empty:
    cumulative = (
        icp_first_seen.groupby("first_engagement")
        .size()
        .reset_index(name="new_icp")
        .sort_values("first_engagement")
    )
    cumulative["cumulative_icp"] = cumulative["new_icp"].cumsum()

    fig_cum = line_chart(
        cumulative,
        x="first_engagement",
        y="cumulative_icp",
        title="Cumulative ICP Engagers (First Engagement Date)",
    )
    chart_section(
        fig_cum,
        caption="Each ICP contact counted at their first engagement date. "
        "This is a proxy — actual connection dates are unavailable.",
    )

# ---------------------------------------------------------------------------
# ICP share over time (stacked area)
# ---------------------------------------------------------------------------
st.subheader("ICP vs Non-ICP Engagement Share")

if not enriched.empty:
    weekly_all = (
        enriched.groupby(["week", "is_icp"])
        .size()
        .reset_index(name="engagements")
    )
    weekly_all["Category"] = weekly_all["is_icp"].map({True: "ICP", False: "Non-ICP"})

    fig_share = area_chart(
        weekly_all,
        x="week",
        y="engagements",
        color="Category",
        title="ICP vs Non-ICP Engagement Share",
        normalize=True,
    )
    chart_section(fig_share, caption="ICP share of total weekly engagement activity.")

# ---------------------------------------------------------------------------
# Waterfall — weekly ICP growth
# ---------------------------------------------------------------------------
st.subheader("Weekly ICP Growth Waterfall")

if not weekly_icp.empty and len(weekly_icp) > 1:
    weeks = weekly_icp["week"].dt.strftime("%b %d").tolist()
    new_engagers = weekly_icp["unique_icp_engagers"].tolist()
    measures = ["absolute"] + ["relative"] * (len(new_engagers) - 1)

    fig_wf = waterfall_chart(
        categories=weeks,
        values=new_engagers,
        title="Weekly New ICP Engagers",
        measure=measures,
    )
    chart_section(fig_wf, caption="Net new unique ICP engagers each week.")

source_footer(
    source="Engagement data enriched with Contacts",
    last_updated="2026-02-09",
    notes="First engagement date used as proxy for ICP network entry. "
    "Connection dates are not available in the source data.",
)
