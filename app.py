"""Fimiliar Vis — Nicole Bello LinkedIn Performance Dashboard.

Entry point: login gate → home page with summary KPIs and navigation.
"""

import streamlit as st

st.set_page_config(
    page_title="Fimiliar Vis — Nicole Bello",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Register themes on import
import src.theme  # noqa: F401, E402

from src.auth import init_session_state, render_login_form, render_profile_sidebar  # noqa: E402
from src.data.nicole_data import get_all_data  # noqa: E402
from src.viz.components import kpi_row, page_header, source_footer  # noqa: E402

# ---------------------------------------------------------------------------
# Session init
# ---------------------------------------------------------------------------
init_session_state()

if not st.session_state.get("authenticated", False):
    render_login_form()
    st.stop()

# ---------------------------------------------------------------------------
# Authenticated: Home page
# ---------------------------------------------------------------------------
render_profile_sidebar()

data = get_all_data()
discovery = data["worksheet"]["discovery"]
followers = data["worksheet"]["followers"]
contacts = data["contacts"]
posts = data["posts"]
engager_summary = data["engager_summary"]

# Extract discovery KPIs
impressions_total = discovery.iloc[0, 1]
members_reached = discovery.iloc[1, 1]

page_header(
    "◆ Fimiliar Vis",
    "LinkedIn Performance Dashboard — tracking content impact, audience growth, "
    "and ICP engagement for Nicole Bello.",
)

# Summary KPIs
total_posts = len(posts)
total_engagements = int(posts["Engagements"].sum())
icp_contacts = int(contacts["is_icp"].sum())
latest_followers = int(followers["Total Followers"].iloc[-1]) if not followers.empty else 0

kpi_row([
    {"label": "Impressions", "value": f"{impressions_total:,}"},
    {"label": "Members Reached", "value": f"{members_reached:,}"},
    {"label": "Total Posts", "value": str(total_posts)},
    {"label": "Total Engagements", "value": f"{total_engagements:,}"},
])

st.markdown("")

kpi_row([
    {"label": "ICP Contacts", "value": str(icp_contacts)},
    {"label": "Unique Engagers", "value": f"{len(engager_summary):,}"},
    {"label": "Followers", "value": f"{latest_followers:,}"},
    {"label": "Avg Engagement Rate", "value": f"{posts['Engagement Rate (%)'].mean():.2f}%"},
])

st.divider()

# Navigation
st.subheader("Dashboard Pages")

col1, col2 = st.columns(2)

with col1:
    st.page_link("pages/1_Content_Performance.py", label="📊 Content Performance", icon="📊")
    st.page_link("pages/2_Audience_Growth.py", label="📈 Audience Growth", icon="📈")
    st.page_link("pages/3_Audience_Quality.py", label="🎯 Audience Quality", icon="🎯")
    st.page_link("pages/4_Engagement_Targets.py", label="🔥 Engagement Targets", icon="🔥")

with col2:
    st.page_link("pages/5_Network_Growth.py", label="🌐 Network Growth", icon="🌐")
    st.page_link("pages/6_Acquisition_Velocity.py", label="⚡ Acquisition Velocity", icon="⚡")
    st.page_link("pages/7_ICP_Composition.py", label="🏢 ICP Composition", icon="🏢")
    st.page_link("pages/8_ICP_Engagement.py", label="🔬 ICP Engagement", icon="🔬")

source_footer(
    source="LinkedIn data via Fimiliar platform",
    last_updated="2026-02-09",
    notes="Service period: 17 Jan 2026 – 9 Feb 2026. Data covers 48 posts, 189 contacts, 2,792 engagement records.",
)
