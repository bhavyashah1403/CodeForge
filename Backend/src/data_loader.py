"""
Data Loader Module
─────────────────
Loads CSV data into DuckDB (serverless analytical database) and provides
Pandas DataFrames for downstream analytics. Uses DuckDB for fast OLAP queries.
"""

import os
import glob
import duckdb
import pandas as pd
from config import DATA_DIR, DB_PATH, CSV_COLUMNS, DTYPES, DATE_COLUMNS


def get_csv_files(data_dir: str = DATA_DIR) -> list[str]:
    """Discover all CSV files in the data directory."""
    pattern = os.path.join(data_dir, "*.csv")
    files = sorted(glob.glob(pattern))
    if not files:
        raise FileNotFoundError(f"No CSV files found in {data_dir}")
    print(f"[DataLoader] Found {len(files)} CSV file(s): {[os.path.basename(f) for f in files]}")
    return files


def load_csv_to_dataframe(filepath: str) -> pd.DataFrame:
    """Load a single CSV into a Pandas DataFrame with proper dtypes."""
    df = pd.read_csv(filepath, dtype=DTYPES, parse_dates=DATE_COLUMNS)
    df.columns = [c.strip() for c in df.columns]
    # Tag with source file for traceability
    df["source_file"] = os.path.basename(filepath)
    return df


def load_all_csvs(data_dir: str = DATA_DIR) -> pd.DataFrame:
    """Load and concatenate all CSV files into a single DataFrame."""
    files = get_csv_files(data_dir)
    dfs = [load_csv_to_dataframe(f) for f in files]
    combined = pd.concat(dfs, ignore_index=True)
    print(f"[DataLoader] Combined DataFrame: {combined.shape[0]:,} rows × {combined.shape[1]} columns")
    return combined


def init_duckdb(db_path: str = DB_PATH) -> duckdb.DuckDBPyConnection:
    """Initialize a DuckDB connection (file-backed for persistence)."""
    con = duckdb.connect(db_path)
    print(f"[DataLoader] DuckDB connected: {db_path}")
    return con


def load_into_duckdb(
    con: duckdb.DuckDBPyConnection,
    df: pd.DataFrame,
    table_name: str = "options_raw",
) -> None:
    """Load a Pandas DataFrame into a DuckDB table."""
    con.execute(f"DROP TABLE IF EXISTS {table_name}")
    con.execute(f"CREATE TABLE {table_name} AS SELECT * FROM df")
    row_count = con.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
    print(f"[DataLoader] Loaded {row_count:,} rows into DuckDB table '{table_name}'")


def query_duckdb(con: duckdb.DuckDBPyConnection, sql: str) -> pd.DataFrame:
    """Execute SQL on DuckDB and return a Pandas DataFrame."""
    return con.execute(sql).fetchdf()


# ─── Convenience: One-call pipeline ─────────────────────
def ingest_pipeline(data_dir: str = DATA_DIR, db_path: str = DB_PATH):
    """Full ingestion: CSV → Pandas → DuckDB. Returns (connection, dataframe)."""
    df = load_all_csvs(data_dir)
    con = init_duckdb(db_path)
    load_into_duckdb(con, df)
    return con, df


if __name__ == "__main__":
    # Quick test
    con, df = ingest_pipeline()
    print("\n── Sample Data ──")
    print(df.head())
    print(f"\n── DuckDB Query Test ──")
    result = query_duckdb(con, "SELECT COUNT(*) as total, MIN(datetime) as start, MAX(datetime) as end FROM options_raw")
    print(result)
    con.close()
