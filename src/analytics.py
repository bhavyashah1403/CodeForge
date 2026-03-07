"""
Analytics Module
────────────────
AI-powered anomaly detection, pattern analysis, and market insights.
Uses Scikit-learn Isolation Forest for unsupervised anomaly detection.
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
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

    print("=" * 60 + "\n")
    return df


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
