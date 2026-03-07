"""
Data Preprocessing Module
─────────────────────────
Cleans, validates, and enriches the raw options data.
Handles missing values, duplicates, outliers, and derives basic columns.
"""

import pandas as pd
import numpy as np
from config import NIFTY_LOT_SIZE


def validate_schema(df: pd.DataFrame) -> pd.DataFrame:
    """Validate that required columns exist and have correct types."""
    required = ["symbol", "datetime", "expiry", "CE", "PE", "spot_close",
                "ATM", "strike", "oi_CE", "oi_PE", "volume_CE", "volume_PE"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")
    print(f"[Preprocessing] Schema validated ✓ ({len(df.columns)} columns)")
    return df


def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """Handle missing/null values in the dataset."""
    before = len(df)
    null_counts = df.isnull().sum()
    total_nulls = null_counts.sum()

    if total_nulls > 0:
        print(f"[Preprocessing] Found {total_nulls} null values:")
        for col, cnt in null_counts[null_counts > 0].items():
            print(f"  - {col}: {cnt} nulls")

    # Drop rows where critical price columns are null
    critical_cols = ["CE", "PE", "spot_close", "strike"]
    df = df.dropna(subset=critical_cols)

    # Fill remaining OI/Volume nulls with 0 (no activity = 0)
    fill_cols = ["oi_CE", "oi_PE", "volume_CE", "volume_PE"]
    for col in fill_cols:
        if col in df.columns:
            df[col] = df[col].fillna(0).astype("int64")

    after = len(df)
    print(f"[Preprocessing] Missing values handled: {before - after} rows dropped, {after:,} remaining")
    return df


def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """Remove exact duplicate rows."""
    before = len(df)
    df = df.drop_duplicates(subset=["datetime", "expiry", "strike"], keep="last")
    after = len(df)
    removed = before - after
    if removed > 0:
        print(f"[Preprocessing] Removed {removed:,} duplicate rows")
    else:
        print(f"[Preprocessing] No duplicates found ✓")
    return df


def filter_invalid_data(df: pd.DataFrame) -> pd.DataFrame:
    """Remove rows with clearly invalid/impossible values."""
    before = len(df)

    # Option prices must be non-negative
    df = df[(df["CE"] >= 0) & (df["PE"] >= 0)].copy()

    # Spot price must be positive
    df = df[df["spot_close"] > 0]

    # Strike must be positive
    df = df[df["strike"] > 0]

    # OI and volume must be non-negative
    df = df[(df["oi_CE"] >= 0) & (df["oi_PE"] >= 0)]
    df = df[(df["volume_CE"] >= 0) & (df["volume_PE"] >= 0)]

    after = len(df)
    removed = before - after
    if removed > 0:
        print(f"[Preprocessing] Filtered {removed:,} invalid rows")
    else:
        print(f"[Preprocessing] No invalid data found ✓")
    return df


def add_derived_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Add basic derived columns useful for downstream analysis."""

    # ── Moneyness ────────────────────────────────────────
    df["moneyness"] = df["spot_close"] / df["strike"]

    # Categorize: ITM / ATM / OTM for calls
    df["moneyness_label"] = pd.cut(
        df["moneyness"],
        bins=[0, 0.97, 1.03, np.inf],
        labels=["OTM", "ATM", "ITM"],
    )

    # ── Time to Expiry (in years) ────────────────────────
    df["time_to_expiry_days"] = (df["expiry"] - df["datetime"]).dt.total_seconds() / 86400
    df["time_to_expiry_years"] = df["time_to_expiry_days"] / 365.0

    # Remove expired or negative TTE rows
    df = df[df["time_to_expiry_days"] > 0].copy()

    # ── Intrinsic Value ──────────────────────────────────
    df["intrinsic_CE"] = np.maximum(df["spot_close"] - df["strike"], 0)
    df["intrinsic_PE"] = np.maximum(df["strike"] - df["spot_close"], 0)

    # ── Extrinsic (Time) Value ───────────────────────────
    df["extrinsic_CE"] = df["CE"] - df["intrinsic_CE"]
    df["extrinsic_PE"] = df["PE"] - df["intrinsic_PE"]

    # ── Put-Call Ratio (PCR) by OI ───────────────────────
    df["pcr_oi"] = np.where(
        df["oi_CE"] > 0,
        df["oi_PE"] / df["oi_CE"],
        np.nan,
    )

    # ── PCR by Volume ────────────────────────────────────
    df["pcr_volume"] = np.where(
        df["volume_CE"] > 0,
        df["volume_PE"] / df["volume_CE"],
        np.nan,
    )

    # ── Total OI and Volume ──────────────────────────────
    df["total_oi"] = df["oi_CE"] + df["oi_PE"]
    df["total_volume"] = df["volume_CE"] + df["volume_PE"]

    # ── Distance from ATM (in strike points) ─────────────
    df["distance_from_atm"] = df["strike"] - df["ATM"]

    # ── Date / Time components for grouping ──────────────
    df["date"] = df["datetime"].dt.date
    df["time"] = df["datetime"].dt.time
    df["hour"] = df["datetime"].dt.hour

    print(f"[Preprocessing] Added {13} derived columns")
    return df


def sort_data(df: pd.DataFrame) -> pd.DataFrame:
    """Sort by datetime and strike for clean ordering."""
    df = df.sort_values(["datetime", "strike"]).reset_index(drop=True)
    print(f"[Preprocessing] Data sorted by datetime + strike")
    return df


def get_data_summary(df: pd.DataFrame) -> dict:
    """Generate a summary report of the preprocessed data."""
    summary = {
        "total_rows": len(df),
        "date_range": f"{df['datetime'].min()} → {df['datetime'].max()}",
        "expiry_dates": sorted(df["expiry"].dt.date.unique().tolist()),
        "strike_range": f"{df['strike'].min():.0f} - {df['strike'].max():.0f}",
        "spot_range": f"{df['spot_close'].min():.2f} - {df['spot_close'].max():.2f}",
        "unique_strikes": df["strike"].nunique(),
        "unique_timestamps": df["datetime"].nunique(),
        "source_files": df["source_file"].unique().tolist(),
        "null_percentage": (df.isnull().sum().sum() / (len(df) * len(df.columns)) * 100),
    }
    return summary


# ─── Full Preprocessing Pipeline ─────────────────────────
def preprocess_pipeline(df: pd.DataFrame) -> pd.DataFrame:
    """Run the full preprocessing pipeline."""
    print("\n" + "=" * 60)
    print("   DATA PREPROCESSING PIPELINE")
    print("=" * 60)

    df = validate_schema(df)
    df = handle_missing_values(df)
    df = remove_duplicates(df)
    df = filter_invalid_data(df)
    df = add_derived_columns(df)
    df = sort_data(df)

    summary = get_data_summary(df)
    print(f"\n── Preprocessing Summary ──")
    for k, v in summary.items():
        print(f"  {k}: {v}")
    print("=" * 60 + "\n")

    return df


if __name__ == "__main__":
    from data_loader import load_all_csvs
    raw_df = load_all_csvs()
    clean_df = preprocess_pipeline(raw_df)
    print(clean_df.head(10))
    print(f"\nColumns: {list(clean_df.columns)}")
    print(f"\nDtypes:\n{clean_df.dtypes}")
