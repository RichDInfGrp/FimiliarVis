"""Fimiliar Vis — Reusable Streamlit layout components."""

from typing import Any

import pandas as pd
import streamlit as st

from src.config import PLOTLY_CONFIG, COLOR_ACCENT


def kpi_row(metrics: list[dict[str, Any]]) -> None:
    """Render a row of KPI metric cards.

    Args:
        metrics: List of dicts with keys "label", "value", and optional "delta".
                 Example: [{"label": "Revenue", "value": "$1.2M", "delta": "+12%"}]
    """
    cols = st.columns(len(metrics))
    for col, m in zip(cols, metrics):
        col.metric(
            label=m["label"],
            value=m["value"],
            delta=m.get("delta"),
        )


def chart_section(fig, caption: str = "", key: str | None = None) -> None:
    """Display a Plotly chart with an accessibility caption below it.

    Args:
        fig: A plotly Figure object.
        caption: Descriptive text for screen readers and context.
        key: Optional unique Streamlit key.
    """
    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG, key=key)
    if caption:
        st.caption(caption)


def source_footer(
    source: str = "",
    last_updated: str = "",
    notes: str = "",
) -> None:
    """Render a collapsible data-source footer.

    Args:
        source: Data source attribution.
        last_updated: Date string for freshness.
        notes: Methodology or caveats.
    """
    with st.expander("About this data"):
        parts = []
        if source:
            parts.append(f"**Source:** {source}")
        if last_updated:
            parts.append(f"**Last updated:** {last_updated}")
        if notes:
            parts.append(f"**Notes:** {notes}")
        st.markdown(" | ".join(parts) if parts else "No metadata provided.")


def page_header(title: str, caption: str = "") -> None:
    """Standardized page title with narrative caption and divider."""
    st.title(title)
    if caption:
        st.caption(caption)
    st.divider()


def comparison_card(
    label: str,
    before: float | int,
    after: float | int,
    fmt: str = ",.0f",
    invert: bool = False,
) -> None:
    """Before/after comparison card with delta.

    Args:
        label: Metric name.
        before: Value before service.
        after: Value after service.
        fmt: Format string for display.
        invert: If True, a decrease is positive (e.g. cost).
    """
    delta = after - before
    pct = (delta / before * 100) if before else 0
    direction = "inverse" if invert else "normal"
    st.metric(
        label=label,
        value=f"{after:{fmt}}",
        delta=f"{delta:+{fmt}} ({pct:+.0f}%)",
        delta_color=direction,
        help=f"Before: {before:{fmt}}",
    )


def styled_table(
    df: pd.DataFrame,
    link_columns: list[str] | None = None,
    height: int = 400,
) -> None:
    """Display a styled, sortable dataframe.

    Args:
        df: Data to display.
        link_columns: Columns containing URLs to render as links.
        height: Table height in pixels.
    """
    column_config = {}
    if link_columns:
        for col in link_columns:
            if col in df.columns:
                column_config[col] = st.column_config.LinkColumn(col, display_text="View")
    st.dataframe(
        df,
        column_config=column_config,
        use_container_width=True,
        height=height,
        hide_index=True,
    )
