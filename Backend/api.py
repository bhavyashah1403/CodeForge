"""
FastAPI REST API — Backend for React Frontend
══════════════════════════════════════════════
Exposes all analytics, data, and model results as JSON endpoints.
Run:  uvicorn api:app --reload --port 8000

Your friend's React app calls these endpoints via fetch() / axios.
"""

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import pandas as pd
import numpy as np
import json
from datetime import date, datetime

from config import PAGE_TITLE
from src.data_loader import load_all_csvs
from src.preprocessing import preprocess_pipeline, get_data_summary
from src.feature_engineering import feature_engineering_pipeline
from src.analytics import (
    analytics_pipeline,
    compute_pcr_timeseries,
    compute_oi_distribution,
    compute_max_pain,
    get_top_anomalies,
    compute_evaluation_metrics,
)

# ─── App Setup ───────────────────────────────────────────
app = FastAPI(
    title="Options Analytics API",
    description="AI-Powered NIFTY Options Market Analytics — Backend API for React Frontend",
    version="1.0.0",
)

# CORS — Allow React dev server (localhost:3000) and any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to your React domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Helper: Convert DataFrame to JSON-safe dict ────────
def df_to_json(df: pd.DataFrame) -> list[dict]:
    """Convert DataFrame to list of dicts with JSON-safe types."""
    df = df.copy()
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            df[col] = df[col].astype(str)
        elif df[col].dtype == "object":
            pass
        elif pd.api.types.is_bool_dtype(df[col]):
            df[col] = df[col].astype(bool)
    # Replace NaN/inf with None
    df = df.replace([np.inf, -np.inf], np.nan)
    df = df.where(df.notna(), None)
    return df.to_dict(orient="records")


# ─── Data Loading (cached at startup) ───────────────────
print("[API] Loading and processing data...")
_raw = load_all_csvs()
_clean = preprocess_pipeline(_raw)
_enriched = feature_engineering_pipeline(_clean, compute_iv=True, iv_sample_frac=0.1)
_df = analytics_pipeline(_enriched)
_pcr_ts = compute_pcr_timeseries(_df)
_metrics = compute_evaluation_metrics(_df)
_summary = get_data_summary(_df)
print(f"[API] Ready — {len(_df):,} rows loaded")


# ═══════════════════════════════════════════════════════════
#  ENDPOINTS
# ═══════════════════════════════════════════════════════════

# ── 1. HEALTH CHECK ─────────────────────────────────────
@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "message": PAGE_TITLE, "rows": len(_df)}


@app.get("/health", tags=["Health"])
def health():
    return {"status": "healthy", "data_loaded": len(_df) > 0, "total_rows": len(_df)}


# ── 2. DATA SUMMARY ─────────────────────────────────────
@app.get("/api/summary", tags=["Data"])
def get_summary():
    """Get overall dataset summary statistics."""
    safe_summary = {}
    for k, v in _summary.items():
        if isinstance(v, list):
            safe_summary[k] = [str(x) for x in v]
        else:
            safe_summary[k] = v
    return safe_summary


# ── 3. EXPIRY DATES ─────────────────────────────────────
@app.get("/api/expiries", tags=["Data"])
def get_expiries():
    """List all available expiry dates."""
    expiries = sorted(_df["expiry"].dt.strftime("%Y-%m-%d").unique().tolist())
    return {"expiries": expiries}


# ── 4. AVAILABLE TIMESTAMPS ─────────────────────────────
@app.get("/api/timestamps", tags=["Data"])
def get_timestamps(expiry: str = None, limit: int = Query(100, le=5000)):
    """Get available timestamps, optionally filtered by expiry."""
    data = _df.copy()
    if expiry:
        data = data[data["expiry"].dt.strftime("%Y-%m-%d") == expiry]
    times = sorted(data["datetime"].unique())
    times = [pd.Timestamp(t).strftime("%Y-%m-%d %H:%M:%S") for t in times[-limit:]]
    return {"timestamps": times, "total": len(times)}


# ── 5. SPOT PRICE TIMESERIES ────────────────────────────
@app.get("/api/spot-price", tags=["Market Data"])
def get_spot_price(expiry: str = None):
    """Spot price over time."""
    data = _df.copy()
    if expiry:
        data = data[data["expiry"].dt.strftime("%Y-%m-%d") == expiry]
    spot = data.groupby("datetime")["spot_close"].first().reset_index()
    spot = spot.sort_values("datetime")
    return df_to_json(spot)


