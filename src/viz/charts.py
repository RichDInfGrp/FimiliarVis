"""Fimiliar Vis — Reusable chart builder functions.

Each function returns a go.Figure (Plotly) styled with the fimiliar template.
Import src.theme before calling any function (done automatically via app.py).
"""

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

from src.config import (
    COLORS_CATEGORICAL,
    COLORS_SEQUENTIAL,
    COLOR_ACCENT,
    COLOR_POSITIVE,
    COLOR_NEGATIVE,
    TEXT_SECONDARY,
)


def horizontal_bar(
    df: pd.DataFrame,
    x: str,
    y: str,
    title: str = "",
    text_format: str = ",.0f",
    color: str | None = None,
) -> go.Figure:
    """Sorted horizontal bar chart with direct labels.

    Args:
        df: DataFrame with at least columns x and y.
        x: Numeric column (bar length).
        y: Categorical column (bar labels).
        title: Chart title.
        text_format: d3-format string for bar labels.
        color: Optional column for color encoding.
    """
    sorted_df = df.sort_values(x, ascending=True)
    fig = px.bar(
        sorted_df,
        x=x,
        y=y,
        orientation="h",
        title=title,
        color=color,
        color_discrete_sequence=COLORS_CATEGORICAL,
        template="fimiliar",
    )
    fig.update_traces(
        texttemplate=f"%{{x:{text_format}}}",
        textposition="outside",
    )
    if not color:
        fig.update_traces(marker_color=COLOR_ACCENT)
    fig.update_layout(showlegend=bool(color), yaxis_title="", xaxis_title="")
    return fig


def line_chart(
    df: pd.DataFrame,
    x: str,
    y: str | list[str],
    title: str = "",
    color: str | None = None,
) -> go.Figure:
    """Line chart for time series. Max 5 series recommended.

    Args:
        df: DataFrame.
        x: Column for x-axis (typically a date).
        y: Column(s) for y-axis values.
        title: Chart title.
        color: Optional column for color grouping (long-format data).
    """
    if isinstance(y, list):
        fig = go.Figure()
        for i, col in enumerate(y):
            fig.add_trace(go.Scatter(
                x=df[x],
                y=df[col],
                mode="lines",
                name=col,
                line=dict(color=COLORS_CATEGORICAL[i % len(COLORS_CATEGORICAL)], width=2),
            ))
        fig.update_layout(title=title, template="fimiliar")
    else:
        fig = px.line(
            df,
            x=x,
            y=y,
            color=color,
            title=title,
            color_discrete_sequence=COLORS_CATEGORICAL,
            template="fimiliar",
        )
    fig.update_traces(line_width=2)
    return fig


def scatter(
    df: pd.DataFrame,
    x: str,
    y: str,
    title: str = "",
    size: str | None = None,
    color: str | None = None,
    trendline: str | None = "ols",
) -> go.Figure:
    """Scatter plot with optional trendline and size encoding.

    Args:
        df: DataFrame.
        x: Numeric column for x-axis.
        y: Numeric column for y-axis.
        title: Chart title.
        size: Optional column for point size (3rd dimension).
        color: Optional column for color grouping.
        trendline: Trendline type ("ols", "lowess", or None).
    """
    fig = px.scatter(
        df,
        x=x,
        y=y,
        size=size,
        color=color,
        trendline=trendline,
        title=title,
        color_discrete_sequence=COLORS_CATEGORICAL,
        template="fimiliar",
    )
    fig.update_traces(marker=dict(opacity=0.7))
    return fig


def area_chart(
    df: pd.DataFrame,
    x: str,
    y: str,
    color: str | None = None,
    title: str = "",
    normalize: bool = False,
) -> go.Figure:
    """Stacked area chart for composition over time.

    Args:
        df: DataFrame in long format.
        x: Column for x-axis (typically date).
        y: Numeric column for y-axis.
        color: Column for stacking groups.
        title: Chart title.
        normalize: If True, show as 100% stacked.
    """
    fig = px.area(
        df,
        x=x,
        y=y,
        color=color,
        title=title,
        groupnorm="percent" if normalize else None,
        color_discrete_sequence=COLORS_CATEGORICAL,
        template="fimiliar",
    )
    return fig


