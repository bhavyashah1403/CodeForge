"""
CodeForge – AI-Powered Options Market Analytics Dashboard

This script launches the Streamlit-based analytics dashboard
for exploring derivatives options data.

Usage:
    streamlit run scripts/run_dashboard.py
"""

import os
import sys

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

st.set_page_config(
    page_title="CodeForge Options Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ---------------------------------------------------------------------------
# Data Loading
# ---------------------------------------------------------------------------
@st.cache_data
def load_data() -> pd.DataFrame:
    """Load and concatenate all CSV files from the data directory."""
    csv_files = sorted(
        f for f in os.listdir(DATA_DIR) if f.endswith(".csv")
    )
    if not csv_files:
        st.error("No CSV data files found in the data/ directory.")
        st.stop()

    frames = []
    for csv_file in csv_files:
        path = os.path.join(DATA_DIR, csv_file)
        df = pd.read_csv(path)
        frames.append(df)

    data = pd.concat(frames, ignore_index=True)

    # Parse datetime columns if present
    for col in ("datetime", "expiry"):
        if col in data.columns:
            data[col] = pd.to_datetime(data[col], errors="coerce")

    return data


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
st.sidebar.title("📊 CodeForge Analytics")
st.sidebar.markdown("AI-Powered Options Market Analytics")


# ---------------------------------------------------------------------------
# Main Content
# ---------------------------------------------------------------------------
def main():
    st.title("CodeForge – Options Market Analytics Dashboard")
    st.markdown(
        "Explore derivatives data, detect patterns in volatility, "
        "open interest, and volume."
    )

    data = load_data()

    # --- Overview metrics ---------------------------------------------------
    st.header("📈 Dataset Overview")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Records", f"{len(data):,}")
    col2.metric("CSV Files", len([f for f in os.listdir(DATA_DIR) if f.endswith(".csv")]))
    col3.metric("Columns", len(data.columns))
    col4.metric(
        "Date Range",
        (
            f"{data['datetime'].min():%Y-%m-%d} → {data['datetime'].max():%Y-%m-%d}"
            if "datetime" in data.columns
            else "N/A"
        ),
    )

    st.dataframe(data.head(100), use_container_width=True)

    # --- Column distribution ------------------------------------------------
    st.header("📊 Column Explorer")
    numeric_cols = data.select_dtypes(include=[np.number]).columns.tolist()
    if numeric_cols:
        selected_col = st.selectbox("Select a numeric column", numeric_cols)
        fig = px.histogram(
            data,
            x=selected_col,
            nbins=60,
            title=f"Distribution of {selected_col}",
            template="plotly_dark",
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.caption("Built with Streamlit · Plotly · Pandas — FOSS ❤️")


if __name__ == "__main__":
    main()
