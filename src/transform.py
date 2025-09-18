#Optional precomputations for example 'daily_summary'
#why: heavy computations once, fast charts many times

import logging
import pandas as pd
from src.config import load_config
from src.utils import setup_logging, sqlite_conn

def create_daily_summary(db_path: str, source_table: str, datetime_col: str = "timestamp", out_table: str = "daily_summary"):
    with sqlite_conn(db_path) as conn:
        q = f'''
        SELECT DATE({datetime_col}) AS date, COUNT(*) AS rows, AVG(value) AS avg_value
        FROM {source_table}
        GROUP BY DATE({datetime_col})
        ORDER BY DATE({datetime_col})
        '''
        df = pd.read_sql(q, conn, parse_dates=["date"])
        df.to_sql(out_table, conn, if_exists="replace", index=False)
        return len(df)

def main(cfg_path: str = "config.yml"):
    setup_logging()
    cfg = load_config(cfg_path)
    db_path = cfg.get("database_path", "db/data.db")
    date_col = cfg.get("default_filters", {}).get("date_col", "timestamp")
    # Assume first source table is the base
    base_table = cfg["data_sources"][0]["table"]
    logging.info("Building daily summary from %s", base_table)
    n = create_daily_summary(db_path, base_table, datetime_col=date_col, out_table="daily_summary")
    logging.info("Materialized daily_summary with %s rows", n)

with sqlite_conn("db/data.db") as conn:
    conn.execute("""
    CREATE TABLE IF NOT EXISTS daily_avg AS
    SELECT DATe(timestamp) AS day,
                 AVG(value) as avg_val
    From events_raw
    GROUP BY DATE(timestamp)
    """)

if __name__ == "__main__":
    main()