def histogram(
    df: pd.DataFrame,
    x: str,
    title: str = "",
    nbins: int = 30,
    show_mean: bool = True,
    show_median: bool = True,
) -> go.Figure:
    """Histogram with optional mean/median reference lines.

    Args:
        df: DataFrame.
        x: Numeric column to distribute.
        title: Chart title.
        nbins: Number of bins.
        show_mean: Show vertical mean line.
        show_median: Show vertical median line.
    """
    fig = px.histogram(
        df,
        x=x,
        nbins=nbins,
        title=title,
        color_discrete_sequence=[COLOR_ACCENT],
        template="fimiliar",
    )
    if show_mean:
        mean_val = df[x].mean()
        fig.add_vline(
            x=mean_val,
            line_dash="dash",
            line_color=TEXT_SECONDARY,
            annotation_text=f"Mean: {mean_val:,.1f}",
            annotation_font_size=11,
        )
    if show_median:
        median_val = df[x].median()
        fig.add_vline(
            x=median_val,
            line_dash="dot",
            line_color=COLORS_CATEGORICAL[2],
            annotation_text=f"Median: {median_val:,.1f}",
            annotation_font_size=11,
        )
    return fig


def donut(
    df: pd.DataFrame,
    values: str,
    names: str,
    title: str = "",
) -> go.Figure:
    """Donut chart — use only for 2-3 categories maximum.

    Args:
        df: DataFrame.
        values: Numeric column for slice sizes.
        names: Categorical column for slice labels.
        title: Chart title.
    """
    fig = px.pie(
        df,
        values=values,
        names=names,
        title=title,
        hole=0.55,
        color_discrete_sequence=COLORS_CATEGORICAL,
        template="fimiliar",
    )
    fig.update_traces(
        textposition="inside",
        textinfo="percent+label",
    )
    return fig


def combo_chart(
    df: pd.DataFrame,
    x: str,
    bar_y: str | list[str],
    line_y: str | list[str],
    title: str = "",
    bar_names: list[str] | None = None,
    line_names: list[str] | None = None,
) -> go.Figure:
    """Stacked subplots: bars on top, lines on bottom, shared x-axis.

    Avoids dual y-axes per CLAUDE.md design rules.
    """
    bar_cols = [bar_y] if isinstance(bar_y, str) else bar_y
    line_cols = [line_y] if isinstance(line_y, str) else line_y
    b_names = bar_names or bar_cols
    l_names = line_names or line_cols

    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.08,
        row_heights=[0.55, 0.45],
    )
    for i, (col, name) in enumerate(zip(bar_cols, b_names)):
        fig.add_trace(
            go.Bar(
                x=df[x],
                y=df[col],
                name=name,
                marker_color=COLORS_CATEGORICAL[i % len(COLORS_CATEGORICAL)],
            ),
            row=1,
            col=1,
        )
    for i, (col, name) in enumerate(zip(line_cols, l_names)):
        fig.add_trace(
            go.Scatter(
                x=df[x],
                y=df[col],
                mode="lines",
                name=name,
                line=dict(
                    color=COLORS_CATEGORICAL[
                        (i + len(bar_cols)) % len(COLORS_CATEGORICAL)
                    ],
                    width=2,
                ),
            ),
            row=2,
            col=1,
        )
    fig.update_layout(title=title, template="fimiliar", barmode="group")
    return fig


def grouped_bar(
    df: pd.DataFrame,
    x: str,
    y: str,
    color: str,
    title: str = "",
    text_format: str = ",.0f",
) -> go.Figure:
    """Grouped bar chart using px.bar with barmode='group'."""
    fig = px.bar(
        df,
        x=x,
        y=y,
        color=color,
        barmode="group",
        title=title,
        color_discrete_sequence=COLORS_CATEGORICAL,
        template="fimiliar",
    )
    fig.update_traces(texttemplate=f"%{{y:{text_format}}}", textposition="outside")
    return fig


def waterfall_chart(
    categories: list[str],
    values: list[float],
    title: str = "",
    measure: list[str] | None = None,
) -> go.Figure:
    """Waterfall chart with brand colors for ICP growth decomposition."""
    if measure is None:
        measure = ["relative"] * len(values)
    fig = go.Figure(
        go.Waterfall(
            x=categories,
            y=values,
            measure=measure,
            increasing_marker_color=COLOR_POSITIVE,
            decreasing_marker_color=COLOR_NEGATIVE,
            totals_marker_color=COLORS_CATEGORICAL[3],
            textposition="outside",
            texttemplate="%{y:+.0f}",
        )
    )
    fig.update_layout(title=title, template="fimiliar", showlegend=False)
    return fig


def funnel_chart(
    stages: list[str],
    values: list[float],
    title: str = "",
) -> go.Figure:
    """Funnel chart with sequential palette."""
    fig = go.Figure(
        go.Funnel(
            y=stages,
            x=values,
            textinfo="value+percent initial",
            marker_color=COLORS_SEQUENTIAL[: len(stages)],
        )
    )
    fig.update_layout(title=title, template="fimiliar")
    return fig
