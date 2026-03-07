import streamlit as st
from src.data_loader import load_all_csvs, preview
from src.visualization import price_time_chart, oi_volume_chart
from src.anomaly import detect_anomalies

st.set_page_config(page_title="QuantLens", layout="wide")
st.title("QuantLens Options Intelligence Platform")

st.sidebar.header("Data")
if st.sidebar.button("Preview data"):
    df = preview()
    st.write(df)
else:
    df = load_all_csvs()

if df.empty:
    st.warning("No CSV data found in data/ — add CSV files and reload.")
else:
    st.header("Market Overview")
    st.plotly_chart(price_time_chart(df), use_container_width=True)
    st.plotly_chart(oi_volume_chart(df), use_container_width=True)

    st.header("AI Alerts (basic)")
    # simple anomaly check: volume spike (sum of both volumes)
    df = df.sort_values("datetime")
    df["total_volume"] = df.get("volume_CE", 0).fillna(0) + df.get("volume_PE", 0).fillna(0)
    anomalies = detect_anomalies(df, ["total_volume"], contamination=0.02)
    if (anomalies == -1).any():
        st.error("⚠️ Anomalies detected in volume — see table below")
        st.write(df[anomalies == -1])
    else:
        st.success("No anomalies detected (basic check)")
