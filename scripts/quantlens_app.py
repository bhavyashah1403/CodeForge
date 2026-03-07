import streamlit as st
from src.data_loader import load_all_csvs, preview, get_unique_expiries, get_unique_strikes, filter_df
from src.visualization import price_time_chart, oi_time_chart, volume_time_chart
from src.anomaly import detect_anomalies

st.set_page_config(page_title="QuantLens", layout="wide")
st.title("QuantLens Options Intelligence Platform")

st.sidebar.header("Data")
if st.sidebar.button("Preview data"):
    df = preview()
    st.write(df)
else:
    df = load_all_csvs()

if not df.empty:
    # sidebar filters
    min_dt = df['datetime'].min()
    max_dt = df['datetime'].max()
    start_date, end_date = st.sidebar.date_input("Date range", value=(min_dt.date(), max_dt.date()))
    expiries = st.sidebar.multiselect("Expiry (pick or leave empty for all)", options=get_unique_expiries())
    strikes = st.sidebar.multiselect("Strike (pick or leave empty for all)", options=get_unique_strikes())
    df = filter_df(df, start_date=start_date, end_date=end_date, expiries=expiries if expiries else None, strikes=strikes if strikes else None)

if df.empty:
    st.warning("No CSV data found in data/ — add CSV files and reload.")
else:
    st.header("Market Overview")
    # Price chart (full width)
    price_fig = price_time_chart(df)
    if price_fig is not None:
        st.plotly_chart(price_fig, use_container_width=True)

    # OI and Volume side-by-side
    col1, col2 = st.columns(2)
    oi_fig = oi_time_chart(df)
    vol_fig = volume_time_chart(df)
    with col1:
        if oi_fig is not None:
            st.plotly_chart(oi_fig, use_container_width=True)
    with col2:
        if vol_fig is not None:
            st.plotly_chart(vol_fig, use_container_width=True)

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
