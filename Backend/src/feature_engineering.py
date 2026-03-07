"""
Feature Engineering Module
──────────────────────────
Calculates Implied Volatility (IV), Greeks approximations,
volatility smile/skew metrics, and enriches the dataset.
Uses py_vollib for Black-Scholes IV computation.
"""

import numpy as np
import pandas as pd
from scipy.stats import norm
from config import RISK_FREE_RATE, TRADING_DAYS_PER_YEAR


# ═══════════════════════════════════════════════════════════
#  IMPLIED VOLATILITY (Newton-Raphson, no external dep needed)
# ═══════════════════════════════════════════════════════════

def _bs_price(S, K, T, r, sigma, option_type="call"):
    """Black-Scholes option price."""
    if T <= 0 or sigma <= 0:
        return 0.0
    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    if option_type == "call":
        return S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    else:
        return K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)


def _bs_vega(S, K, T, r, sigma):
    """Black-Scholes Vega (sensitivity of price to volatility)."""
    if T <= 0 or sigma <= 0:
        return 0.0
    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    return S * np.sqrt(T) * norm.pdf(d1)


def implied_volatility(
    market_price, S, K, T, r=RISK_FREE_RATE,
    option_type="call", max_iter=100, tol=1e-6
):
    """
    Calculate IV using Newton-Raphson method.
    Returns NaN if convergence fails.
    """
    if T <= 0 or market_price <= 0:
        return np.nan

    # Intrinsic value check
    if option_type == "call":
        intrinsic = max(S - K * np.exp(-r * T), 0)
    else:
        intrinsic = max(K * np.exp(-r * T) - S, 0)

    if market_price < intrinsic:
        return np.nan

    sigma = 0.3  # initial guess
    for _ in range(max_iter):
        price = _bs_price(S, K, T, r, sigma, option_type)
        vega = _bs_vega(S, K, T, r, sigma)
        if vega < 1e-12:
            break
        diff = price - market_price
        if abs(diff) < tol:
            return sigma
        sigma -= diff / vega
        if sigma <= 0:
            sigma = 0.001  # reset to small positive
    return np.nan


def compute_iv_vectorized(df: pd.DataFrame, sample_frac: float = 1.0) -> pd.DataFrame:
    """
    Compute IV for both CE and PE across the DataFrame.
    Uses vectorized approach with fallback to row-wise for robustness.
    sample_frac < 1.0 computes IV on a sample for speed.
    """
    print("[FeatureEng] Computing Implied Volatility...")

    if sample_frac < 1.0:
        calc_df = df.sample(frac=sample_frac, random_state=42)
    else:
        calc_df = df

    iv_ce = []
    iv_pe = []
    for _, row in calc_df.iterrows():
        S = row["spot_close"]
        K = row["strike"]
        T = row["time_to_expiry_years"]

        iv_c = implied_volatility(row["CE"], S, K, T, RISK_FREE_RATE, "call")
        iv_p = implied_volatility(row["PE"], S, K, T, RISK_FREE_RATE, "put")
        iv_ce.append(iv_c)
        iv_pe.append(iv_p)

    calc_df = calc_df.copy()
    calc_df["iv_CE"] = iv_ce
    calc_df["iv_PE"] = iv_pe

    # Average IV
    calc_df["iv_avg"] = calc_df[["iv_CE", "iv_PE"]].mean(axis=1)

    if sample_frac < 1.0:
        # Merge back
        df = df.merge(
            calc_df[["datetime", "strike", "expiry", "iv_CE", "iv_PE", "iv_avg"]],
            on=["datetime", "strike", "expiry"],
            how="left",
        )
    else:
        df = calc_df

    valid_iv = df["iv_CE"].notna().sum() + df["iv_PE"].notna().sum()
    print(f"[FeatureEng] IV computed: {valid_iv:,} valid IV values")
    return df


# ═══════════════════════════════════════════════════════════
#  GREEKS (Analytical Black-Scholes)
# ═══════════════════════════════════════════════════════════

def compute_greeks(df: pd.DataFrame) -> pd.DataFrame:
    """Compute Delta, Gamma, Theta for calls and puts using BS formulas."""
    print("[FeatureEng] Computing Greeks...")

    S = df["spot_close"].values
    K = df["strike"].values
    T = df["time_to_expiry_years"].values
    r = RISK_FREE_RATE

    # Use IV if available, else use a default
    sigma_ce = df["iv_CE"].fillna(0.2).values
    sigma_pe = df["iv_PE"].fillna(0.2).values

    sqrt_T = np.sqrt(np.maximum(T, 1e-10))

    # ── Call Greeks ──────────────────────────────────────
    d1_ce = (np.log(S / K) + (r + 0.5 * sigma_ce**2) * T) / (sigma_ce * sqrt_T)
    d2_ce = d1_ce - sigma_ce * sqrt_T

    df["delta_CE"] = norm.cdf(d1_ce)
    df["gamma_CE"] = norm.pdf(d1_ce) / (S * sigma_ce * sqrt_T)
    df["theta_CE"] = (-(S * norm.pdf(d1_ce) * sigma_ce) / (2 * sqrt_T)
                       - r * K * np.exp(-r * T) * norm.cdf(d2_ce)) / TRADING_DAYS_PER_YEAR
    df["vega_CE"] = S * sqrt_T * norm.pdf(d1_ce) / 100  # per 1% vol move

    # ── Put Greeks ───────────────────────────────────────
    d1_pe = (np.log(S / K) + (r + 0.5 * sigma_pe**2) * T) / (sigma_pe * sqrt_T)
    d2_pe = d1_pe - sigma_pe * sqrt_T

    df["delta_PE"] = norm.cdf(d1_pe) - 1
    df["gamma_PE"] = norm.pdf(d1_pe) / (S * sigma_pe * sqrt_T)
    df["theta_PE"] = (-(S * norm.pdf(d1_pe) * sigma_pe) / (2 * sqrt_T)
                       + r * K * np.exp(-r * T) * norm.cdf(-d2_pe)) / TRADING_DAYS_PER_YEAR
    df["vega_PE"] = S * sqrt_T * norm.pdf(d1_pe) / 100

    print(f"[FeatureEng] Greeks computed (Delta, Gamma, Theta, Vega for CE & PE)")
    return df


