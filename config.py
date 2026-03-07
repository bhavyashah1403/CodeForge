"""
Configuration constants for the Options Analytics Platform.
"""
import os

# ─── Paths ───────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(BASE_DIR, "options.duckdb")

# ─── Data Schema ─────────────────────────────────────────
CSV_COLUMNS = [
    "symbol", "datetime", "expiry", "CE", "PE",
    "spot_close", "ATM", "strike",
    "oi_CE", "oi_PE", "volume_CE", "volume_PE",
]

DTYPES = {
    "symbol": "str",
    "CE": "float64",
    "PE": "float64",
    "spot_close": "float64",
    "ATM": "float64",
    "strike": "float64",
    "oi_CE": "int64",
    "oi_PE": "int64",
    "volume_CE": "int64",
    "volume_PE": "int64",
}

DATE_COLUMNS = ["datetime", "expiry"]

# ─── Options Constants ───────────────────────────────────
RISK_FREE_RATE = 0.07          # ~7% (India RBI rate)
TRADING_DAYS_PER_YEAR = 252
NIFTY_LOT_SIZE = 25            # NIFTY option lot size

# ─── Anomaly Detection ───────────────────────────────────
ISOLATION_FOREST_CONTAMINATION = 0.05   # 5% anomaly fraction
VOLUME_SPIKE_THRESHOLD = 3.0           # 3x std dev above mean
OI_CHANGE_THRESHOLD = 2.0             # 2x std dev for OI changes

# ─── Dashboard ───────────────────────────────────────────
PAGE_TITLE = "AI-Powered Options Analytics Platform"
PAGE_ICON = "📊"
LAYOUT = "wide"