# ── 6. OI DISTRIBUTION ──────────────────────────────────
@app.get("/api/oi-distribution", tags=["Analytics"])
def get_oi_distribution(timestamp: str = None, expiry: str = None):
    """Open Interest distribution across strikes at a given time."""
    data = _df.copy()
    if expiry:
        data = data[data["expiry"].dt.strftime("%Y-%m-%d") == expiry]
    if timestamp:
        ts = pd.Timestamp(timestamp)
        data = data[data["datetime"] == ts]
    else:
        data = data[data["datetime"] == data["datetime"].max()]

    oi = data.groupby("strike").agg(
        oi_CE=("oi_CE", "sum"),
        oi_PE=("oi_PE", "sum"),
        volume_CE=("volume_CE", "sum"),
        volume_PE=("volume_PE", "sum"),
    ).reset_index()
    oi["total_oi"] = oi["oi_CE"] + oi["oi_PE"]
    return df_to_json(oi.sort_values("strike"))


# ── 7. PCR TIMESERIES ───────────────────────────────────
@app.get("/api/pcr", tags=["Analytics"])
def get_pcr():
    """Put-Call Ratio (OI + Volume) over time with spot price."""
    return df_to_json(_pcr_ts)


# ── 8. VOLATILITY SMILE ─────────────────────────────────
@app.get("/api/volatility-smile", tags=["Volatility"])
def get_volatility_smile(timestamp: str = None, expiry: str = None):
    """IV across strikes (volatility smile)."""
    data = _df.copy()
    if expiry:
        data = data[data["expiry"].dt.strftime("%Y-%m-%d") == expiry]
    if timestamp:
        data = data[data["datetime"] == pd.Timestamp(timestamp)]
    else:
        data = data[data["datetime"] == data["datetime"].max()]

    data = data.dropna(subset=["iv_CE", "iv_PE"])
    data = data[(data["iv_CE"] > 0.01) & (data["iv_CE"] < 3.0)]
    result = data[["strike", "iv_CE", "iv_PE", "iv_avg", "moneyness_label"]].sort_values("strike")
    # Convert IV to percentage
    result = result.copy()
    result["iv_CE_pct"] = (result["iv_CE"] * 100).round(2)
    result["iv_PE_pct"] = (result["iv_PE"] * 100).round(2)
    return df_to_json(result)


# ── 9. ANOMALIES ────────────────────────────────────────
@app.get("/api/anomalies", tags=["AI / ML"])
def get_anomalies(n: int = Query(50, le=500), expiry: str = None):
    """Top N anomalous data points detected by Isolation Forest."""
    data = _df.copy()
    if expiry:
        data = data[data["expiry"].dt.strftime("%Y-%m-%d") == expiry]
    top = get_top_anomalies(data, n=n)
    return df_to_json(top)


@app.get("/api/anomaly-scatter", tags=["AI / ML"])
def get_anomaly_scatter(expiry: str = None):
    """All data points with anomaly flag (for scatter plot)."""
    data = _df.copy()
    if expiry:
        data = data[data["expiry"].dt.strftime("%Y-%m-%d") == expiry]
    cols = ["datetime", "strike", "total_volume", "total_oi", "is_anomaly", "anomaly_score"]
    available = [c for c in cols if c in data.columns]
    return df_to_json(data[available])


# ── 10. VOLUME SPIKES ───────────────────────────────────
@app.get("/api/volume-spikes", tags=["AI / ML"])
def get_volume_spikes(n: int = Query(50, le=500), expiry: str = None):
    """Top N volume spikes."""
    data = _df.copy()
    if expiry:
        data = data[data["expiry"].dt.strftime("%Y-%m-%d") == expiry]
    if "volume_spike_any" in data.columns:
        spikes = data[data["volume_spike_any"] == True]
        spikes = spikes.nlargest(n, "total_volume")
        return df_to_json(spikes[["datetime", "strike", "CE", "PE", "volume_CE",
                                   "volume_PE", "total_volume", "anomaly_score"]])
    return []


# ── 11. MAX PAIN ────────────────────────────────────────
@app.get("/api/max-pain", tags=["Analytics"])
def get_max_pain(timestamp: str = None, expiry: str = None):
    """Max Pain strike calculation."""
    data = _df.copy()
    if expiry:
        data = data[data["expiry"].dt.strftime("%Y-%m-%d") == expiry]
    ts = pd.Timestamp(timestamp) if timestamp else None
    result = compute_max_pain(data, timestamp=ts)
    if result:
        return {k: str(v) if isinstance(v, (pd.Timestamp, datetime)) else v
                for k, v in result.items()}
    raise HTTPException(status_code=404, detail="Could not compute max pain")


# ── 12. GREEKS ───────────────────────────────────────────
@app.get("/api/greeks", tags=["Volatility"])
def get_greeks(timestamp: str = None, expiry: str = None):
    """Option Greeks at a given snapshot."""
    data = _df.copy()
    if expiry:
        data = data[data["expiry"].dt.strftime("%Y-%m-%d") == expiry]
    if timestamp:
        data = data[data["datetime"] == pd.Timestamp(timestamp)]
    else:
        data = data[data["datetime"] == data["datetime"].max()]

    greek_cols = ["strike", "CE", "PE", "delta_CE", "delta_PE",
                  "gamma_CE", "gamma_PE", "theta_CE", "theta_PE",
                  "vega_CE", "vega_PE"]
    available = [c for c in greek_cols if c in data.columns]
    return df_to_json(data[available].sort_values("strike"))


