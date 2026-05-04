import dash_bootstrap_components as dbc

# Dash Bootstrap theme
THEME = dbc.themes.FLATLY

# Brand palette — hex equivalents of OKLCH tokens defined in styles.css
COLOR_PRIMARY = "#E04B2A"      # oklch(0.55 0.185 28) — Databricks red
COLOR_DARK    = "#1E1C1B"      # oklch(0.14 0.006 30) — near-black, warm-tinted
COLOR_SURFACE = "#FDFCFB"      # oklch(0.995 0.002 60) — warm white
COLOR_BG      = "#F7F5F3"      # oklch(0.975 0.004 60) — page background
COLOR_MUTED   = "#6E6A68"      # oklch(0.50 0.010 30) — muted text
COLOR_BORDER  = "#E0DBD7"      # oklch(0.890 0.005 60) — border
COLOR_SUCCESS = "#1E9B64"      # oklch(0.60 0.14 142) — green
COLOR_WARNING = "#C58C12"      # oklch(0.70 0.15 75) — amber
COLOR_DANGER  = "#E04B2A"      # same as primary — red is red

# Category colors for architecture nodes and chart series
CATEGORY_COLORS = {
    "source":    "#4A8DB5",
    "ingestion": "#E07B39",
    "catalog":   "#8E44AD",
    "bronze":    "#8D6748",
    "silver":    "#7A8590",
    "gold":      "#C9A227",
    "consumer":  "#1E9B64",
    "agent":     "#C0392B",
}

# Chart series colors (Electronics, Apparel, Home & Garden, Sports)
CHART_COLORS = ["#E04B2A", "#3B82F6", "#10B981", "#F59E0B"]

# Spacing constants
PAD_XS = "4px"
PAD_SM = "8px"
PAD_MD = "16px"
PAD_LG = "24px"
PAD_XL = "40px"

# Dark chart colours — used by theme callback to sync on toggle
CHART_DARK = {
    "font_color":  "#D6D4D0",
    "grid_color":  "#2E2C2A",
    "tick_color":  "#7A7674",
    "hover_bg":    "#1F1D1A",
    "hover_bd":    "#3A3835",
}
CHART_LIGHT = {
    "font_color":  COLOR_DARK,
    "grid_color":  COLOR_BORDER,
    "tick_color":  COLOR_MUTED,
    "hover_bg":    COLOR_SURFACE,
    "hover_bd":    COLOR_BORDER,
}

# Plotly base layout applied to all figures.
# Backgrounds are transparent so the containing .chart-wrap div's color shows through.
PLOTLY_LAYOUT = {
    "font": {
        "family": "Inter, 'Segoe UI', system-ui, sans-serif",
        "size":   12,
        "color":  CHART_DARK["font_color"],
    },
    "paper_bgcolor": "rgba(0,0,0,0)",
    "plot_bgcolor":  "rgba(0,0,0,0)",
    "margin": {"t": 44, "b": 36, "l": 52, "r": 16},
    "legend": {
        "orientation": "h",
        "y": -0.18,
        "font": {"size": 11},
        "bgcolor": "rgba(0,0,0,0)",
    },
    "colorway": CHART_COLORS,
    "xaxis": {
        "gridcolor":  CHART_DARK["grid_color"],
        "linecolor":  CHART_DARK["grid_color"],
        "tickfont":   {"size": 11, "color": CHART_DARK["tick_color"]},
        "title_font": {"size": 12, "color": CHART_DARK["tick_color"]},
        "showgrid":   False,
        "zeroline":   False,
    },
    "yaxis": {
        "gridcolor":  CHART_DARK["grid_color"],
        "linecolor":  "rgba(0,0,0,0)",
        "tickfont":   {"size": 11, "color": CHART_DARK["tick_color"]},
        "title_font": {"size": 12, "color": CHART_DARK["tick_color"]},
        "showgrid":   True,
        "zeroline":   False,
        "gridwidth":  1,
    },
    "title": {
        "font": {"size": 13, "color": CHART_DARK["font_color"], "weight": "bold"},
        "x": 0,
        "xanchor": "left",
        "pad": {"l": 0},
    },
    "hoverlabel": {
        "bgcolor":    CHART_DARK["hover_bg"],
        "bordercolor": CHART_DARK["hover_bd"],
        "font":       {"size": 12, "color": CHART_DARK["font_color"]},
    },
}
