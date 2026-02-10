# Fimiliar Vis — Claude Instructions

This workspace produces **on-brand, Information-is-Beautiful-quality data visualizations** as Streamlit apps.
Drop a visualization brief in `briefs/`; Claude builds a complete, polished Streamlit application.

---

## Workflow

1. **Read the brief** — any `.md` or `.txt` file in `briefs/`.
2. **State the questions** the visualization must answer in a comment at the top of `app.py`.
3. **Determine data needs.** Use files in `data/` or generate realistic synthetic data. Never use random uniform noise — model real-world distributions, seasonality, and outliers.
4. **Select chart types** using the Chart Selection Guide below.
5. **Build the app** following every convention in this file. Import from `src/` — never inline chart logic in `app.py`.
6. **Run the Quality Checklist** (bottom of this file) before declaring done.

---

## McCandless Framework (Every Visualization, No Exceptions)

| Element | Requirement |
|---------|-------------|
| **Information** | Accurate, cited data. State the source. Label synthetic data. |
| **Function** | Answers a specific question. The user learns something new. |
| **Visual Form** | Clean, elegant, distinctive. Would IiB publish this? |
| **Story** | Narrative arc: context → insight → implication. Use annotations. |

Add a narrative subtitle under every page title:
```python
st.caption("Why this matters: ...")
```

---

## Brand Design System

### Colors

| Token | Hex | Usage |
|-------|-----|-------|
| Main | `#0e0e0f` | Primary text, chart labels, strong emphasis |
| Accent | `#93f3db` | Primary data series, highlights, interactive elements |
| Secondary dark | `#5b5b5b` | Secondary text, gridlines, supporting series |
| Secondary accent | `#c8f9eb` | Fills, area backgrounds, light emphasis |
| Light | `#F5F5F5` | Page background, card backgrounds |
| White | `#FFFFFF` | Chart plot area, containers |

**Categorical palette (use in order, max 5 per chart):**
`#93f3db` · `#5b5b5b` · `#66d9c2` · `#0e0e0f` · `#a0a0a0`

**Sequential (magnitude):**
`#c8f9eb` → `#93f3db` → `#4ecab0` → `#2a9d8f` → `#1a6b5a`

**Diverging (above/below midpoint):**
`#e07a5f` (warm) → `#F5F5F5` (neutral) → `#93f3db` (cool)

**Semantic:**
| Meaning | Hex |
|---------|-----|
| Positive | `#93f3db` |
| Negative | `#e07a5f` |
| Neutral | `#5b5b5b` |
| Highlight | `#c8f9eb` |

### Typography

**Font family:** Inter (all weights 100–900 available via Google Fonts).

| Role | Size | Weight |
|------|------|--------|
| Page title | 28px | 700 |
| Section heading | 20px | 600 |
| Chart title | 16px | 600 |
| Body text | 14px | 400 |
| Axis labels | 12px | 400 |
| Annotations | 11px | 400 |

### Layout

- Page background: `#F5F5F5`
- Card/container background: `#FFFFFF`
- Primary text: `#0e0e0f`
- Secondary text: `#5b5b5b`
- Gridlines/borders: `#E8E8E8`
- Always use `st.set_page_config(layout="wide")`
- Generous whitespace. Use `st.divider()` between sections.
- Max 3 columns in any row. Never nest columns inside columns.

---

## Project Structure

```
Fimiliar Vis/
├── CLAUDE.md                   # This file — do not modify
├── briefs/                     # Drop visualization briefs here
├── app.py                      # Main Streamlit entry point
├── pages/                      # Additional pages (if multi-page)
├── src/
│   ├── config.py               # Brand tokens (colors, fonts, layout)
│   ├── theme.py                # Plotly template + Altair theme
│   ├── data/
│   │   ├── loader.py           # Cached data loading
│   │   └── processor.py        # Transforms + aggregations
│   └── viz/
│       ├── charts.py           # One function per chart type → go.Figure
│       └── components.py       # Reusable Streamlit layout helpers
├── data/
│   ├── raw/                    # Original data files
│   └── processed/              # Cleaned data
├── .streamlit/config.toml      # Streamlit theme
└── requirements.txt
```

