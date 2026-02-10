"""Fimiliar Vis — Common data transforms and aggregation helpers."""

from typing import Literal

import pandas as pd
import streamlit as st


@st.cache_data
def parse_dates(df: pd.DataFrame, column: str, fmt: str | None = None) -> pd.DataFrame:
    """Convert a column to datetime, returning a copy.

    Args:
        df: Source DataFrame.
        column: Column name to parse.
        fmt: Optional strftime format string.
    """
    out = df.copy()
    out[column] = pd.to_datetime(out[column], format=fmt)
    return out


@st.cache_data
def aggregate(
    df: pd.DataFrame,
    group_by: str | list[str],
    agg_column: str,
    func: Literal["sum", "mean", "median", "count", "min", "max"] = "sum",
) -> pd.DataFrame:
    """Group and aggregate a DataFrame.

    Args:
        df: Source DataFrame.
        group_by: Column(s) to group on.
        agg_column: Column to aggregate.
        func: Aggregation function name.
    """
    return df.groupby(group_by, as_index=False)[agg_column].agg(func)


@st.cache_data
def pivot_for_chart(
    df: pd.DataFrame,
    index: str,
    columns: str,
    values: str,
    fill_value: float = 0,
) -> pd.DataFrame:
    """Pivot a long DataFrame to wide format suitable for multi-series charts.

    Args:
        df: Source DataFrame in long format.
        index: Column for the new index (e.g. date).
        columns: Column whose unique values become new columns (e.g. category).
        values: Column with the numeric values.
        fill_value: Fill missing cells with this value.
    """
    return df.pivot_table(
        index=index, columns=columns, values=values, fill_value=fill_value
    ).reset_index()


@st.cache_data
def filter_df(df: pd.DataFrame, column: str, values: list) -> pd.DataFrame:
    """Filter a DataFrame to rows where column is in values."""
    return df[df[column].isin(values)]
