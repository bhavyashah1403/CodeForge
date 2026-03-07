"""
Analytics Module
────────────────
AI-powered anomaly detection, pattern analysis, and market insights.
Uses Scikit-learn Isolation Forest for unsupervised anomaly detection,
KMeans clustering for activity patterns, and statistical methods for
volatility skew/smile detection plus time-series pattern recognition.
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from config import (
    ISOLATION_FOREST_CONTAMINATION,
    VOLUME_SPIKE_THRESHOLD,
    OI_CHANGE_THRESHOLD,
)


# ═══════════════════════════════════════════════════════════
#  ANOMALY DETECTION (Isolation Forest)
# ═══════════════════════════════════════════════════════════

def detect_anomalies_isolation_forest(
    df: pd.DataFrame,
    features: list[str] = None,
    contamination: float = ISOLATION_FOREST_CONTAMINATION,
) -> pd.DataFrame:
    """
    Detect anomalies using Isolation Forest (unsupervised ML).
    Flags unusual combinations of volume, OI, and price movements.
    """
    print("[Analytics] Running Isolation Forest anomaly detection...")

    if features is None:
        features = ["CE", "PE", "oi_CE", "oi_PE", "volume_CE", "volume_PE",
                     "total_oi", "total_volume", "pcr_oi"]

    # Keep only available features
    available = [f for f in features if f in df.columns]
    if not available:
        print("[Analytics] WARNING: No features available for anomaly detection")
        df["anomaly_score"] = 0
        df["is_anomaly"] = False
        return df

    # Prepare feature matrix (drop NaN rows for fitting)
    X = df[available].copy()
    mask = X.notna().all(axis=1)
    X_clean = X[mask]

    # Standardize
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_clean)

    # Fit Isolation Forest
    iso_forest = IsolationForest(
        contamination=contamination,
        random_state=42,
        n_estimators=100,
        n_jobs=-1,
    )
    predictions = iso_forest.fit_predict(X_scaled)
    scores = iso_forest.decision_function(X_scaled)

    # Map back to DataFrame
    df["anomaly_score"] = np.nan
    df["is_anomaly"] = False
    df.loc[mask, "anomaly_score"] = scores
    df.loc[mask, "is_anomaly"] = predictions == -1

    n_anomalies = df["is_anomaly"].sum()
    print(f"[Analytics] Detected {n_anomalies:,} anomalies ({n_anomalies/len(df)*100:.1f}%)")
    return df


# ═══════════════════════════════════════════════════════════
#  VOLUME SPIKE DETECTION
# ═══════════════════════════════════════════════════════════

def detect_volume_spikes(
    df: pd.DataFrame,
    threshold: float = VOLUME_SPIKE_THRESHOLD,
) -> pd.DataFrame:
    """
    Flag unusual volume spikes using z-score method.
    A spike = volume > threshold × std above mean for that strike/expiry.
    """
    print("[Analytics] Detecting volume spikes...")

    for col in ["volume_CE", "volume_PE"]:
        grouped = df.groupby(["strike", "expiry"])[col]
        mean = grouped.transform("mean")
        std = grouped.transform("std").fillna(1)

        z_score = (df[col] - mean) / std
        spike_col = f"{col}_spike"
        df[spike_col] = z_score > threshold

    df["volume_spike_any"] = df["volume_CE_spike"] | df["volume_PE_spike"]
    n_spikes = df["volume_spike_any"].sum()
    print(f"[Analytics] Found {n_spikes:,} volume spikes")
    return df


# ═══════════════════════════════════════════════════════════
#  OI-BASED ANALYSIS
# ═══════════════════════════════════════════════════════════

def detect_unusual_oi_changes(
    df: pd.DataFrame,
    threshold: float = OI_CHANGE_THRESHOLD,
) -> pd.DataFrame:
    """Detect unusual OI build-up or unwinding."""
    print("[Analytics] Detecting unusual OI changes...")

    for col in ["oi_CE_change", "oi_PE_change"]:
        if col not in df.columns:
            continue
        mean = df[col].mean()
        std = df[col].std()
        if std > 0:
            z_score = (df[col] - mean) / std
            df[f"{col}_unusual"] = z_score.abs() > threshold

    oi_unusual_cols = [c for c in df.columns if c.endswith("_unusual")]
    if oi_unusual_cols:
        df["oi_unusual_any"] = df[oi_unusual_cols].any(axis=1)
        n_unusual = df["oi_unusual_any"].sum()
        print(f"[Analytics] Found {n_unusual:,} unusual OI changes")

    return df


# ═══════════════════════════════════════════════════════════
#  AGGREGATED ANALYTICS / SNAPSHOTS
# ═══════════════════════════════════════════════════════════

def compute_pcr_timeseries(df: pd.DataFrame) -> pd.DataFrame:
    """Compute aggregated PCR over time for market sentiment tracking."""
    print("[Analytics] Computing PCR timeseries...")

    pcr_ts = df.groupby("datetime").agg(
        total_oi_CE=("oi_CE", "sum"),
        total_oi_PE=("oi_PE", "sum"),
        total_vol_CE=("volume_CE", "sum"),
        total_vol_PE=("volume_PE", "sum"),
        spot=("spot_close", "first"),
    ).reset_index()

    pcr_ts["pcr_oi"] = pcr_ts["total_oi_PE"] / pcr_ts["total_oi_CE"].replace(0, np.nan)
    pcr_ts["pcr_volume"] = pcr_ts["total_vol_PE"] / pcr_ts["total_vol_CE"].replace(0, np.nan)

    print(f"[Analytics] PCR timeseries: {len(pcr_ts)} timestamps")
    return pcr_ts


def compute_oi_distribution(df: pd.DataFrame, timestamp=None) -> pd.DataFrame:
    """Get OI distribution across strikes at a given timestamp (or latest)."""
    if timestamp is None:
        timestamp = df["datetime"].max()

    snapshot = df[df["datetime"] == timestamp].copy()
    oi_dist = snapshot.groupby("strike").agg(
        oi_CE=("oi_CE", "sum"),
        oi_PE=("oi_PE", "sum"),
        volume_CE=("volume_CE", "sum"),
        volume_PE=("volume_PE", "sum"),
    ).reset_index()

    oi_dist["total_oi"] = oi_dist["oi_CE"] + oi_dist["oi_PE"]
    return oi_dist


def compute_max_pain(df: pd.DataFrame, timestamp=None) -> dict:
    """
    Calculate Max Pain strike price.
    Max Pain = strike where total loss for option writers is minimized.
    """
    if timestamp is None:
        timestamp = df["datetime"].max()

    snapshot = df[df["datetime"] == timestamp].copy()
    strikes = snapshot["strike"].unique()
    spot = snapshot["spot_close"].iloc[0] if len(snapshot) > 0 else np.nan

    pain_values = {}
    for strike in strikes:
        row = snapshot[snapshot["strike"] == strike]
        if row.empty:
            continue

        # Total CE pain: sum of (max(spot - K, 0) * oi_CE) for all strikes
        ce_pain = 0
        pe_pain = 0
        for _, r in snapshot.iterrows():
            ce_pain += max(strike - r["strike"], 0) * r["oi_CE"]
            pe_pain += max(r["strike"] - strike, 0) * r["oi_PE"]

        pain_values[strike] = ce_pain + pe_pain

    if pain_values:
        max_pain_strike = min(pain_values, key=pain_values.get)
        return {
            "max_pain_strike": max_pain_strike,
            "spot_price": spot,
            "distance_from_spot": max_pain_strike - spot,
            "timestamp": timestamp,
        }
    return {}


def get_top_anomalies(df: pd.DataFrame, n: int = 20) -> pd.DataFrame:
    """Get top N most anomalous data points."""
    if "anomaly_score" not in df.columns:
        return pd.DataFrame()
    anomalies = df[df["is_anomaly"] == True].nsmallest(n, "anomaly_score")
    return anomalies[["datetime", "strike", "expiry", "CE", "PE",
                       "spot_close", "oi_CE", "oi_PE", "volume_CE",
                       "volume_PE", "anomaly_score"]].reset_index(drop=True)


# ═══════════════════════════════════════════════════════════
#  EVALUATION METRICS
# ═══════════════════════════════════════════════════════════

def compute_evaluation_metrics(df: pd.DataFrame) -> dict:
    """
    Compute comprehensive evaluation metrics for the analytics platform.
    Covers: data quality, model performance, feature coverage, and insights quality.
    """
    from sklearn.metrics import silhouette_score
    from sklearn.preprocessing import StandardScaler

    metrics = {}

    # ── 1. DATA QUALITY METRICS ──────────────────────────
    total_rows = len(df)
    null_pct = (df.isnull().sum().sum() / (total_rows * len(df.columns))) * 100
    duplicate_pct = (1 - df.drop_duplicates(subset=["datetime", "strike", "expiry"]).shape[0] / total_rows) * 100

    metrics["data_quality"] = {
        "total_rows": total_rows,
        "total_columns": len(df.columns),
        "null_percentage": round(null_pct, 4),
        "duplicate_percentage": round(duplicate_pct, 4),
        "date_range_days": (df["datetime"].max() - df["datetime"].min()).days,
        "unique_strikes": int(df["strike"].nunique()),
        "unique_timestamps": int(df["datetime"].nunique()),
        "unique_expiries": int(df["expiry"].nunique()),
        "completeness_score": round(100 - null_pct, 2),
    }

    # ── 2. ANOMALY DETECTION METRICS (Isolation Forest) ──
    if "anomaly_score" in df.columns and "is_anomaly" in df.columns:
        anomaly_df = df.dropna(subset=["anomaly_score"])
        n_anomalies = anomaly_df["is_anomaly"].sum()
        n_normal = len(anomaly_df) - n_anomalies

        # Silhouette Score: measures cluster separation quality (-1 to 1)
        # Higher = better separation between anomalies and normal points
        feature_cols = ["CE", "PE", "oi_CE", "oi_PE", "volume_CE", "volume_PE",
                        "total_oi", "total_volume", "pcr_oi"]
        available_feats = [f for f in feature_cols if f in df.columns]
        silhouette = np.nan

        if n_anomalies > 1 and n_normal > 1 and available_feats:
            try:
                sample = anomaly_df.sample(min(5000, len(anomaly_df)), random_state=42)
                X = sample[available_feats].fillna(0)
                scaler = StandardScaler()
                X_scaled = scaler.fit_transform(X)
                labels = sample["is_anomaly"].astype(int).values
                silhouette = round(silhouette_score(X_scaled, labels, sample_size=min(2000, len(X_scaled))), 4)
            except Exception:
                silhouette = np.nan

        # Anomaly score distribution stats
        scores = anomaly_df["anomaly_score"]
        metrics["anomaly_detection"] = {
            "model": "Isolation Forest (sklearn)",
            "n_estimators": 100,
            "contamination": ISOLATION_FOREST_CONTAMINATION,
            "total_samples": int(len(anomaly_df)),
            "anomalies_detected": int(n_anomalies),
            "normal_points": int(n_normal),
            "anomaly_rate_pct": round(n_anomalies / len(anomaly_df) * 100, 2),
            "silhouette_score": silhouette,
            "mean_anomaly_score": round(scores.mean(), 4),
            "std_anomaly_score": round(scores.std(), 4),
            "min_anomaly_score": round(scores.min(), 4),
            "max_anomaly_score": round(scores.max(), 4),
            "median_anomaly_score": round(scores.median(), 4),
        }

    # ── 3. VOLUME SPIKE DETECTION METRICS ────────────────
    if "volume_spike_any" in df.columns:
        n_spikes = df["volume_spike_any"].sum()
        metrics["volume_spike_detection"] = {
            "method": "Z-Score Threshold",
            "threshold": VOLUME_SPIKE_THRESHOLD,
            "total_spikes": int(n_spikes),
            "spike_rate_pct": round(n_spikes / total_rows * 100, 2),
            "ce_spikes": int(df["volume_CE_spike"].sum()) if "volume_CE_spike" in df.columns else 0,
            "pe_spikes": int(df["volume_PE_spike"].sum()) if "volume_PE_spike" in df.columns else 0,
        }

    # ── 4. OI CHANGE DETECTION METRICS ───────────────────
    if "oi_unusual_any" in df.columns:
        n_oi_unusual = df["oi_unusual_any"].sum()
        metrics["oi_change_detection"] = {
            "method": "Z-Score Threshold",
            "threshold": OI_CHANGE_THRESHOLD,
            "unusual_changes": int(n_oi_unusual),
            "unusual_rate_pct": round(n_oi_unusual / total_rows * 100, 2),
        }

    # ── 5. IMPLIED VOLATILITY METRICS ────────────────────
    if "iv_CE" in df.columns:
        iv_valid = df["iv_CE"].notna().sum() + df["iv_PE"].notna().sum()
        iv_coverage = iv_valid / (total_rows * 2) * 100

        iv_ce_valid = df["iv_CE"].dropna()
        iv_pe_valid = df["iv_PE"].dropna()

        metrics["implied_volatility"] = {
            "method": "Newton-Raphson (Black-Scholes)",
            "iv_coverage_pct": round(iv_coverage, 2),
            "valid_iv_values": int(iv_valid),
            "mean_iv_CE": round(iv_ce_valid.mean() * 100, 2) if len(iv_ce_valid) > 0 else None,
            "mean_iv_PE": round(iv_pe_valid.mean() * 100, 2) if len(iv_pe_valid) > 0 else None,
            "iv_CE_std": round(iv_ce_valid.std() * 100, 2) if len(iv_ce_valid) > 0 else None,
            "iv_PE_std": round(iv_pe_valid.std() * 100, 2) if len(iv_pe_valid) > 0 else None,
        }

    # ── 6. FEATURE ENGINEERING COVERAGE ──────────────────
    derived_features = [
        "moneyness", "time_to_expiry_days", "intrinsic_CE", "intrinsic_PE",
        "extrinsic_CE", "extrinsic_PE", "pcr_oi", "pcr_volume", "total_oi",
        "total_volume", "distance_from_atm", "iv_CE", "iv_PE",
        "delta_CE", "gamma_CE", "theta_CE", "vega_CE",
        "delta_PE", "gamma_PE", "theta_PE", "vega_PE",
        "oi_CE_change", "oi_PE_change", "vol_CE_ma5", "vol_PE_ma5",
        "vol_CE_ratio", "vol_PE_ratio", "relative_strike", "iv_spread",
    ]
    present = [f for f in derived_features if f in df.columns]
    metrics["feature_engineering"] = {
        "total_derived_features": len(present),
        "expected_features": len(derived_features),
        "coverage_pct": round(len(present) / len(derived_features) * 100, 1),
        "features_present": present,
    }

    # ── 7. CROSS-VALIDATION: ANOMALY vs VOLUME SPIKES ───
    if "is_anomaly" in df.columns and "volume_spike_any" in df.columns:
        both = (df["is_anomaly"] & df["volume_spike_any"]).sum()
        anomaly_only = (df["is_anomaly"] & ~df["volume_spike_any"]).sum()
        spike_only = (~df["is_anomaly"] & df["volume_spike_any"]).sum()
        neither = (~df["is_anomaly"] & ~df["volume_spike_any"]).sum()

        # Overlap: how much do anomalies and spikes agree?
        total_flagged = both + anomaly_only + spike_only
        overlap_pct = (both / total_flagged * 100) if total_flagged > 0 else 0

        metrics["cross_validation"] = {
            "anomaly_and_spike": int(both),
            "anomaly_only": int(anomaly_only),
            "spike_only": int(spike_only),
            "neither": int(neither),
            "overlap_pct": round(overlap_pct, 2),
            "interpretation": "Higher overlap = anomaly detector captures volume spikes well",
        }

    return metrics


def print_evaluation_metrics(metrics: dict) -> None:
    """Pretty-print evaluation metrics."""
    for section, values in metrics.items():
        print(f"\n{'─' * 50}")
        print(f"  {section.upper().replace('_', ' ')}")
        print(f"{'─' * 50}")
        if isinstance(values, dict):
            for k, v in values.items():
                if isinstance(v, list) and len(v) > 5:
                    print(f"  {k}: [{len(v)} features]")
                else:
                    print(f"  {k}: {v}")


# ═══════════════════════════════════════════════════════════
#  FULL ANALYTICS PIPELINE
# ═══════════════════════════════════════════════════════════

def analytics_pipeline(df: pd.DataFrame) -> pd.DataFrame:
    """Run all analytics on the enriched dataset."""
    print("\n" + "=" * 60)
    print("   ANALYTICS PIPELINE")
    print("=" * 60)

    df = detect_anomalies_isolation_forest(df)
    df = detect_volume_spikes(df)
    df = detect_unusual_oi_changes(df)
    df = cluster_market_activity(df)

    print("=" * 60 + "\n")
    return df


# ═══════════════════════════════════════════════════════════
#  KMEANS CLUSTERING (Strike × Expiry Activity Patterns)
# ═══════════════════════════════════════════════════════════

def cluster_market_activity(
    df: pd.DataFrame,
    n_clusters: int = 4,
) -> pd.DataFrame:
    """
    Cluster market activity patterns across strikes/expiries using KMeans.
    Identifies groups: high-activity, low-activity, hedging zones, speculative zones.
    """
    print("[Analytics] Running KMeans clustering on market activity...")

    features = ["total_oi", "total_volume", "pcr_oi", "CE", "PE"]
    available = [f for f in features if f in df.columns]
    if len(available) < 2:
        df["activity_cluster"] = 0
        return df

    X = df[available].copy().fillna(0)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    df["activity_cluster"] = kmeans.fit_predict(X_scaled)

    # Label clusters by mean total_volume
    cluster_means = df.groupby("activity_cluster")["total_volume"].mean()
    rank = cluster_means.rank(ascending=True).astype(int)
    label_map = {c: ["Low Activity", "Moderate Activity", "High Activity", "Extreme Activity"][min(r - 1, 3)]
                 for c, r in rank.items()}
    df["cluster_label"] = df["activity_cluster"].map(label_map)

    for label, count in df["cluster_label"].value_counts().items():
        print(f"[Analytics]   {label}: {count:,} rows")

    return df


# ═══════════════════════════════════════════════════════════
#  VOLATILITY SKEW / SMILE PATTERN DETECTION
# ═══════════════════════════════════════════════════════════

def detect_volatility_patterns(df: pd.DataFrame) -> dict:
    """
    Detect volatility skew/smile patterns from IV data.
    Returns structured pattern analysis.
    """
    print("[Analytics] Detecting volatility patterns...")

    patterns = {
        "skew_detected": False,
        "smile_detected": False,
        "skew_direction": None,
        "smile_curvature": None,
        "iv_term_structure": [],
        "skew_by_expiry": [],
    }

    if "iv_CE" not in df.columns or "iv_PE" not in df.columns:
        return patterns

    # Get latest timestamp for snapshot analysis
    latest_ts = df["datetime"].max()
    snapshot = df[df["datetime"] == latest_ts].copy()
    snapshot = snapshot.dropna(subset=["iv_CE", "iv_PE"])

    if len(snapshot) < 5:
        return patterns

    # Sort by strike
    snapshot = snapshot.sort_values("strike")

    # ── 1. Skew Detection ───────────────────────────
    # Compare OTM put IV vs OTM call IV
    atm = snapshot["ATM"].iloc[0]
    otm_puts = snapshot[snapshot["strike"] < atm * 0.98]
    otm_calls = snapshot[snapshot["strike"] > atm * 1.02]

    if len(otm_puts) > 0 and len(otm_calls) > 0:
        put_iv_mean = otm_puts["iv_PE"].mean()
        call_iv_mean = otm_calls["iv_CE"].mean()

        if put_iv_mean > 0 and call_iv_mean > 0:
            skew_ratio = put_iv_mean / call_iv_mean
            patterns["skew_detected"] = abs(skew_ratio - 1.0) > 0.1
            patterns["skew_direction"] = "put_skew" if skew_ratio > 1.1 else (
                "call_skew" if skew_ratio < 0.9 else "neutral"
            )
            patterns["skew_ratio"] = round(float(skew_ratio), 4)
            patterns["otm_put_iv_avg"] = round(float(put_iv_mean * 100), 2)
            patterns["otm_call_iv_avg"] = round(float(call_iv_mean * 100), 2)

    # ── 2. Smile Detection ──────────────────────────
    # Fit quadratic to IV vs moneyness to detect curvature
    if "relative_strike" in snapshot.columns:
        iv_avg = snapshot["iv_avg"].dropna()
        rel_strike = snapshot.loc[iv_avg.index, "relative_strike"]

        if len(iv_avg) > 3:
            try:
                coeffs = np.polyfit(rel_strike, iv_avg, 2)
                curvature = coeffs[0]  # quadratic coefficient
                patterns["smile_detected"] = curvature > 0.05
                patterns["smile_curvature"] = round(float(curvature), 6)
                patterns["smile_vertex"] = round(float(-coeffs[1] / (2 * coeffs[0])), 4) if coeffs[0] != 0 else 0
            except (np.linalg.LinAlgError, ValueError):
                pass

    # ── 3. IV Term Structure (across expiries) ──────
    for expiry in df["expiry"].unique():
        exp_data = df[(df["expiry"] == expiry) & (df["datetime"] == latest_ts)]
        exp_data = exp_data.dropna(subset=["iv_CE", "iv_PE"])
        if len(exp_data) > 0:
            patterns["iv_term_structure"].append({
                "expiry": str(expiry),
                "mean_iv_CE": round(float(exp_data["iv_CE"].mean() * 100), 2),
                "mean_iv_PE": round(float(exp_data["iv_PE"].mean() * 100), 2),
                "atm_iv": round(float(exp_data.loc[
                    (exp_data["strike"] - exp_data["ATM"]).abs().idxmin(), "iv_avg"
                ] * 100), 2) if len(exp_data) > 0 else None,
            })

    # ── 4. Skew by Expiry ───────────────────────────
    for expiry in df["expiry"].unique():
        exp_data = df[(df["expiry"] == expiry) & (df["datetime"] == latest_ts)]
        exp_data = exp_data.dropna(subset=["iv_CE", "iv_PE"]).sort_values("strike")
        if len(exp_data) > 5:
            atm_e = exp_data["ATM"].iloc[0]
            puts_e = exp_data[exp_data["strike"] < atm_e * 0.98]["iv_PE"]
            calls_e = exp_data[exp_data["strike"] > atm_e * 1.02]["iv_CE"]
            if len(puts_e) > 0 and len(calls_e) > 0:
                patterns["skew_by_expiry"].append({
                    "expiry": str(expiry),
                    "put_iv_avg": round(float(puts_e.mean() * 100), 2),
                    "call_iv_avg": round(float(calls_e.mean() * 100), 2),
                    "skew": round(float((puts_e.mean() - calls_e.mean()) * 100), 2),
                })

    return patterns


# ═══════════════════════════════════════════════════════════
#  IV SPIKE / SHIFT DETECTION
# ═══════════════════════════════════════════════════════════

def detect_iv_spikes(df: pd.DataFrame, threshold: float = 2.0) -> list[dict]:
    """
    Detect sudden spikes or shifts in implied volatility.
    Compares IV changes across consecutive timestamps per strike.
    """
    print("[Analytics] Detecting IV spikes/shifts...")

    spikes = []
    if "iv_CE" not in df.columns:
        return spikes

    sorted_df = df.sort_values(["strike", "expiry", "datetime"]).copy()

    for iv_col, opt_type in [("iv_CE", "Call"), ("iv_PE", "Put")]:
        grouped = sorted_df.groupby(["strike", "expiry"])[iv_col]
        iv_change = grouped.diff()
        iv_mean = grouped.transform("mean")
        iv_std = grouped.transform("std").fillna(0.001)

        z_scores = (iv_change / iv_std).fillna(0)
        spike_mask = z_scores.abs() > threshold

        spike_rows = sorted_df[spike_mask].head(50)  # top 50 spikes
        for _, row in spike_rows.iterrows():
            spikes.append({
                "datetime": str(row["datetime"]),
                "strike": float(row["strike"]),
                "expiry": str(row["expiry"]),
                "option_type": opt_type,
                "iv_value": round(float(row[iv_col] * 100), 2) if pd.notna(row[iv_col]) else None,
                "iv_change_zscore": round(float(z_scores.loc[row.name]), 2),
                "severity": "high" if abs(z_scores.loc[row.name]) > 3 else "medium",
            })

    spikes.sort(key=lambda x: abs(x.get("iv_change_zscore", 0)), reverse=True)
    print(f"[Analytics] Found {len(spikes)} IV spike events")
    return spikes[:30]


# ═══════════════════════════════════════════════════════════
#  AI-DRIVEN INSIGHT GENERATION
# ═══════════════════════════════════════════════════════════

def generate_ai_insights(df: pd.DataFrame) -> list[dict]:
    """
    Generate actionable AI-driven insights from analyzed data.
    Combines anomaly detection, volume analysis, OI patterns,
    volatility patterns, and sentiment analysis.
    """
    print("[Analytics] Generating AI insights...")
    insights = []
    insight_id = 1

    latest_ts = df["datetime"].max()
    latest = df[df["datetime"] == latest_ts]

    # ── 1. Sentiment Analysis ────────────────────────
    if "pcr_oi" in df.columns:
        pcr_mean = latest["pcr_oi"].mean()
        pcr_prev = df[df["datetime"] < latest_ts].groupby("datetime")["pcr_oi"].mean()
        if len(pcr_prev) > 1:
            pcr_prev_val = pcr_prev.iloc[-1] if len(pcr_prev) > 0 else pcr_mean
            pcr_change = pcr_mean - pcr_prev_val

            if abs(pcr_change) > 0.1:
                direction = "bullish" if pcr_change > 0 else "bearish"
                insights.append({
                    "id": insight_id, "type": direction,
                    "title": "Sentiment Shift Detected",
                    "description": f"PCR moved from {pcr_prev_val:.2f} to {pcr_mean:.2f} "
                                   f"({'increased' if pcr_change > 0 else 'decreased'} by {abs(pcr_change):.2f}). "
                                   f"This suggests a shift toward {'bullish' if pcr_change > 0 else 'bearish'} sentiment "
                                   f"as {'puts' if pcr_change > 0 else 'calls'} are being {'written' if pcr_change > 0 else 'bought'} aggressively.",
                    "timestamp": str(latest_ts),
                    "severity": "high" if abs(pcr_change) > 0.3 else "medium",
                })
                insight_id += 1

    # ── 2. Anomaly Hotspots ──────────────────────────
    if "is_anomaly" in df.columns:
        anomalies = latest[latest["is_anomaly"] == True]
        if len(anomalies) > 0:
            top_anomaly = anomalies.nsmallest(1, "anomaly_score").iloc[0]
            anomaly_strikes = anomalies["strike"].value_counts().head(3)
            strike_list = ", ".join([str(int(s)) for s in anomaly_strikes.index])

            insights.append({
                "id": insight_id, "type": "anomaly",
                "title": "Anomaly Detected",
                "description": f"AI detected {len(anomalies)} anomalous data points at the latest timestamp. "
                               f"Most anomalous strike: {int(top_anomaly['strike'])} with score {top_anomaly['anomaly_score']:.4f}. "
                               f"Top affected strikes: {strike_list}. "
                               f"This may indicate unusual institutional activity or hedging.",
                "timestamp": str(latest_ts),
                "severity": "high",
            })
            insight_id += 1

    # ── 3. Volume Spike Alerts ───────────────────────
    if "volume_spike_any" in df.columns:
        spikes = latest[latest["volume_spike_any"] == True]
        if len(spikes) > 0:
            top_spike = spikes.nlargest(1, "total_volume").iloc[0]
            insights.append({
                "id": insight_id, "type": "spike",
                "title": "Volume Spike Alert",
                "description": f"Detected {len(spikes)} volume spikes. "
                               f"Highest at strike {int(top_spike['strike'])} with "
                               f"CE vol: {int(top_spike['volume_CE']):,}, PE vol: {int(top_spike['volume_PE']):,}. "
                               f"This suggests significant directional interest at these levels.",
                "timestamp": str(latest_ts),
                "severity": "high" if len(spikes) > 5 else "medium",
            })
            insight_id += 1

    # ── 4. Max Pain Analysis ─────────────────────────
    max_pain = compute_max_pain(df)
    if max_pain:
        mp_strike = max_pain["max_pain_strike"]
        spot = max_pain["spot_price"]
        distance = max_pain["distance_from_spot"]
        insights.append({
            "id": insight_id, "type": "info",
            "title": "Max Pain Analysis",
            "description": f"Max Pain is at {int(mp_strike)} for the current data. "
                           f"Spot ({spot:.1f}) is {abs(distance):.0f} points "
                           f"{'above' if distance < 0 else 'below'} Max Pain. "
                           f"Markets tend to gravitate toward Max Pain near expiry.",
            "timestamp": str(latest_ts),
            "severity": "low",
        })
        insight_id += 1

    # ── 5. OI Build-up / Support-Resistance ──────────
    if len(latest) > 0:
        oi_by_strike = latest.groupby("strike").agg(
            oi_CE=("oi_CE", "sum"), oi_PE=("oi_PE", "sum")
        ).reset_index()

        if len(oi_by_strike) > 0:
            max_ce_oi_strike = oi_by_strike.loc[oi_by_strike["oi_CE"].idxmax()]
            max_pe_oi_strike = oi_by_strike.loc[oi_by_strike["oi_PE"].idxmax()]

            insights.append({
                "id": insight_id, "type": "bearish",
                "title": "Resistance Level (Call OI)",
                "description": f"Highest Call OI build-up at strike {int(max_ce_oi_strike['strike'])} "
                               f"with {int(max_ce_oi_strike['oi_CE']):,} contracts. "
                               f"Heavy Call writing indicates this may act as strong resistance.",
                "timestamp": str(latest_ts),
                "severity": "medium",
            })
            insight_id += 1

            insights.append({
                "id": insight_id, "type": "bullish",
                "title": "Support Level (Put OI)",
                "description": f"Highest Put OI build-up at strike {int(max_pe_oi_strike['strike'])} "
                               f"with {int(max_pe_oi_strike['oi_PE']):,} contracts. "
                               f"Heavy Put writing suggests strong support at this level.",
                "timestamp": str(latest_ts),
                "severity": "medium",
            })
            insight_id += 1

    # ── 6. Volatility Pattern Alerts ─────────────────
    vol_patterns = detect_volatility_patterns(df)
    if vol_patterns.get("skew_detected"):
        direction = vol_patterns["skew_direction"]
        ratio = vol_patterns.get("skew_ratio", 0)
        insights.append({
            "id": insight_id, "type": "volatility",
            "title": "Volatility Skew Detected",
            "description": f"{'Put' if direction == 'put_skew' else 'Call'} skew detected with ratio {ratio:.2f}. "
                           f"OTM Put IV: {vol_patterns.get('otm_put_iv_avg', 0):.1f}%, "
                           f"OTM Call IV: {vol_patterns.get('otm_call_iv_avg', 0):.1f}%. "
                           f"{'Higher put IV suggests crash protection demand.' if direction == 'put_skew' else 'Higher call IV suggests upside demand.'}",
            "timestamp": str(latest_ts),
            "severity": "high",
        })
        insight_id += 1

    if vol_patterns.get("smile_detected"):
        curvature = vol_patterns.get("smile_curvature", 0)
        insights.append({
            "id": insight_id, "type": "volatility",
            "title": "Volatility Smile Pattern",
            "description": f"Volatility smile detected with curvature coefficient {curvature:.4f}. "
                           f"Both OTM puts and OTM calls have elevated IV relative to ATM options. "
                           f"This indicates market uncertainty about direction but expectation of a large move.",
            "timestamp": str(latest_ts),
            "severity": "medium",
        })
        insight_id += 1

    # ── 7. Cluster-based Insights ────────────────────
    if "cluster_label" in df.columns:
        cluster_dist = latest["cluster_label"].value_counts()
        extreme = cluster_dist.get("Extreme Activity", 0)
        if extreme > 0:
            extreme_strikes = latest[latest["cluster_label"] == "Extreme Activity"]["strike"].unique()
            strike_list = ", ".join([str(int(s)) for s in sorted(extreme_strikes)[:5]])
            insights.append({
                "id": insight_id, "type": "spike",
                "title": "Extreme Activity Cluster",
                "description": f"KMeans clustering identified {extreme} data points with extreme activity. "
                               f"Key strikes: {strike_list}. "
                               f"These areas show unusually high combined volume and OI, "
                               f"suggesting concentrated institutional positioning.",
                "timestamp": str(latest_ts),
                "severity": "high" if extreme > 3 else "medium",
            })
            insight_id += 1

    # ── 8. IV Spike Alerts ───────────────────────────
    iv_spikes = detect_iv_spikes(df)
    if iv_spikes:
        top_spike = iv_spikes[0]
        insights.append({
            "id": insight_id, "type": "volatility",
            "title": "IV Spike Detected",
            "description": f"Sudden IV shift at strike {int(top_spike['strike'])} ({top_spike['option_type']}). "
                           f"IV: {top_spike['iv_value']}%, z-score: {top_spike['iv_change_zscore']:.1f}. "
                           f"Rapid IV changes suggest evolving market expectations or event-driven trading.",
            "timestamp": top_spike["datetime"],
            "severity": top_spike["severity"],
        })
        insight_id += 1

    print(f"[Analytics] Generated {len(insights)} AI insights")
    return insights


if __name__ == "__main__":
    from data_loader import load_all_csvs
    from preprocessing import preprocess_pipeline
    from feature_engineering import feature_engineering_pipeline

    raw = load_all_csvs()
    clean = preprocess_pipeline(raw)
    enriched = feature_engineering_pipeline(clean, compute_iv=True, iv_sample_frac=0.05)
    analyzed = analytics_pipeline(enriched)

    print("\n── Top Anomalies ──")
    print(get_top_anomalies(analyzed))

    print("\n── Max Pain ──")
    print(compute_max_pain(analyzed))

    print("\n── Evaluation Metrics ──")
    metrics = compute_evaluation_metrics(analyzed)
    print_evaluation_metrics(metrics)
