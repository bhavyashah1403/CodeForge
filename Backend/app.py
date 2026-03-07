"""
AI-Powered Options Market Visualization & Analytics Platform
════════════════════════════════════════════════════════════
Streamlit Dashboard — Main Entry Point

Tech Stack: Python | DuckDB | Pandas | Scikit-learn | Plotly | Streamlit
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

from config import PAGE_TITLE, PAGE_ICON, LAYOUT
from src.data_loader import load_all_csvs, init_duckdb, load_into_duckdb, query_duckdb
from src.preprocessing import preprocess_pipeline, get_data_summary
from src.feature_engineering import feature_engineering_pipeline
from src.analytics import (
    analytics_pipeline,
    compute_pcr_timeseries,
    compute_oi_distribution,
    compute_max_pain,
    get_top_anomalies,
)
from src.visualizations import (
    plot_oi_distribution,
    plot_volatility_smile,
    plot_pcr_timeseries,
    plot_oi_heatmap,
    plot_anomalies,
    plot_greeks_surface,
    plot_spot_price,
    plot_volume_profile,
)


# ─── Page Config ─────────────────────────────────────────
st.set_page_config(page_title=PAGE_TITLE, page_icon=PAGE_ICON, layout=LAYOUT)


# ─── Custom CSS ──────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(90deg, #00C853, #2979FF, #AB47BC);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .metric-card {
        background: #1E2130;
        border-radius: 10px;
        padding: 1rem;
        border-left: 4px solid #2979FF;
    }
    div[data-testid="stMetricValue"] { font-size: 1.4rem; }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
#  DATA LOADING (cached)
# ═══════════════════════════════════════════════════════════

@st.cache_data(show_spinner="Loading & preprocessing data...")
def load_and_process_data(iv_sample_frac: float = 0.1):
    """Load → Preprocess → Feature Engineer → Analytics (cached)."""
    raw = load_all_csvs()
    clean = preprocess_pipeline(raw)
    enriched = feature_engineering_pipeline(clean, compute_iv=True, iv_sample_frac=iv_sample_frac)
    analyzed = analytics_pipeline(enriched)
    return analyzed


@st.cache_data(show_spinner="Computing PCR timeseries...")
def get_pcr_ts(_df):
    return compute_pcr_timeseries(_df)


# ═══════════════════════════════════════════════════════════
#  SIDEBAR
# ═══════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("## ⚙️ Controls")

    iv_frac = st.slider(
        "IV Computation Sample %",
        min_value=1, max_value=100, value=10, step=5,
        help="% of data to compute IV on. Lower = faster, higher = more accurate.",
    )

    if st.button("🔄 Reload Data", use_container_width=True):
        st.cache_data.clear()

    st.markdown("---")
    st.markdown("### 📊 Navigation")
    page = st.radio(
        "Select View",
        ["🏠 Overview", "📈 Volatility Analysis", "🔍 Anomaly Detection",
         "📊 OI & Volume", "🧮 Greeks", "🗃️ Raw Data"],
        label_visibility="collapsed",
    )

# ─── Load Data ───────────────────────────────────────────
df = load_and_process_data(iv_sample_frac=iv_frac / 100)
pcr_ts = get_pcr_ts(df)

# ─── Sidebar Filters ────────────────────────────────────
with st.sidebar:
    st.markdown("---")
    st.markdown("### 🎯 Filters")

    expiry_dates = sorted(df["expiry"].dt.date.unique())
    selected_expiry = st.selectbox(
        "Expiry Date",
        options=expiry_dates,
        index=0,
    )
    selected_expiry_ts = pd.Timestamp(selected_expiry)

    # Filter data by expiry
    df_filtered = df[df["expiry"].dt.date == selected_expiry].copy()

    available_times = sorted(df_filtered["datetime"].unique())
    if available_times:
        selected_time = st.select_slider(
            "Snapshot Time",
            options=available_times,
            value=available_times[-1],
            format_func=lambda x: pd.Timestamp(x).strftime("%m/%d %H:%M"),
        )
    else:
        selected_time = None

    st.markdown("---")
    summary = get_data_summary(df)
    st.markdown(f"**Rows:** {summary['total_rows']:,}")
    st.markdown(f"**Strikes:** {summary['unique_strikes']}")
    st.markdown(f"**Files:** {len(summary['source_files'])}")


# ═══════════════════════════════════════════════════════════
#  PAGE: OVERVIEW
# ═══════════════════════════════════════════════════════════

if page == "🏠 Overview":
    st.markdown('<p class="main-header">AI-Powered Options Analytics Platform</p>',
                unsafe_allow_html=True)
    st.caption("NIFTY 50 Index Options — Real-time Analysis & AI Anomaly Detection")

    # ── Key Metrics Row ──────────────────────────────────
    col1, col2, col3, col4, col5 = st.columns(5)

    latest = df_filtered[df_filtered["datetime"] == df_filtered["datetime"].max()]

    with col1:
        spot = latest["spot_close"].iloc[0] if len(latest) > 0 else 0
        st.metric("Spot Price", f"₹{spot:,.2f}")
    with col2:
        atm = latest["ATM"].iloc[0] if len(latest) > 0 else 0
        st.metric("ATM Strike", f"₹{atm:,.0f}")
    with col3:
        pcr = latest["pcr_oi"].mean() if len(latest) > 0 else 0
        sentiment = "🟢 Bullish" if pcr > 1.0 else "🔴 Bearish" if pcr < 0.7 else "🟡 Neutral"
        st.metric("PCR (OI)", f"{pcr:.2f}", sentiment)
    with col4:
        total_oi = latest["total_oi"].sum() if len(latest) > 0 else 0
        st.metric("Total OI", f"{total_oi:,.0f}")
    with col5:
        anomalies = df_filtered["is_anomaly"].sum() if "is_anomaly" in df_filtered.columns else 0
        st.metric("Anomalies", f"{anomalies:,}")

    st.markdown("---")

    # ── Charts Row 1 ─────────────────────────────────────
    col_left, col_right = st.columns(2)

    with col_left:
        st.plotly_chart(plot_spot_price(df_filtered), use_container_width=True)

    with col_right:
        st.plotly_chart(plot_pcr_timeseries(pcr_ts), use_container_width=True)

    # ── Charts Row 2 ─────────────────────────────────────
    col_left2, col_right2 = st.columns(2)

    with col_left2:
        st.plotly_chart(
            plot_oi_distribution(df_filtered, timestamp=selected_time),
            use_container_width=True,
        )

    with col_right2:
        st.plotly_chart(
            plot_volume_profile(df_filtered),
            use_container_width=True,
        )

    # ── Max Pain ─────────────────────────────────────────
    with st.expander("📌 Max Pain Analysis", expanded=False):
        mp = compute_max_pain(df_filtered, timestamp=selected_time)
        if mp:
            c1, c2, c3 = st.columns(3)
            c1.metric("Max Pain Strike", f"₹{mp['max_pain_strike']:,.0f}")
            c2.metric("Spot Price", f"₹{mp['spot_price']:,.2f}")
            c3.metric("Distance from Spot", f"{mp['distance_from_spot']:,.0f} pts")
        else:
            st.info("Could not compute Max Pain for selected snapshot")


# ═══════════════════════════════════════════════════════════
#  PAGE: VOLATILITY ANALYSIS
# ═══════════════════════════════════════════════════════════

elif page == "📈 Volatility Analysis":
    st.markdown("## 📈 Implied Volatility Analysis")

    if "iv_CE" in df_filtered.columns and df_filtered["iv_CE"].notna().any():
        # Smile chart
        st.plotly_chart(
            plot_volatility_smile(df_filtered, timestamp=selected_time),
            use_container_width=True,
        )

        # IV Statistics
        st.markdown("### IV Statistics")
        col1, col2, col3 = st.columns(3)
        iv_data = df_filtered[df_filtered["iv_CE"].notna()]
        if len(iv_data) > 0:
            col1.metric("Mean CE IV", f"{iv_data['iv_CE'].mean()*100:.1f}%")
            col2.metric("Mean PE IV", f"{iv_data['iv_PE'].mean()*100:.1f}%")
            col3.metric("IV Spread (CE-PE)", f"{(iv_data['iv_CE'] - iv_data['iv_PE']).mean()*100:.2f}%")

        # IV Heatmap-like view
        st.markdown("### IV across Strikes (Selected Snapshot)")
        snap = df_filtered[df_filtered["datetime"] == selected_time].dropna(subset=["iv_CE"]).sort_values("strike")
        if len(snap) > 0:
            st.dataframe(
                snap[["strike", "CE", "PE", "iv_CE", "iv_PE", "moneyness_label"]].style.format({
                    "iv_CE": "{:.2%}", "iv_PE": "{:.2%}",
                    "CE": "₹{:.2f}", "PE": "₹{:.2f}",
                }),
                use_container_width=True,
                height=400,
            )
    else:
        st.warning("IV data not available. Increase IV sample % in sidebar and reload.")


# ═══════════════════════════════════════════════════════════
#  PAGE: ANOMALY DETECTION
# ═══════════════════════════════════════════════════════════

elif page == "🔍 Anomaly Detection":
    st.markdown("## 🔍 AI-Powered Anomaly Detection")
    st.caption("Isolation Forest (unsupervised ML) identifies unusual trading patterns")

    if "is_anomaly" in df_filtered.columns:
        col1, col2, col3 = st.columns(3)
        n_anomalies = df_filtered["is_anomaly"].sum()
        col1.metric("Total Anomalies", f"{n_anomalies:,}")
        col2.metric("Anomaly Rate", f"{n_anomalies/len(df_filtered)*100:.1f}%")
        col3.metric("Volume Spikes", f"{df_filtered['volume_spike_any'].sum():,}" if "volume_spike_any" in df_filtered.columns else "N/A")

        st.plotly_chart(plot_anomalies(df_filtered), use_container_width=True)

        st.markdown("### Top Anomalous Data Points")
        top = get_top_anomalies(df_filtered, n=25)
        if len(top) > 0:
            st.dataframe(top, use_container_width=True, height=400)
        else:
            st.info("No anomalies detected for this expiry")

        # Volume spikes
        if "volume_spike_any" in df_filtered.columns:
            st.markdown("### Volume Spikes")
            spikes = df_filtered[df_filtered["volume_spike_any"] == True]
            if len(spikes) > 0:
                st.dataframe(
                    spikes[["datetime", "strike", "volume_CE", "volume_PE", "total_volume", "anomaly_score"]]
                    .sort_values("total_volume", ascending=False).head(20),
                    use_container_width=True,
                )
    else:
        st.warning("Anomaly detection results not available")


# ═══════════════════════════════════════════════════════════
#  PAGE: OI & VOLUME
# ═══════════════════════════════════════════════════════════

elif page == "📊 OI & Volume":
    st.markdown("## 📊 Open Interest & Volume Analysis")

    tab1, tab2, tab3 = st.tabs(["OI Distribution", "OI Heatmap", "Volume Profile"])

    with tab1:
        st.plotly_chart(
            plot_oi_distribution(df_filtered, timestamp=selected_time),
            use_container_width=True,
        )

    with tab2:
        heatmap_col = st.selectbox("OI Type", ["oi_CE", "oi_PE"])
        st.plotly_chart(
            plot_oi_heatmap(df_filtered, oi_col=heatmap_col),
            use_container_width=True,
        )

    with tab3:
        st.plotly_chart(plot_volume_profile(df_filtered), use_container_width=True)

    # OI Change analysis
    st.markdown("### OI Change Leaders")
    if "oi_CE_change" in df_filtered.columns:
        latest_oi = df_filtered[df_filtered["datetime"] == selected_time]
        if len(latest_oi) > 0:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Top CE OI Builds**")
                st.dataframe(
                    latest_oi.nlargest(10, "oi_CE")[["strike", "oi_CE", "oi_CE_change"]],
                    use_container_width=True,
                )
            with col2:
                st.markdown("**Top PE OI Builds**")
                st.dataframe(
                    latest_oi.nlargest(10, "oi_PE")[["strike", "oi_PE", "oi_PE_change"]],
                    use_container_width=True,
                )


# ═══════════════════════════════════════════════════════════
#  PAGE: GREEKS
# ═══════════════════════════════════════════════════════════

elif page == "🧮 Greeks":
    st.markdown("## 🧮 Option Greeks Analysis")

    if "delta_CE" in df_filtered.columns:
        greek_choice = st.selectbox(
            "Select Greek",
            ["delta_CE", "delta_PE", "gamma_CE", "gamma_PE",
             "theta_CE", "theta_PE", "vega_CE", "vega_PE"],
        )

        st.plotly_chart(
            plot_greeks_surface(df_filtered, greek=greek_choice),
            use_container_width=True,
        )

        # Greeks table at selected time
        st.markdown("### Greeks at Selected Snapshot")
        snap = df_filtered[df_filtered["datetime"] == selected_time]
        if len(snap) > 0:
            greek_cols = ["strike", "CE", "PE", "delta_CE", "delta_PE",
                          "gamma_CE", "gamma_PE", "theta_CE", "theta_PE"]
            available_cols = [c for c in greek_cols if c in snap.columns]
            st.dataframe(
                snap[available_cols].sort_values("strike"),
                use_container_width=True,
                height=400,
            )
    else:
        st.warning("Greeks not computed. Enable IV computation in sidebar.")


# ═══════════════════════════════════════════════════════════
#  PAGE: RAW DATA
# ═══════════════════════════════════════════════════════════

elif page == "🗃️ Raw Data":
    st.markdown("## 🗃️ Data Explorer")

    st.markdown(f"**Total rows:** {len(df_filtered):,} | **Columns:** {len(df_filtered.columns)}")

    # Column filter
    all_cols = df_filtered.columns.tolist()
    selected_cols = st.multiselect(
        "Select columns to display",
        options=all_cols,
        default=["datetime", "strike", "CE", "PE", "spot_close", "oi_CE", "oi_PE",
                 "volume_CE", "volume_PE", "pcr_oi", "is_anomaly"],
    )

    if selected_cols:
        st.dataframe(
            df_filtered[selected_cols].head(1000),
            use_container_width=True,
            height=600,
        )

    # DuckDB SQL Query
    st.markdown("### 🦆 DuckDB SQL Query")
    sql_query = st.text_area(
        "Enter SQL query (table: `df_filtered`)",
        value="SELECT strike, AVG(oi_CE) as avg_oi_ce, AVG(oi_PE) as avg_oi_pe FROM df_filtered GROUP BY strike ORDER BY strike",
        height=100,
    )
    if st.button("Run Query"):
        try:
            import duckdb
            result = duckdb.query(sql_query).to_df()
            st.dataframe(result, use_container_width=True)
        except Exception as e:
            st.error(f"Query error: {e}")


# ─── Footer ─────────────────────────────────────────────
st.markdown("---")
st.caption("Built with Python | DuckDB | Pandas | Scikit-learn | Plotly | Streamlit — FOSS Stack")