Always create `src/config.py` and `src/theme.py` first. Every other module imports from them.

---

## Chart Selection Guide

| Data Question | Chart Type | Library | Notes |
|---------------|-----------|---------|-------|
| How much? / Ranking? | Horizontal bar | Plotly | Sort descending. Direct-label bars. |
| Change over time? | Line chart | Plotly | Max 5 lines. Annotate key events. |
| Distribution? | Histogram / KDE | Plotly | Show mean/median as vertical lines. |
| Parts of a whole? | Stacked bar / Treemap | Plotly | Donut OK for 2–3 slices. No pie. |
| Relationship between variables? | Scatter | Plotly | Add trendline. Size = 3rd dimension. |
| Composition over time? | Stacked area | Plotly | Use % mode if totals vary. |
| Flow / connections? | Sankey | Plotly | Max 10–15 nodes. |
| Geographic? | Choropleth / Mapbox | Plotly | Sequential palette for magnitude. |
| Compare categories on metrics? | Small multiples | Altair | Facet/repeat. More honest than radar. |
| Key numbers at a glance? | KPI cards | Streamlit | `st.metric()` with delta values. |

### Prohibitions

- **No pie charts.** Use horizontal bar or donut (max 3 slices).
- **No 3D charts.** They distort perception.
- **No dual y-axes.** Use small multiples or normalize.
- **No rainbow color scales.** Use sequential or diverging palettes above.
- **No rotated x-axis labels.** Flip to horizontal bar or abbreviate.
- **No decorative gridlines.** Y-axis grid only, light `#E8E8E8`.
- **No chart borders or boxes.** Charts float on the background.

---

## Plotly Conventions

```python
import plotly.express as px
import plotly.graph_objects as go
from src.theme import *  # registers "fimiliar" template on import

# Always explicit template:
fig = px.bar(df, x="value", y="category", orientation="h",
             color_discrete_sequence=COLORS_CATEGORICAL,
             template="fimiliar")

# Direct labeling over legends:
fig.update_traces(texttemplate="%{x:.1f}", textposition="outside")

# Annotate the key insight:
fig.add_annotation(
    x=value, y=category,
    text="Highest in 5 years",
    showarrow=True, arrowhead=2,
    font=dict(size=11, color="#5b5b5b"),
)

# Display in Streamlit:
st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
```

### Rules
- Always `use_container_width=True`.
- Always `config={"displayModeBar": False}` unless zoom/pan is needed.
- `hovermode="x unified"` for time series.
- Format hover: `hovertemplate="%{y:,.0f}<extra></extra>"`.
- Annotate the single most important insight on every chart.
- Remove legends when direct labels suffice.

---

## Altair Conventions

Use Altair for faceted / small-multiple statistical charts:

```python
import altair as alt
from src.config import COLORS_CATEGORICAL, FONT_FAMILY

# Theme registered in src/theme.py — just enable:
alt.themes.enable("fimiliar")
```

Display with: `st.altair_chart(chart, use_container_width=True)`

---

## Streamlit Layout Patterns

### Page Setup (first lines of every app.py)

```python
import streamlit as st
st.set_page_config(
    page_title="[Title] — Fimiliar Vis",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded",
)
```

### Standard Page Anatomy

