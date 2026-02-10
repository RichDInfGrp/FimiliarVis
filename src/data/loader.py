"""Fimiliar Vis — Cached data loading utilities.

All functions use @st.cache_data so Streamlit only reads files once.
"""

from pathlib import Path

import pandas as pd
import streamlit as st

_DATA_DIR = Path(__file__).resolve().parents[2] / "data"


@st.cache_data
def load_csv(filename: str, subdir: str = "raw", **kwargs) -> pd.DataFrame:
    """Load a CSV file from data/<subdir>/<filename>.

    Args:
        filename: Name of the CSV file (e.g. "sales.csv").
        subdir: Subdirectory under data/ — "raw" or "processed".
        **kwargs: Extra arguments forwarded to pd.read_csv.
    """
    path = _DATA_DIR / subdir / filename
    return pd.read_csv(path, **kwargs)


@st.cache_data
def load_json(filename: str, subdir: str = "raw", **kwargs) -> pd.DataFrame:
    """Load a JSON file from data/<subdir>/<filename>."""
    path = _DATA_DIR / subdir / filename
    return pd.read_json(path, **kwargs)


@st.cache_data
def load_parquet(filename: str, subdir: str = "raw", **kwargs) -> pd.DataFrame:
    """Load a Parquet file from data/<subdir>/<filename>."""
    path = _DATA_DIR / subdir / filename
    return pd.read_parquet(path, **kwargs)


@st.cache_data
def load_excel(filename: str, subdir: str = "raw", **kwargs) -> pd.DataFrame:
    """Load an Excel file from data/<subdir>/<filename>."""
    path = _DATA_DIR / subdir / filename
    return pd.read_excel(path, **kwargs)


@st.cache_data
def find_and_load_excel(
    prefix: str, subdir: str = "raw", sheet_name: str | int = 0, **kwargs
) -> pd.DataFrame:
    """Find an Excel file by filename prefix and load it.

    Uses glob to match files starting with *prefix* in ``data/<subdir>/``.
    """
    search_dir = _DATA_DIR / subdir
    matches = sorted(search_dir.glob(f"{prefix}*.xlsx"))
    if not matches:
        raise FileNotFoundError(
            f"No .xlsx file matching prefix '{prefix}' in {search_dir}"
        )
    return pd.read_excel(matches[0], sheet_name=sheet_name, **kwargs)