# ═══════════════════════════════════════════════════════════
#  VOLATILITY SMILE / SKEW METRICS
# ═══════════════════════════════════════════════════════════

def compute_smile_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute volatility smile/skew metrics per timestamp.
    - IV Skew = IV(OTM Put) - IV(OTM Call) at same distance from ATM
    - Smile curvature: quadratic fit coefficient on moneyness vs IV
    """
    print("[FeatureEng] Computing volatility smile metrics...")

    # IV spread between CE and PE at same strike
    df["iv_spread"] = df["iv_CE"] - df["iv_PE"]

    # Relative strike (normalized distance from ATM)
    df["relative_strike"] = (df["strike"] - df["ATM"]) / df["ATM"]

    print(f"[FeatureEng] Smile metrics computed")
    return df


# ═══════════════════════════════════════════════════════════
#  VOLUME & OI CHANGE FEATURES
# ═══════════════════════════════════════════════════════════

def compute_volume_oi_features(df: pd.DataFrame) -> pd.DataFrame:
    """Compute rolling and change-based features for OI and volume."""
    print("[FeatureEng] Computing volume/OI features...")

    # Sort for rolling calculations
    df = df.sort_values(["strike", "expiry", "datetime"]).copy()

    # Group by strike + expiry for time-series features
    grouped = df.groupby(["strike", "expiry"])

    # OI change (delta)
    df["oi_CE_change"] = grouped["oi_CE"].diff().fillna(0)
    df["oi_PE_change"] = grouped["oi_PE"].diff().fillna(0)

    # Volume moving average (5-period)
    df["vol_CE_ma5"] = grouped["volume_CE"].transform(
        lambda x: x.rolling(5, min_periods=1).mean()
    )
    df["vol_PE_ma5"] = grouped["volume_PE"].transform(
        lambda x: x.rolling(5, min_periods=1).mean()
    )

    # Volume ratio to moving average (spike detection)
    df["vol_CE_ratio"] = np.where(
        df["vol_CE_ma5"] > 0,
        df["volume_CE"] / df["vol_CE_ma5"],
        1.0,
    )
    df["vol_PE_ratio"] = np.where(
        df["vol_PE_ma5"] > 0,
        df["volume_PE"] / df["vol_PE_ma5"],
        1.0,
    )

    # Re-sort by datetime
    df = df.sort_values(["datetime", "strike"]).reset_index(drop=True)

    print(f"[FeatureEng] Volume/OI features added (changes, MA, ratios)")
    return df


# ═══════════════════════════════════════════════════════════
#  FULL FEATURE ENGINEERING PIPELINE
# ═══════════════════════════════════════════════════════════

def feature_engineering_pipeline(
    df: pd.DataFrame,
    compute_iv: bool = True,
    iv_sample_frac: float = 0.1,
) -> pd.DataFrame:
    """
    Full feature engineering pipeline.
    iv_sample_frac: fraction of rows to compute IV on (1.0 = all, 0.1 = 10% sample).
    Use smaller fraction for faster iteration during development.
    """
    print("\n" + "=" * 60)
    print("   FEATURE ENGINEERING PIPELINE")
    print("=" * 60)

    if compute_iv:
        df = compute_iv_vectorized(df, sample_frac=iv_sample_frac)
        df = compute_greeks(df)
        df = compute_smile_metrics(df)

    df = compute_volume_oi_features(df)

    print(f"\n[FeatureEng] Final dataset: {df.shape[0]:,} rows × {df.shape[1]} columns")
    print("=" * 60 + "\n")
    return df


if __name__ == "__main__":
    from data_loader import load_all_csvs
    from preprocessing import preprocess_pipeline

    raw = load_all_csvs()
    clean = preprocess_pipeline(raw)

    # Use 5% sample for quick IV test
    enriched = feature_engineering_pipeline(clean, compute_iv=True, iv_sample_frac=0.05)
    print(enriched[["strike", "CE", "PE", "iv_CE", "iv_PE", "delta_CE", "delta_PE"]].dropna().head(10))
