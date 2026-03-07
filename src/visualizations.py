"""
Visualizations Module
─────────────────────
Plotly-based interactive charts for the Options Analytics Dashboard.
All functions return Plotly Figure objects for Streamlit rendering.
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots


# ═══════════════════════════════════════════════════════════
#  COLOR SCHEME
# ═══════════════════════════════════════════════════════════

COLORS = {
    "CE": "#00C853",       # Green for calls
    "PE": "#FF1744",       # Red for puts
    "spot": "#2979FF",     # Blue for spot
    "anomaly": "#FF6D00",  # Orange for anomalies
    "bg": "#0E1117",       # Dark background
    "grid": "#1E2130",     # Grid lines
    "text": "#FAFAFA",     # Text color
}

LAYOUT_DEFAULTS = dict(
    template="plotly_dark",
    font=dict(family="Segoe UI, sans-serif", size=12),
    margin=dict(l=60, r=30, t=50, b=50),
    height=500,
)


# ═══════════════════════════════════════════════════════════
#  1. OI DISTRIBUTION (Bar Chart)
# ═══════════════════════════════════════════════════════════

def plot_oi_distribution(df: pd.DataFrame, timestamp=None, expiry=None) -> go.Figure:
    """Stacked bar chart of CE/PE OI across strikes."""
    data = df.copy()
    if expiry is not None:
        data = data[data["expiry"] == expiry]
    if timestamp is not None:
        data = data[data["datetime"] == timestamp]
    else:
        data = data[data["datetime"] == data["datetime"].max()]

    oi = data.groupby("strike").agg(
        oi_CE=("oi_CE", "sum"),
        oi_PE=("oi_PE", "sum"),
    ).reset_index()

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=oi["strike"], y=oi["oi_CE"],
        name="Call OI", marker_color=COLORS["CE"], opacity=0.85,
    ))
    fig.add_trace(go.Bar(
        x=oi["strike"], y=-oi["oi_PE"],
        name="Put OI", marker_color=COLORS["PE"], opacity=0.85,
    ))

    # ATM line
    if "ATM" in data.columns and len(data) > 0:
        atm = data["ATM"].iloc[0]
        fig.add_vline(x=atm, line_dash="dash", line_color="yellow",
                      annotation_text=f"ATM: {atm:.0f}")

    fig.update_layout(
        title="Open Interest Distribution by Strike",
        xaxis_title="Strike Price",
        yaxis_title="Open Interest",
        barmode="overlay",
        **LAYOUT_DEFAULTS,
    )
    return fig


# ═══════════════════════════════════════════════════════════
#  2. VOLATILITY SMILE / SKEW
# ═══════════════════════════════════════════════════════════

def plot_volatility_smile(df: pd.DataFrame, timestamp=None, expiry=None) -> go.Figure:
    """IV vs Strike price (volatility smile curve)."""
    data = df.copy()
    if expiry is not None:
        data = data[data["expiry"] == expiry]
    if timestamp is not None:
        data = data[data["datetime"] == timestamp]
    else:
        data = data[data["datetime"] == data["datetime"].max()]

    # Filter valid IV
    data = data.dropna(subset=["iv_CE", "iv_PE"])
    data = data[(data["iv_CE"] > 0.01) & (data["iv_CE"] < 3.0)]
    data = data.sort_values("strike")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=data["strike"], y=data["iv_CE"] * 100,
        mode="lines+markers", name="Call IV",
        line=dict(color=COLORS["CE"], width=2),
        marker=dict(size=5),
    ))
    fig.add_trace(go.Scatter(
        x=data["strike"], y=data["iv_PE"] * 100,
        mode="lines+markers", name="Put IV",
        line=dict(color=COLORS["PE"], width=2),
        marker=dict(size=5),
    ))

    if "ATM" in data.columns and len(data) > 0:
        atm = data["ATM"].iloc[0]
        fig.add_vline(x=atm, line_dash="dash", line_color="yellow",
                      annotation_text=f"ATM: {atm:.0f}")

    fig.update_layout(
        title="Implied Volatility Smile / Skew",
        xaxis_title="Strike Price",
        yaxis_title="Implied Volatility (%)",
        **LAYOUT_DEFAULTS,
    )
    return fig


# ═══════════════════════════════════════════════════════════
#  3. PCR TIMESERIES
# ═══════════════════════════════════════════════════════════

def plot_pcr_timeseries(pcr_ts: pd.DataFrame) -> go.Figure:
    """Put-Call Ratio over time with spot price overlay."""
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(go.Scatter(
        x=pcr_ts["datetime"], y=pcr_ts["pcr_oi"],
        mode="lines", name="PCR (OI)",
        line=dict(color="#AB47BC", width=2),
    ), secondary_y=False)

    fig.add_trace(go.Scatter(
        x=pcr_ts["datetime"], y=pcr_ts["spot"],
        mode="lines", name="Spot Price",
        line=dict(color=COLORS["spot"], width=1.5),
    ), secondary_y=True)

    # Sentiment zones
    fig.add_hline(y=1.0, line_dash="dot", line_color="gray",
                  annotation_text="Neutral (1.0)", secondary_y=False)
    fig.add_hline(y=1.5, line_dash="dot", line_color=COLORS["CE"],
                  annotation_text="Bullish >1.5", secondary_y=False)
    fig.add_hline(y=0.7, line_dash="dot", line_color=COLORS["PE"],
                  annotation_text="Bearish <0.7", secondary_y=False)

    fig.update_layout(
        title="Put-Call Ratio (OI) vs Spot Price",
        **LAYOUT_DEFAULTS,
    )
    fig.update_yaxes(title_text="PCR", secondary_y=False)
    fig.update_yaxes(title_text="Spot Price", secondary_y=True)
    return fig


# ═══════════════════════════════════════════════════════════
#  4. OI HEATMAP
# ═══════════════════════════════════════════════════════════

def plot_oi_heatmap(df: pd.DataFrame, oi_col: str = "oi_CE", expiry=None) -> go.Figure:
    """Heatmap of OI across time and strikes."""
    data = df.copy()
    if expiry is not None:
        data = data[data["expiry"] == expiry]

    # Pivot: datetime × strike → OI
    pivot = data.pivot_table(
        index="strike", columns="datetime", values=oi_col, aggfunc="sum"
    ).fillna(0)

    # Subsample columns for readability
    if pivot.shape[1] > 100:
        step = max(1, pivot.shape[1] // 100)
        pivot = pivot.iloc[:, ::step]

    fig = go.Figure(data=go.Heatmap(
        z=pivot.values,
        x=pivot.columns.astype(str),
        y=pivot.index,
        colorscale="Viridis",
        colorbar_title="OI",
    ))

    title = f"{oi_col.replace('_', ' ').title()} Heatmap (Strike × Time)"
    fig.update_layout(
        title=title,
        xaxis_title="Time",
        yaxis_title="Strike",
        **LAYOUT_DEFAULTS,
        height=600,
    )
    return fig


# ═══════════════════════════════════════════════════════════
#  5. ANOMALY SCATTER
# ═══════════════════════════════════════════════════════════

def plot_anomalies(df: pd.DataFrame) -> go.Figure:
    """Scatter plot highlighting anomalous data points."""
    fig = go.Figure()

    normal = df[df["is_anomaly"] == False]
    anomalies = df[df["is_anomaly"] == True]

    fig.add_trace(go.Scatter(
        x=normal["datetime"], y=normal["total_volume"],
        mode="markers", name="Normal",
        marker=dict(color=COLORS["spot"], size=3, opacity=0.3),
    ))

    fig.add_trace(go.Scatter(
        x=anomalies["datetime"], y=anomalies["total_volume"],
        mode="markers", name="Anomaly",
        marker=dict(color=COLORS["anomaly"], size=8, opacity=0.8,
                    symbol="x", line=dict(width=1, color="white")),
        text=anomalies["strike"].astype(str) + " strike",
    ))

    fig.update_layout(
        title="Anomaly Detection: Volume Patterns",
        xaxis_title="Time",
        yaxis_title="Total Volume",
        **LAYOUT_DEFAULTS,
    )
    return fig


# ═══════════════════════════════════════════════════════════
#  6. GREEKS SURFACE
# ═══════════════════════════════════════════════════════════

def plot_greeks_surface(df: pd.DataFrame, greek: str = "delta_CE", expiry=None) -> go.Figure:
    """3D surface plot of a Greek across strike and time."""
    data = df.copy()
    if expiry is not None:
        data = data[data["expiry"] == expiry]

    if greek not in data.columns:
        fig = go.Figure()
        fig.add_annotation(text=f"Greek '{greek}' not available", showarrow=False)
        return fig

    data = data.dropna(subset=[greek])

    pivot = data.pivot_table(
        index="strike", columns="datetime", values=greek, aggfunc="mean"
    ).fillna(0)

    if pivot.shape[1] > 50:
        step = max(1, pivot.shape[1] // 50)
        pivot = pivot.iloc[:, ::step]

    fig = go.Figure(data=go.Surface(
        z=pivot.values,
        x=list(range(pivot.shape[1])),
        y=pivot.index,
        colorscale="RdYlGn",
    ))

    fig.update_layout(
        title=f"{greek.replace('_', ' ').title()} Surface",
        scene=dict(
            xaxis_title="Time Steps",
            yaxis_title="Strike",
            zaxis_title=greek,
        ),
        **LAYOUT_DEFAULTS,
        height=600,
    )
    return fig


# ═══════════════════════════════════════════════════════════
#  7. PRICE EVOLUTION
# ═══════════════════════════════════════════════════════════

def plot_spot_price(df: pd.DataFrame) -> go.Figure:
    """Spot price line chart over time."""
    spot = df.groupby("datetime")["spot_close"].first().reset_index()

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=spot["datetime"], y=spot["spot_close"],
        mode="lines", name="NIFTY Spot",
        line=dict(color=COLORS["spot"], width=2),
        fill="tozeroy", fillcolor="rgba(41,121,255,0.1)",
    ))

    fig.update_layout(
        title="NIFTY Spot Price",
        xaxis_title="Time",
        yaxis_title="Price",
        **LAYOUT_DEFAULTS,
    )
    return fig


# ═══════════════════════════════════════════════════════════
#  8. VOLUME PROFILE
# ═══════════════════════════════════════════════════════════

def plot_volume_profile(df: pd.DataFrame, expiry=None) -> go.Figure:
    """Horizontal bar chart showing volume at each strike."""
    data = df.copy()
    if expiry is not None:
        data = data[data["expiry"] == expiry]

    vol = data.groupby("strike").agg(
        volume_CE=("volume_CE", "sum"),
        volume_PE=("volume_PE", "sum"),
    ).reset_index()

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=vol["strike"], x=vol["volume_CE"],
        name="Call Volume", marker_color=COLORS["CE"],
        orientation="h", opacity=0.8,
    ))
    fig.add_trace(go.Bar(
        y=vol["strike"], x=-vol["volume_PE"],
        name="Put Volume", marker_color=COLORS["PE"],
        orientation="h", opacity=0.8,
    ))

    fig.update_layout(
        title="Volume Profile by Strike",
        xaxis_title="Volume",
        yaxis_title="Strike",
        barmode="overlay",
        **LAYOUT_DEFAULTS,
        height=600,
    )
    return fig
