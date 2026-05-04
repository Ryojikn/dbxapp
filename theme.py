import dash_bootstrap_components as dbc

# Dash Bootstrap theme
THEME = dbc.themes.FLATLY

# Brand palette
COLOR_PRIMARY = "#E04B2A"      # Databricks red
COLOR_DARK    = "#1B1F23"
COLOR_SURFACE = "#FFFFFF"
COLOR_MUTED   = "#6C757D"
COLOR_SUCCESS = "#27AE60"
COLOR_WARNING = "#F39C12"
COLOR_DANGER  = "#E74C3C"

# Category colors for architecture nodes and chart series
CATEGORY_COLORS = {
    "source":    "#5D8AA8",
    "ingestion": "#E07B39",
    "catalog":   "#8E44AD",
    "bronze":    "#8D6748",
    "silver":    "#7F8C8D",
    "gold":      "#D4AC0D",
    "consumer":  "#27AE60",
    "agent":     "#C0392B",
}

# Chart series colors (same order as: Electronics, Apparel, Home & Garden, Sports)
CHART_COLORS = ["#E04B2A", "#3498DB", "#2ECC71", "#F39C12"]

# Spacing
PAD_SM = "8px"
PAD_MD = "16px"
PAD_LG = "24px"

# Plotly base layout applied to all figures
PLOTLY_LAYOUT = {
    "font":          {"family": "Inter, sans-serif", "size": 12, "color": COLOR_DARK},
    "paper_bgcolor": COLOR_SURFACE,
    "plot_bgcolor":  "#F8F9FA",
    "margin":        {"t": 40, "b": 40, "l": 50, "r": 20},
    "legend":        {"orientation": "h", "y": -0.2},
    "colorway":      CHART_COLORS,
}