# ── 13. VOLUME PROFILE ──────────────────────────────────
@app.get("/api/volume-profile", tags=["Analytics"])
def get_volume_profile(expiry: str = None):
    """Cumulative volume per strike."""
    data = _df.copy()
    if expiry:
        data = data[data["expiry"].dt.strftime("%Y-%m-%d") == expiry]
    vol = data.groupby("strike").agg(
        volume_CE=("volume_CE", "sum"),
        volume_PE=("volume_PE", "sum"),
    ).reset_index()
    vol["total_volume"] = vol["volume_CE"] + vol["volume_PE"]
    return df_to_json(vol.sort_values("strike"))


# ── 14. EVALUATION METRICS ──────────────────────────────
@app.get("/api/metrics", tags=["Evaluation"])
def get_metrics():
    """Full evaluation metrics for the platform."""
    # Make JSON-safe
    safe = {}
    for section, values in _metrics.items():
        if isinstance(values, dict):
            safe[section] = {}
            for k, v in values.items():
                if isinstance(v, (np.integer, np.int64)):
                    safe[section][k] = int(v)
                elif isinstance(v, (np.floating, np.float64)):
                    safe[section][k] = float(v) if not np.isnan(v) else None
                elif isinstance(v, np.bool_):
                    safe[section][k] = bool(v)
                else:
                    safe[section][k] = v
        else:
            safe[section] = values
    return safe


# ── 15. KEY METRICS (Dashboard Cards) ───────────────────
@app.get("/api/key-metrics", tags=["Dashboard"])
def get_key_metrics(expiry: str = None):
    """Key metrics for dashboard header cards."""
    data = _df.copy()
    if expiry:
        data = data[data["expiry"].dt.strftime("%Y-%m-%d") == expiry]

    latest = data[data["datetime"] == data["datetime"].max()]

    return {
        "spot_price": round(float(latest["spot_close"].iloc[0]), 2) if len(latest) > 0 else None,
        "atm_strike": float(latest["ATM"].iloc[0]) if len(latest) > 0 else None,
        "pcr_oi": round(float(latest["pcr_oi"].mean()), 4) if len(latest) > 0 else None,
        "total_oi": int(latest["total_oi"].sum()) if len(latest) > 0 else None,
        "total_volume": int(latest["total_volume"].sum()) if len(latest) > 0 else None,
        "anomalies_count": int(data["is_anomaly"].sum()) if "is_anomaly" in data.columns else 0,
        "volume_spikes": int(data["volume_spike_any"].sum()) if "volume_spike_any" in data.columns else 0,
        "sentiment": "Bullish" if (latest["pcr_oi"].mean() > 1.0 if len(latest) > 0 else False) else
                     "Bearish" if (latest["pcr_oi"].mean() < 0.7 if len(latest) > 0 else False) else "Neutral",
    }


# ── 16. RAW DATA (paginated) ────────────────────────────
@app.get("/api/data", tags=["Data"])
def get_raw_data(
    expiry: str = None,
    strike: float = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(100, le=1000),
):
    """Paginated raw data with optional filters."""
    data = _df.copy()
    if expiry:
        data = data[data["expiry"].dt.strftime("%Y-%m-%d") == expiry]
    if strike:
        data = data[data["strike"] == strike]

    total = len(data)
    start = (page - 1) * page_size
    end = start + page_size
    page_data = data.iloc[start:end]

    cols = ["datetime", "strike", "expiry", "CE", "PE", "spot_close", "ATM",
            "oi_CE", "oi_PE", "volume_CE", "volume_PE", "pcr_oi", "is_anomaly"]
    available = [c for c in cols if c in page_data.columns]

    return {
        "data": df_to_json(page_data[available]),
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size,
    }


# ── 17. OI HEATMAP DATA ─────────────────────────────────
@app.get("/api/oi-heatmap", tags=["Analytics"])
def get_oi_heatmap(oi_type: str = "oi_CE", expiry: str = None):
    """OI heatmap data (strike × time matrix)."""
    data = _df.copy()
    if expiry:
        data = data[data["expiry"].dt.strftime("%Y-%m-%d") == expiry]

    if oi_type not in ["oi_CE", "oi_PE"]:
        raise HTTPException(status_code=400, detail="oi_type must be 'oi_CE' or 'oi_PE'")

    pivot = data.pivot_table(
        index="strike", columns="datetime", values=oi_type, aggfunc="sum"
    ).fillna(0)

    # Subsample for performance
    if pivot.shape[1] > 100:
        step = max(1, pivot.shape[1] // 100)
        pivot = pivot.iloc[:, ::step]

    return {
        "strikes": pivot.index.tolist(),
        "timestamps": [str(t) for t in pivot.columns],
        "values": pivot.values.tolist(),
    }


# ═══════════════════════════════════════════════════════════
#  RUN
# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
