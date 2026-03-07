from fastapi import FastAPI, Query, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity
import requests
import json
import os
from typing import Optional
from datetime import datetime

app = FastAPI(title="OptionsAI Backend", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── MOCK DATA LAYER ────────────────────────────────────────────────────────
# All functions below are stubs that simulate DB/CSV output.
# Replace the return values with real DB/CSV reads when you connect your data.

def load_dataset() -> pd.DataFrame:
    """Replace this with actual CSV/DB read. Returns a mock options DataFrame."""
    np.random.seed(42)
    strikes = list(range(21000, 24001, 100))
    expiries = ["2025-01-30", "2025-02-27", "2025-03-27"]
    timestamps = pd.date_range("2025-01-01 09:15", periods=50, freq="15min")

    rows = []
    for ts in timestamps:
        spot = 22500 + np.random.normal(0, 200)
        for strike in strikes:
            for expiry in expiries:
                moneyness = (strike - spot) / spot
                iv = 0.18 + 0.05 * moneyness**2 + np.random.normal(0, 0.01)
                call_oi = max(0, int(np.random.exponential(5000) * (1 - abs(moneyness) * 2)))
                put_oi = max(0, int(np.random.exponential(5000) * (1 - abs(moneyness) * 2)))
                volume = max(0, int(np.random.exponential(2000) * (1 - abs(moneyness) * 3)))
                rows.append({
                    "timestamp": ts,
                    "strike": strike,
                    "expiry": expiry,
                    "spot_price": round(spot, 2),
                    "call_oi": call_oi,
                    "put_oi": put_oi,
                    "call_volume": volume,
                    "put_volume": int(volume * np.random.uniform(0.5, 1.5)),
                    "iv": round(max(0.05, iv), 4),
                })
    return pd.DataFrame(rows)

DF = load_dataset()

def get_latest_timestamp():
    return DF["timestamp"].max()

def get_atm_strike(spot):
    strikes = DF["strike"].unique()
    return min(strikes, key=lambda x: abs(x - spot))

# ─── TRANSLATION (MyMemory Free API) ────────────────────────────────────────

def translate_text(text: str, target_lang: str) -> str:
    """Uses MyMemory free API — no key needed, 5000 chars/day free."""
    if target_lang == "en":
        return text
    try:
        url = f"https://api.mymemory.translated.net/get"
        params = {"q": text, "langpair": f"en|{target_lang}"}
        r = requests.get(url, params=params, timeout=5)
        data = r.json()
        return data["responseData"]["translatedText"]
    except Exception:
        return text  # fallback to English on error

# ─── ROUTES ─────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"status": "OptionsAI backend running", "version": "1.0.0"}

@app.get("/dashboard/summary")
def dashboard_summary(accept_language: Optional[str] = Header(default="en")):
    """Returns key summary stats for the dashboard bottom bar."""
    ts = get_latest_timestamp()
    latest = DF[DF["timestamp"] == ts]
    spot = latest["spot_price"].iloc[0]
    atm = get_atm_strike(spot)

    total_call_oi = int(latest["call_oi"].sum())
    total_put_oi = int(latest["put_oi"].sum())
    total_volume = int((latest["call_volume"] + latest["put_volume"]).sum())
    pcr = round(total_put_oi / total_call_oi, 4) if total_call_oi else 0

    # Max Pain: strike where total OI value is minimized for option writers
    pain_scores = {}
    for strike in latest["strike"].unique():
        call_pain = latest[latest["strike"] >= strike]["call_oi"].sum() * abs(strike - spot)
        put_pain = latest[latest["strike"] <= strike]["put_oi"].sum() * abs(strike - spot)
        pain_scores[strike] = call_pain + put_pain
    max_pain = min(pain_scores, key=pain_scores.get)

    return {
        "timestamp": str(ts),
        "spot_price": round(spot, 2),
        "atm_strike": int(atm),
        "max_pain_strike": int(max_pain),
        "total_call_oi": total_call_oi,
        "total_put_oi": total_put_oi,
        "total_volume": total_volume,
        "pcr": pcr,
    }

@app.get("/dashboard/iv-curve")
def iv_curve(expiry: str = Query(default="2025-01-30"), timestamp: Optional[str] = None):
    """Returns IV across strikes for selected expiry."""
    ts = pd.to_datetime(timestamp) if timestamp else get_latest_timestamp()
    subset = DF[(DF["timestamp"] == ts) & (DF["expiry"] == expiry)]
    subset = subset.sort_values("strike")
    return {
        "strikes": subset["strike"].tolist(),
        "iv": subset["iv"].tolist(),
        "expiry": expiry,
    }

@app.get("/dashboard/surface")
def surface_data():
    """Returns 3D volatility surface data."""
    ts = get_latest_timestamp()
    subset = DF[DF["timestamp"] == ts].groupby(["strike", "expiry"])["iv"].mean().reset_index()
    expiries = sorted(subset["expiry"].unique().tolist())
    strikes = sorted(subset["strike"].unique().tolist())

    z = []
    for exp in expiries:
        row = []
        for s in strikes:
            val = subset[(subset["expiry"] == exp) & (subset["strike"] == s)]["iv"]
            row.append(float(val.iloc[0]) if len(val) > 0 else None)
        z.append(row)

    return {"strikes": strikes, "expiries": expiries, "z": z}

@app.get("/dashboard/oi-distribution")
def oi_distribution(timestamp: Optional[str] = None, expiry: Optional[str] = None):
    """Returns call vs put OI per strike."""
    ts = pd.to_datetime(timestamp) if timestamp else get_latest_timestamp()
    subset = DF[DF["timestamp"] == ts]
    if expiry:
        subset = subset[subset["expiry"] == expiry]
    grouped = subset.groupby("strike").agg(call_oi=("call_oi", "sum"), put_oi=("put_oi", "sum")).reset_index()
    return {
        "strikes": grouped["strike"].tolist(),
        "call_oi": grouped["call_oi"].tolist(),
        "put_oi": grouped["put_oi"].tolist(),
    }

@app.get("/dashboard/volume-heatmap")
def volume_heatmap():
    """Returns volume matrix for heatmap (strikes × time)."""
    grouped = DF.groupby(["timestamp", "strike"]).agg(
        volume=("call_volume", "sum")
    ).reset_index()
    pivoted = grouped.pivot(index="timestamp", columns="strike", values="volume").fillna(0)
    return {
        "timestamps": [str(t) for t in pivoted.index.tolist()],
        "strikes": [int(s) for s in pivoted.columns.tolist()],
        "values": pivoted.values.tolist(),
    }

@app.get("/dashboard/pcr-trend")
def pcr_trend():
    """Returns Put-Call Ratio over time."""
    grouped = DF.groupby("timestamp").agg(
        call_oi=("call_oi", "sum"), put_oi=("put_oi", "sum")
    ).reset_index()
    grouped["pcr"] = grouped["put_oi"] / grouped["call_oi"]
    return {
        "timestamps": [str(t) for t in grouped["timestamp"].tolist()],
        "pcr": grouped["pcr"].round(4).tolist(),
    }

@app.get("/dashboard/expiries")
def get_expiries():
    return {"expiries": sorted(DF["expiry"].unique().tolist())}

# ─── FINGERPRINT ENGINE ──────────────────────────────────────────────────────

def compute_fingerprint(subset: pd.DataFrame, spot: float) -> dict:
    """Compute 6-dim fingerprint vector for a given timestamp subset."""
    if subset.empty:
        return {}
    atm = get_atm_strike(spot)
    strikes = sorted(subset["strike"].unique())
    iv_by_strike = subset.groupby("strike")["iv"].mean()
    min_iv = iv_by_strike.get(min(strikes), 0.18)
    max_iv = iv_by_strike.get(max(strikes), 0.22)
    atm_iv = float(iv_by_strike.get(atm, 0.18))

    total_call_oi = subset["call_oi"].sum()
    total_put_oi = subset["put_oi"].sum()
    oi_ratio = float(total_call_oi / total_put_oi) if total_put_oi else 1.0

    total_vol = (subset["call_volume"] + subset["put_volume"]).sum()
    max_strike_vol = subset.groupby("strike").apply(lambda x: (x["call_volume"] + x["put_volume"]).sum()).max()
    vol_concentration = float(max_strike_vol / total_vol) if total_vol else 0

    expiries = sorted(subset["expiry"].unique())
    if len(expiries) >= 2:
        near_iv = subset[subset["expiry"] == expiries[0]]["iv"].mean()
        far_iv = subset[subset["expiry"] == expiries[-1]]["iv"].mean()
        term_slope = float(near_iv - far_iv)
    else:
        term_slope = 0.0

    atm_rows = subset[subset["strike"] == atm]
    atm_oi = atm_rows["call_oi"].sum() + atm_rows["put_oi"].sum()
    atm_vol = atm_rows["call_volume"].sum() + atm_rows["put_volume"].sum()
    vol_oi_divergence = float((atm_vol - atm_oi) / atm_oi) if atm_oi else 0

    return {
        "iv_skew": round(float(max_iv - min_iv), 4),
        "oi_ratio": round(oi_ratio, 4),
        "volume_concentration": round(vol_concentration, 4),
        "atm_iv": round(atm_iv, 4),
        "term_slope": round(term_slope, 4),
        "vol_oi_divergence": round(vol_oi_divergence, 4),
    }

@app.post("/fingerprint/compute")
def fingerprint_compute(body: dict = None):
    ts = get_latest_timestamp()
    subset = DF[DF["timestamp"] == ts]
    spot = subset["spot_price"].iloc[0]
    fp = compute_fingerprint(subset, spot)
    return {"timestamp": str(ts), "fingerprint": fp, "spot": round(float(spot), 2)}

@app.get("/fingerprint/match")
def fingerprint_match(timestamp: Optional[str] = None):
    """Finds top 3 historical fingerprint matches using cosine similarity."""
    ts = pd.to_datetime(timestamp) if timestamp else get_latest_timestamp()
    all_ts = sorted(DF["timestamp"].unique())

    vectors = []
    for t in all_ts:
        subset = DF[DF["timestamp"] == t]
        spot = subset["spot_price"].iloc[0]
        fp = compute_fingerprint(subset, spot)
        if fp:
            vectors.append({"timestamp": t, **fp})

    if not vectors:
        return {"matches": []}

    df_vec = pd.DataFrame(vectors).set_index("timestamp")
    keys = ["iv_skew", "oi_ratio", "volume_concentration", "atm_iv", "term_slope", "vol_oi_divergence"]
    df_vec = df_vec[keys].fillna(0)

    scaler = MinMaxScaler()
    normed = scaler.fit_transform(df_vec.values)
    df_normed = pd.DataFrame(normed, index=df_vec.index, columns=keys)

    current_vec = df_normed.loc[ts].values.reshape(1, -1) if ts in df_normed.index else normed[-1].reshape(1, -1)
    sims = cosine_similarity(current_vec, normed)[0]

    sim_series = pd.Series(sims, index=df_vec.index)
    sim_series = sim_series.drop(ts, errors="ignore")
    top3 = sim_series.nlargest(3)

    matches = []
    for match_ts, score in top3.items():
        subset = DF[DF["timestamp"] == match_ts]
        spot = subset["spot_price"].iloc[0]
        fp = compute_fingerprint(subset, spot)
        matches.append({
            "timestamp": str(match_ts),
            "similarity": round(float(score) * 100, 1),
            "fingerprint": fp,
            "spot": round(float(spot), 2),
        })

    current_subset = DF[DF["timestamp"] == ts]
    current_spot = current_subset["spot_price"].iloc[0]
    current_fp = compute_fingerprint(current_subset, current_spot)

    return {
        "current_timestamp": str(ts),
        "current_fingerprint": current_fp,
        "matches": matches
    }

@app.get("/fingerprint/outcome")
def fingerprint_outcome(match_timestamp: str):
    """Returns what happened after a historical match."""
    ts = pd.to_datetime(match_timestamp)
    all_ts = sorted(DF["timestamp"].unique())
    idx = list(all_ts).index(ts) if ts in all_ts else -1

    outcomes = []
    for i in range(1, 4):
        if idx + i < len(all_ts):
            next_ts = all_ts[idx + i]
            subset = DF[DF["timestamp"] == next_ts]
            spot = float(subset["spot_price"].iloc[0])
            avg_iv = float(subset["iv"].mean())
            total_call_oi = int(subset["call_oi"].sum())
            total_put_oi = int(subset["put_oi"].sum())
            outcomes.append({
                "timestamp": str(next_ts),
                "spot": round(spot, 2),
                "avg_iv": round(avg_iv, 4),
                "call_oi": total_call_oi,
                "put_oi": total_put_oi,
            })

    return {"match_timestamp": match_timestamp, "outcomes": outcomes}

# ─── TRAP DETECTOR ───────────────────────────────────────────────────────────

@app.get("/trap/current")
def trap_current(accept_language: Optional[str] = Header(default="en")):
    """Detects current positioning trap."""
    ts = get_latest_timestamp()
    subset = DF[DF["timestamp"] == ts]
    grouped = subset.groupby("strike").agg(call_oi=("call_oi", "sum"), put_oi=("put_oi", "sum")).reset_index()
    grouped["total_oi"] = grouped["call_oi"] + grouped["put_oi"]
    grouped["call_dominance"] = grouped["call_oi"] / grouped["total_oi"].replace(0, 1)

    total_oi = grouped["total_oi"].sum()
    mean_dom = grouped["call_dominance"].mean()
    std_dom = grouped["call_dominance"].std()

    traps = []
    for _, row in grouped.iterrows():
        if row["call_dominance"] > 0.75:
            score = min(100, int((row["call_dominance"] - 0.75) / 0.25 * 100))
            traps.append({"strike": int(row["strike"]), "side": "CALLS", "score": score,
                          "oi": int(row["total_oi"]), "dominance": round(float(row["call_dominance"]), 3)})
        elif row["call_dominance"] < 0.25:
            score = min(100, int((0.25 - row["call_dominance"]) / 0.25 * 100))
            traps.append({"strike": int(row["strike"]), "side": "PUTS", "score": score,
                          "oi": int(row["total_oi"]), "dominance": round(float(row["call_dominance"]), 3)})

    if not traps:
        status = "GREEN"
        message = "No significant positioning trap detected. Market positioning is balanced."
    else:
        top = max(traps, key=lambda x: x["score"])
        status = "RED" if top["score"] > 70 else "YELLOW"
        message = f"Heavy {top['side']} concentration at strike {top['strike']}. Crowding score: {top['score']}/100."
        if accept_language not in ["en", None]:
            message = translate_text(message, accept_language)

    return {
        "status": status,
        "timestamp": str(ts),
        "message": message,
        "traps": sorted(traps, key=lambda x: -x["score"])[:5],
    }

@app.get("/trap/chain")
def trap_chain():
    """Full OI chain data for heatmap."""
    ts = get_latest_timestamp()
    subset = DF[DF["timestamp"] == ts]
    grouped = subset.groupby("strike").agg(call_oi=("call_oi", "sum"), put_oi=("put_oi", "sum")).reset_index()
    return {
        "strikes": grouped["strike"].tolist(),
        "call_oi": grouped["call_oi"].tolist(),
        "put_oi": grouped["put_oi"].tolist(),
    }

@app.get("/trap/history")
def trap_history():
    """Historical trap events (stub — connect real DB for history)."""
    return {
        "events": [
            {"date": "2025-01-15 10:30", "strike_zone": "22000-22500", "side": "CALLS",
             "score": 82, "resolved_in": "3 candles", "outcome": "Price dropped 180 pts"},
            {"date": "2025-01-10 13:45", "strike_zone": "21500-22000", "side": "PUTS",
             "score": 74, "resolved_in": "5 candles", "outcome": "Price rose 220 pts"},
            {"date": "2024-12-28 11:00", "strike_zone": "23000-23500", "side": "CALLS",
             "score": 91, "resolved_in": "2 candles", "outcome": "Violent 300 pt reversal"},
        ]
    }

# ─── TRANSLATION ENDPOINT ────────────────────────────────────────────────────

@app.post("/translate")
def translate(body: dict):
    text = body.get("text", "")
    target_lang = body.get("target_lang", "en")
    translated = translate_text(text, target_lang)
    return {"original": text, "translated": translated, "lang": target_lang}

# ─── AI INSIGHTS (Hugging Face Inference API — free) ─────────────────────────

@app.post("/ai/insight")
def ai_insight(body: dict):
    """
    Calls Hugging Face free Inference API for text generation.
    Model: mistralai/Mistral-7B-Instruct-v0.3 (free tier).
    Replace HF_TOKEN with your free Hugging Face token.
    """
    prompt = body.get("prompt", "Explain the current options market conditions.")
    HF_TOKEN = os.getenv("HF_TOKEN", "")  # Set this env var — free HF token

    try:
        headers = {"Authorization": f"Bearer {HF_TOKEN}"} if HF_TOKEN else {}
        payload = {
            "inputs": f"<s>[INST] You are an expert options market analyst. Answer briefly and clearly. {prompt} [/INST]",
            "parameters": {"max_new_tokens": 300, "temperature": 0.7}
        }
        r = requests.post(
            "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.3",
            headers=headers,
            json=payload,
            timeout=30
        )
        data = r.json()
        if isinstance(data, list) and data:
            text = data[0].get("generated_text", "")
            # Strip the prompt echo
            if "[/INST]" in text:
                text = text.split("[/INST]")[-1].strip()
            return {"insight": text}
        return {"insight": "AI model is warming up. Please try again in a moment."}
    except Exception as e:
        return {"insight": f"AI service temporarily unavailable. Data is live."}

# ─── ANOMALY DETECTION (via HF zero-shot or rule-based fallback) ─────────────

@app.get("/anomaly/detect")
def anomaly_detect():
    """
    Rule-based anomaly detection using Z-score on OI and volume.
    Integrate with HF or OpenRouter for AI-enhanced descriptions.
    """
    ts = get_latest_timestamp()
    subset = DF[DF["timestamp"] == ts].copy()
    subset["total_oi"] = subset["call_oi"] + subset["put_oi"]
    subset["total_vol"] = subset["call_volume"] + subset["put_volume"]

    oi_mean, oi_std = subset["total_oi"].mean(), subset["total_oi"].std()
    vol_mean, vol_std = subset["total_vol"].mean(), subset["total_vol"].std()

    subset["oi_zscore"] = (subset["total_oi"] - oi_mean) / (oi_std + 1e-9)
    subset["vol_zscore"] = (subset["total_vol"] - vol_mean) / (vol_std + 1e-9)

    anomalies = subset[(subset["oi_zscore"].abs() > 2) | (subset["vol_zscore"].abs() > 2)]

    results = []
    for _, row in anomalies.head(10).iterrows():
        results.append({
            "strike": int(row["strike"]),
            "expiry": row["expiry"],
            "oi_zscore": round(float(row["oi_zscore"]), 2),
            "vol_zscore": round(float(row["vol_zscore"]), 2),
            "call_oi": int(row["call_oi"]),
            "put_oi": int(row["put_oi"]),
            "iv": round(float(row["iv"]), 4),
            "anomaly_type": "HIGH_OI" if abs(row["oi_zscore"]) > abs(row["vol_zscore"]) else "HIGH_VOLUME",
        })

    return {"timestamp": str(ts), "anomalies": results, "total_found": len(results)}