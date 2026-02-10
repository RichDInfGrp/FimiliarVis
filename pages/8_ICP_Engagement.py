"""Page 8: ICP Engagement — funnel, ICP% over time, engaged-not-connected."""

import pandas as pd
import streamlit as st

st.set_page_config(page_title="ICP Engagement", page_icon="🔬", layout="wide")

import src.theme  # noqa: F401, E402

from src.auth import page_guard, render_profile_sidebar  # noqa: E402
from src.data.nicole_data import get_all_data  # noqa: E402
from src.viz.charts import funnel_chart, line_chart  # noqa: E402
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
contacts = data["contacts"]
enriched = data["enriched"]
engager_summary = data["engager_summary"]
weekly_icp = data["weekly_icp"]

# ---------------------------------------------------------------------------
# Compute funnel numbers
# ---------------------------------------------------------------------------
total_contacts = len(contacts)
icp_contacts = int(contacts["is_icp"].sum())

icp_engagers = engager_summary[engager_summary["is_icp"]]
icp_engaged = len(icp_engagers)
icp_3plus = int((icp_engagers["total_engagements"] >= 3).sum())
icp_commented = int((icp_engagers["comments"] > 0).sum())

# ---------------------------------------------------------------------------
# Header + KPIs
# ---------------------------------------------------------------------------
page_header(
    "ICP Engagement",
    "Deep dive into how ICP contacts engage — from awareness to active participation.",
)

kpi_row([
    {"label": "Total Contacts", "value": str(total_contacts)},
    {"label": "ICP Contacts", "value": str(icp_contacts)},
    {"label": "ICP Engaged", "value": str(icp_engaged)},
    {"label": "ICP 3+ Engagements", "value": str(icp_3plus)},
])

# ---------------------------------------------------------------------------
# Funnel
# ---------------------------------------------------------------------------
st.subheader("ICP Engagement Funnel")

funnel_stages = [
    "All Contacts",
    "ICP Contacts",
    "ICP Engaged",
    "3+ Engagements",
    "Commented",
]
funnel_values = [total_contacts, icp_contacts, icp_engaged, icp_3plus, icp_commented]

fig_funnel = funnel_chart(
    stages=funnel_stages,
    values=funnel_values,
    title="ICP Engagement Funnel",
)
chart_section(
    fig_funnel,
    caption=f"From {total_contacts} contacts → {icp_contacts} ICP → "
    f"{icp_engaged} engaged → {icp_3plus} with 3+ engagements → {icp_commented} commented.",
)

# ---------------------------------------------------------------------------
# ICP % over time
# ---------------------------------------------------------------------------
st.subheader("ICP Engagement Share Over Time")

if not enriched.empty:
    weekly_all = (
        enriched.groupby("week")
        .agg(
            total=("reactionType", "count"),
            icp_total=("is_icp", "sum"),
        )
        .reset_index()
    )
    weekly_all["icp_pct"] = (weekly_all["icp_total"] / weekly_all["total"] * 100).round(1)
    weekly_all = weekly_all.sort_values("week")

    fig_pct = line_chart(
        weekly_all,
        x="week",
        y="icp_pct",
        title="ICP % of Weekly Engagements",
    )
    chart_section(fig_pct, caption="Percentage of each week's engagements from ICP contacts.")

# ---------------------------------------------------------------------------
# ICP engagers detail table
# ---------------------------------------------------------------------------
st.subheader("ICP Engager Details")

if not icp_engagers.empty:
    icp_detail = icp_engagers[
        ["full_name", "title", "company", "country",
         "total_engagements", "likes", "comments", "unique_posts",
         "first_engagement", "last_engagement", "icp_tier"]
    ].copy()
    icp_detail["first_engagement"] = icp_detail["first_engagement"].dt.strftime("%Y-%m-%d")
    icp_detail["last_engagement"] = icp_detail["last_engagement"].dt.strftime("%Y-%m-%d")
    icp_detail.columns = [
        "Name", "Title", "Company", "Country",
        "Engagements", "Likes", "Comments", "Posts",
        "First Seen", "Last Active", "ICP Tier",
    ]
    styled_table(icp_detail, height=500)

# ---------------------------------------------------------------------------
# Engaged but not in contacts
# ---------------------------------------------------------------------------
st.subheader("Engaged but Not in Contacts")
st.caption(
    "People who engaged with posts but aren't in the contacts database — "
    "potential new connections to pursue."
)

unknown_engagers = engager_summary[engager_summary["icp_tier"] == "Unknown"].copy()
if not unknown_engagers.empty:
    top_unknown = unknown_engagers.head(20)[
        ["profile_url", "total_engagements", "likes", "comments", "unique_posts", "last_engagement"]
    ].copy()
    top_unknown["last_engagement"] = top_unknown["last_engagement"].dt.strftime("%Y-%m-%d")
    top_unknown.columns = [
        "Profile URL", "Engagements", "Likes", "Comments", "Posts", "Last Active"
    ]
    styled_table(top_unknown, link_columns=["Profile URL"])
else:
    st.info("All engagers are in the contacts database.")

source_footer(
    source="Engagement + Contacts enrichment data",
    last_updated="2026-02-09",
    notes="Funnel: All contacts → ICP match → engaged (any reaction) → 3+ engagements → commented.",
)
