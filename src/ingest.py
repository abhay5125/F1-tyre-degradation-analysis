import argparse
import logging
import pandas as pd
from typing import List, Optional
from src.config import load_config
from src.utils import setup_logging, sqlite_conn

def load_csv_to_db(path: str, table: str, db_path: str, datetime_cols: Optional[List[str]] = None,
                   categorical_cols: Optional[List[str]] = None, keep_cols: Optional[List[str]] = None) -> int:
    df = pd.read_csv(path)
    if keep_cols:
        missing = set(keep_cols) - set(df.columns)
        if missing:
            raise ValueError(f"Missing columns in {path}: {missing}")
        df = df[keep_cols]
    # types
    for col in datetime_cols or []:
        df[col] = pd.to_datetime(df[col], errors="coerce", utc=False)
    for col in categorical_cols or []:
        df[col] = df[col].astype("category")
    # write
    with sqlite_conn(db_path) as conn:
        df.to_sql(table, conn, if_exists="replace", index=False)
        n = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    return n

def main(cfg_path: str = "config.yml"):
    setup_logging()
    cfg = load_config(cfg_path)
    db_path = cfg.get("database_path", "db/data.db")
    total = 0
    for src in cfg.get("data_sources", []):
        logging.info("Loading %s → table=%s", src["path"], src["table"])
        n = load_csv_to_db(
            src["path"], src["table"], db_path,
            datetime_cols=src.get("datetime_cols"),
            categorical_cols=src.get("categorical_cols"),
            keep_cols=src.get("keep_cols"),
        )
        logging.info("Loaded %s rows into %s", n, src["table"])
        total += n
    logging.info("Done. Total rows loaded: %s", total)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config.yml")
    args = parser.parse_args()
    main(args.config)
