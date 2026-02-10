"""Fimiliar Vis — Authentication and user profile management."""

import streamlit as st

from src.config import DEFAULT_USER_PROFILE


def init_session_state() -> None:
    """Initialize session state with defaults."""
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
    if "user_profile" not in st.session_state:
        st.session_state["user_profile"] = dict(DEFAULT_USER_PROFILE)


def check_login(username: str, password: str) -> bool:
    """Validate credentials against Streamlit secrets."""
    try:
        valid_user = st.secrets["credentials"]["username"]
        valid_pass = st.secrets["credentials"]["password"]
        return username == valid_user and password == valid_pass
    except (KeyError, FileNotFoundError):
        return False


def render_login_form() -> None:
    """Render a branded login page."""
    st.markdown(
        """
        <div style="text-align:center; padding:3rem 0 1rem;">
            <h1 style="color:#0e0e0f; font-size:2.2rem; margin-bottom:0.2rem;">
                ◆ Fimiliar Vis
            </h1>
            <p style="color:#5b5b5b; font-size:1rem;">
                LinkedIn Performance Dashboard
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        with st.form("login_form", border=True):
            st.subheader("Sign In")
            username = st.text_input("Username", placeholder="nicole.bello")
            password = st.text_input("Password", type="password", placeholder="Enter password")
            submitted = st.form_submit_button("Sign In", use_container_width=True, type="primary")

            if submitted:
                if check_login(username, password):
                    st.session_state["authenticated"] = True
                    st.rerun()
                else:
                    st.error("Invalid username or password.")


def render_profile_sidebar() -> None:
    """Render user profile in the sidebar with photo and editable fields."""
    profile = st.session_state.get("user_profile", DEFAULT_USER_PROFILE)

    with st.sidebar:
        # Profile photo — circular via HTML
        photo_url = profile.get("photo_url", "")
        if photo_url:
            st.markdown(
                f"""
                <div style="text-align:center; margin-bottom:0.5rem;">
                    <img src="{photo_url}"
                         style="width:80px; height:80px; border-radius:50%;
                                object-fit:cover; border:3px solid #93f3db;"
                         alt="Profile photo"
                         onerror="this.style.display='none'">
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown(
            f"**{profile.get('name', 'User')}**\n\n"
            f"{profile.get('title', '')}\n\n"
            f"📍 {profile.get('location', '')}"
        )

        linkedin_url = profile.get("linkedin_url", "")
        if linkedin_url:
            st.markdown(f"[View LinkedIn Profile]({linkedin_url})")

        with st.expander("Edit Profile"):
            new_name = st.text_input("Name", value=profile.get("name", ""), key="edit_name")
            new_title = st.text_input("Title", value=profile.get("title", ""), key="edit_title")
            new_company = st.text_input("Company", value=profile.get("company", ""), key="edit_company")
            new_location = st.text_input("Location", value=profile.get("location", ""), key="edit_location")
            new_photo = st.text_input("Photo URL", value=profile.get("photo_url", ""), key="edit_photo")

            if st.button("Save Changes", key="save_profile"):
                st.session_state["user_profile"] = {
                    **profile,
                    "name": new_name,
                    "title": new_title,
                    "company": new_company,
                    "location": new_location,
                    "photo_url": new_photo,
                }
                st.rerun()

        st.divider()

        if st.button("Sign Out", key="sign_out"):
            st.session_state["authenticated"] = False
            st.rerun()


def page_guard() -> None:
    """Check authentication and stop page rendering if not logged in."""
    if not st.session_state.get("authenticated", False):
        st.warning("Please sign in from the home page.")
        st.stop()
