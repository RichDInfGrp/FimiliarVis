"""Page 7: ICP Composition — by region, industry, size + demographics."""

import pandas as pd
import streamlit as st

st.set_page_config(page_title="ICP Composition", page_icon="🏢", layout="wide")

import src.theme  # noqa: F401, E402

from src.auth import page_guard, render_profile_sidebar  # noqa: E402
from src.data.nicole_data import get_all_data  # noqa: E402
from src.viz.charts import horizontal_bar  # noqa: E402
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
engager_summary = data["engager_summary"]
demographics = data["worksheet"]["demographics"]

icp_contacts = contacts[contacts["is_icp"]].copy()

# ---------------------------------------------------------------------------
# KPIs
# ---------------------------------------------------------------------------
page_header(
    "ICP Composition",
    "Who are the Ideal Customer Profile contacts? Breakdown by region, industry, company size, "
    "and comparison with LinkedIn audience demographics.",
)

n_icp = len(icp_contacts)
n_countries = icp_contacts["Country person"].dropna().nunique()
n_industries = icp_contacts["Company Industry"].dropna().nunique()
n_companies = icp_contacts["Company Name Test"].dropna().nunique()

kpi_row([
    {"label": "ICP Contacts", "value": str(n_icp)},
    {"label": "Countries", "value": str(n_countries)},
    {"label": "Industries", "value": str(n_industries)},
    {"label": "Companies", "value": str(n_companies)},
])

# ---------------------------------------------------------------------------
# ICP by region
# ---------------------------------------------------------------------------
left, right = st.columns(2)

with left:
    st.subheader("ICP by Region")
    region_counts = (
        icp_contacts["Country person"]
        .dropna()
        .value_counts()
        .reset_index()
    )
    region_counts.columns = ["Country", "Count"]
    if not region_counts.empty:
        fig_region = horizontal_bar(region_counts, x="Count", y="Country", title="ICP Contacts by Country")
        chart_section(fig_region)

with right:
    st.subheader("ICP by Industry")
    industry_counts = (
        icp_contacts["Company Industry"]
        .dropna()
        .value_counts()
        .reset_index()
    )
    industry_counts.columns = ["Industry", "Count"]
    if not industry_counts.empty:
        fig_ind = horizontal_bar(industry_counts, x="Count", y="Industry", title="ICP Contacts by Industry")
        chart_section(fig_ind)

# ---------------------------------------------------------------------------
# ICP by company size
# ---------------------------------------------------------------------------
st.subheader("ICP by Company Size")

size_counts = (
    icp_contacts["Size"]
    .dropna()
    .value_counts()
    .reset_index()
)
size_counts.columns = ["Size", "Count"]
if not size_counts.empty:
    fig_size = horizontal_bar(size_counts, x="Count", y="Size", title="ICP Contacts by Company Size")
    chart_section(fig_size)

# ---------------------------------------------------------------------------
# Top ICP contacts table
# ---------------------------------------------------------------------------
st.subheader("ICP Contacts Detail")

icp_display = icp_contacts[
    ["full_name", "Title Test", "Company Name Test", "Country person",
     "Company Industry", "Size", "icp_tier", "profile_url"]
].copy()
icp_display.columns = [
    "Name", "Title", "Company", "Country", "Industry", "Size", "ICP Tier", "Profile"
]
styled_table(icp_display, link_columns=["Profile"])

# ---------------------------------------------------------------------------
# LinkedIn audience demographics
# ---------------------------------------------------------------------------
st.subheader("LinkedIn Audience Demographics")
st.caption("From Nicole's LinkedIn analytics — broader audience composition.")

if not demographics.empty:
    demo_categories = demographics["Top Demographics"].unique()
    tabs = st.tabs(list(demo_categories))

    for tab, cat in zip(tabs, demo_categories):
        with tab:
            cat_df = demographics[demographics["Top Demographics"] == cat].copy()
            cat_df["Percentage"] = (cat_df["Percentage"].astype(float) * 100).round(1)
            cat_df = cat_df[["Value", "Percentage"]].rename(
                columns={"Percentage": "% of Audience"}
            )
            fig_demo = horizontal_bar(
                cat_df,
                x="% of Audience",
                y="Value",
                title=f"Audience by {cat}",
                text_format=".1f",
            )
            chart_section(fig_demo)

source_footer(
    source="Contacts enrichment + WorkSheet DEMOGRAPHICS",
    last_updated="2026-02-09",
    notes="ICP = Broad | Global | Specific match. Demographics from LinkedIn audience analytics.",
)