```python
# 1. Title block
st.title("Clear, Specific Title")
st.caption("Why this matters: what this data reveals and why it matters.")
st.divider()

# 2. KPI row (3–4 metrics)
c1, c2, c3, c4 = st.columns(4)
c1.metric("Revenue", "$1.2M", "+12%")
c2.metric("Users", "45,231", "-3%")
c3.metric("Conversion", "3.2%", "+0.4%")
c4.metric("Avg Order", "$68", "+$5")
st.divider()

# 3. Filters in sidebar
with st.sidebar:
    st.header("Filters")
    date_range = st.date_input("Date range", value=[start, end])
    category = st.multiselect("Category", options=categories, default=categories)

# 4. Main visualizations in tabs
tab1, tab2 = st.tabs(["Overview", "Deep Dive"])
with tab1:
    left, right = st.columns([2, 1])
    with left:
        st.plotly_chart(main_chart, use_container_width=True, config={"displayModeBar": False})
    with right:
        st.plotly_chart(supporting_chart, use_container_width=True, config={"displayModeBar": False})

# 5. Source footer
with st.expander("About this data"):
    st.markdown("**Source:** ... | **Last updated:** ... | **Notes:** ...")
```

### Rules
- `@st.cache_data` on every data-loading and processing function.
- Sidebar for filters and controls only — never content.
- Use `st.tabs()` for 2–4 distinct views.
- Use `st.expander()` for methodology, data notes, supplementary tables.
- Column ratios: `[2, 1]` or `[1, 1]` — max 3 columns, never nested.
- Every `st.metric()` should include `delta` when time-comparison data exists.
- Display tables with `st.dataframe(df, hide_index=True)`.

---

## Synthetic Data Generation

When no real data is provided:

```python
import numpy as np
import pandas as pd

np.random.seed(42)  # reproducible

# Realistic distributions:
# Revenue → lognormal | Counts → Poisson | Rates → Beta | Time series → trend + seasonality + noise

# Use real-world labels (city names, product categories — not "Category_A")
# Add intentional patterns: one clear outlier, a trend that tells a story, seasonal variation
```

Always add: `st.caption("Note: This visualization uses synthetic data for illustration.")`

---

## Accessibility

- All text meets WCAG AA contrast (4.5:1 normal, 3:1 large).
- Never encode meaning with color alone — add shape, pattern, or direct labels.
- Categorical palette passes deuteranopia and protanopia simulation.
- `st.caption()` below every chart describing the key insight (screen reader fallback).
- Minimum 11px for any text in a chart.
- All data points have informative hover tooltips.

---

## Code Style

- Python 3.11+ syntax.
- Type hints on all function signatures.
- Docstrings on all functions in `src/`.
- One chart per function in `src/viz/charts.py` — each returns `go.Figure` or `alt.Chart`.
- No logic in `app.py` beyond layout — delegate to `src/` modules.
- Import order: stdlib → third-party → local (`src.`).
- f-strings for formatting. `f"{value:,.0f}"` for integers, `f"{value:.1%}"` for percentages.
- Use `pathlib.Path` for all file paths (Windows compatibility).

---

## Quality Checklist

Every item must pass before delivering.

### McCandless Test
- [ ] Data is accurate, sourced, and labeled
- [ ] Viz answers a specific question stated in title/subtitle
- [ ] Design is clean, elegant, no chart junk
- [ ] Narrative present — context, insight, implication

### Visual Design
- [ ] 3–5 color palette max, no rainbow
- [ ] High data-ink ratio — every pixel earns its place
- [ ] Direct labels preferred over legends
- [ ] Key insight annotated on at least one chart
- [ ] No 3D, no pie, no dual y-axes, no rotated labels
- [ ] Generous whitespace

### Streamlit
- [ ] `st.set_page_config()` with title and icon
- [ ] KPI metrics row at top (when applicable)
- [ ] Sidebar for filters only
- [ ] `@st.cache_data` on data loading
- [ ] Charts use `use_container_width=True`
- [ ] Source/about section in expander

### Accessibility
- [ ] Colorblind-safe palette
- [ ] No color-only encoding
- [ ] Descriptive caption below each chart
- [ ] All chart text >= 11px

### Code
- [ ] `src/config.py` and `src/theme.py` imported
- [ ] Chart functions in `src/viz/charts.py`
- [ ] Type hints and docstrings present
- [ ] `requirements.txt` complete
- [ ] App runs with `streamlit run app.py` without errors
