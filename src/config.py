"""Fimiliar Vis — Brand tokens and design constants.

Single source of truth for colors, fonts, and layout values.
Import from here everywhere — never hardcode hex values elsewhere.
"""

# --- Brand Colors ---
COLOR_MAIN = "#0e0e0f"
COLOR_ACCENT = "#93f3db"
COLOR_SECONDARY_DARK = "#5b5b5b"
COLOR_SECONDARY_ACCENT = "#c8f9eb"
COLOR_LIGHT = "#F5F5F5"
COLOR_WHITE = "#FFFFFF"

# --- Chart Palettes ---
COLORS_CATEGORICAL = ["#93f3db", "#5b5b5b", "#66d9c2", "#0e0e0f", "#a0a0a0"]
COLORS_SEQUENTIAL = ["#c8f9eb", "#93f3db", "#4ecab0", "#2a9d8f", "#1a6b5a"]
COLORS_DIVERGING = ["#e07a5f", "#F5F5F5", "#93f3db"]

# --- Semantic Colors ---
COLOR_POSITIVE = "#93f3db"
COLOR_NEGATIVE = "#e07a5f"
COLOR_NEUTRAL = "#5b5b5b"
COLOR_HIGHLIGHT = "#c8f9eb"

# --- Typography ---
FONT_FAMILY = "Inter, -apple-system, BlinkMacSystemFont, sans-serif"

# --- Layout ---
BG_PAGE = "#F5F5F5"
BG_CARD = "#FFFFFF"
TEXT_PRIMARY = "#0e0e0f"
TEXT_SECONDARY = "#5b5b5b"
GRIDLINE_COLOR = "#E8E8E8"

# --- Plotly chart config (hide toolbar by default) ---
PLOTLY_CONFIG = {"displayModeBar": False}

# --- User Profile Defaults ---
DEFAULT_USER_PROFILE = {
    "name": "Nicole Bello",
    "title": "Group Vice President, EMEA, Dayforce",
    "location": "London, England, United Kingdom",
    "company": "Dayforce",
    "linkedin_url": "https://www.linkedin.com/in/nicolebello1/",
    "photo_url": (
        "https://media.licdn.com/dms/image/v2/D4E03AQE2Z0fDBCK_fQ/"
        "profile-displayphoto-shrink_800_800/profile-displayphoto-shrink_800_800/"
        "0/1715379076958?e=1772064000&v=beta&"
        "t=0Gdk3zA1oOXvGTsfBjPYyqq1ZxamBHD9JzeS88Nxf0c"
    ),
}

# --- Service Date ---
SERVICE_START_DATE = "2026-01-17"

# --- Data File Prefixes (for glob matching timestamped filenames) ---
DATA_FILE_PREFIXES = {
    "contacts": "Contacts-Enrich-Nicole",
    "engagement": "Engagement-Nicole",
    "daily_update": "Nicole's-Daily-Update",
    "worksheet": "WorkSheet_Nicole",
}
