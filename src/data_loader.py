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


def get_unique_expiries():
    df = load_all_csvs()
    if df.empty:
        return []
    return sorted(df['expiry'].dropna().unique())


def get_unique_strikes():
    df = load_all_csvs()
    if df.empty:
        return []
    return sorted(df['strike'].dropna().unique())


def filter_df(df, start_date=None, end_date=None, expiries=None, strikes=None):
    if df.empty:
        return df
    out = df
    if start_date is not None:
        out = out[out['datetime'] >= pd.to_datetime(start_date)]
    if end_date is not None:
        out = out[out['datetime'] <= pd.to_datetime(end_date)]
    if expiries:
        out = out[out['expiry'].isin(expiries)]
    if strikes:
        out = out[out['strike'].isin(strikes)]
    return out
