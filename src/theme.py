"""Fimiliar Vis — Plotly template and Altair theme registration.

Import this module to activate the 'fimiliar' theme for both libraries.
The Plotly template is set as default on import. Altair theme must be
enabled with alt.themes.enable("fimiliar").
"""

import altair as alt
import plotly.graph_objects as go
import plotly.io as pio

from src.config import (
    COLORS_CATEGORICAL,
    FONT_FAMILY,
    GRIDLINE_COLOR,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
)

# ---------------------------------------------------------------------------
# Plotly template
# ---------------------------------------------------------------------------

_fimiliar_plotly = go.layout.Template(
    layout=go.Layout(
        font=dict(family=FONT_FAMILY, size=12, color=TEXT_PRIMARY),
        title=dict(
            font=dict(size=16, color=TEXT_PRIMARY),
            x=0,
            xanchor="left",
            pad=dict(l=0),
        ),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        colorway=COLORS_CATEGORICAL,
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor="#FFFFFF",
            font_size=12,
            font_family=FONT_FAMILY,
        ),
        margin=dict(l=48, r=24, t=64, b=48),
        xaxis=dict(
            showgrid=False,
            linecolor=GRIDLINE_COLOR,
            tickfont=dict(size=11, color=TEXT_SECONDARY),
            title_font=dict(size=12, color=TEXT_SECONDARY),
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor=GRIDLINE_COLOR,
            gridwidth=1,
            linecolor="rgba(0,0,0,0)",
            tickfont=dict(size=11, color=TEXT_SECONDARY),
            title_font=dict(size=12, color=TEXT_SECONDARY),
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
            font=dict(size=11, color=TEXT_SECONDARY),
        ),
    )
)

pio.templates["fimiliar"] = _fimiliar_plotly
pio.templates.default = "fimiliar"

# ---------------------------------------------------------------------------
# Altair theme
# ---------------------------------------------------------------------------

_font_name = FONT_FAMILY.split(",")[0].strip()


def _fimiliar_altair() -> dict:
    """Return the Fimiliar Altair theme config."""
    return {
        "config": {
            "background": "transparent",
            "font": _font_name,
            "title": {"fontSize": 16, "font": _font_name, "color": TEXT_PRIMARY},
            "axis": {
                "labelFontSize": 11,
                "titleFontSize": 12,
                "labelColor": TEXT_SECONDARY,
                "titleColor": TEXT_SECONDARY,
                "gridColor": GRIDLINE_COLOR,
                "domainColor": GRIDLINE_COLOR,
                "tickColor": GRIDLINE_COLOR,
            },
            "view": {"strokeWidth": 0},
            "range": {"category": COLORS_CATEGORICAL},
            "legend": {
                "orient": "top",
                "labelFontSize": 11,
                "titleFontSize": 12,
                "labelColor": TEXT_SECONDARY,
            },
        }
    }


alt.themes.register("fimiliar", _fimiliar_altair)
alt.themes.enable("fimiliar")
