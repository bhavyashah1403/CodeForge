from pathlib import Path
import pandas as pd

DATA_DIR = Path(__file__).resolve().parents[1] / "data"


def list_csv_files():
    return sorted([p for p in DATA_DIR.glob("*.csv")])


def load_all_csvs():
    files = list_csv_files()
    if not files:
        return pd.DataFrame()
    dfs = [pd.read_csv(f, parse_dates=["datetime"]) for f in files]
    return pd.concat(dfs, ignore_index=True)


def preview(n=5):
    df = load_all_csvs()
    return df.head(n)
