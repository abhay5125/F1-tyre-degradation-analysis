import streamlit as st
import pandas as pd
from src.config import load_config
from src.utils import sqlite_conn
from src.viz_utils import line_chart, bar_chart

# -------- Helper: inject WHERE before GROUP BY / ORDER BY / LIMIT --------
def apply_date_filter(q: str, date_col: str, start_iso: str, end_iso: str) -> str:
    """
    Insert a WHERE (or AND) date filter before GROUP BY / ORDER BY / LIMIT.
    Works with the simple SELECT queries defined in config.yml.
    """
    clause = f"DATE({date_col}) BETWEEN DATE('{start_iso}') AND DATE('{end_iso}')"
    q_flat = " ".join(q.split())           # normalize whitespace
    low = q_flat.lower()

    # Find earliest clause among GROUP BY / ORDER BY / LIMIT
    cut = len(q_flat)
    for kw in (" group by ", " order by ", " limit "):
        idx = low.find(kw)
        if idx != -1:
            cut = min(cut, idx)

    head, tail = q_flat[:cut], q_flat[cut:]
    if " where " in head.lower():
        head = f"{head} AND {clause}"
    else:
        head = f"{head} WHERE {clause}"
    return head + tail

#-------------------------Page Setup-----------------------------------
st.set_page_config(page_title="Baseline Dashboard", layout="wide")

cfg = load_config("config.yml")
db_path = cfg.get("database_path", "db/data.db")

st.title(cfg.get("project_name", "Dashboard"))

#----------------------------KPIs---------------------------------------
st.subheader("KPIs")
cols = st.columns(max(1, len(cfg.get("kpis", []))))
with sqlite_conn(db_path) as conn:
    for i, kpi in enumerate(cfg.get("kpis", [])):
        val = conn.execute(kpi["sql"]).fetchone()[0]
        cols[i].metric(label=kpi["label"], value=round(val, 2) if isinstance(val, (int, float)) else val)

#-------------------Date Filter UI--------------------------------------
date_col = cfg.get("default_filters", {}).get("date_col")
if date_col:
    st.subheader("Filters")
    r = cfg.get("default_filters", {}).get("range", [])
    default_start = pd.to_datetime(r[0]).date() if len(r) > 0 and r[0] else None
    default_end   = pd.to_datetime(r[1]).date() if len(r) > 1 and r[1] else None

    picked = st.date_input("Date range", value=(default_start, default_end))
    if isinstance(picked, tuple):
        start_d, end_d = picked
    else:
        start_d = end_d = picked

    start_iso = pd.to_datetime(start_d).date().isoformat() if start_d else None
    end_iso   = pd.to_datetime(end_d).date().isoformat() if end_d else None
else:
    start_iso = end_iso = None

st.divider()

#-------------------Charts (from config)--------------------------------
with sqlite_conn(db_path) as conn:
    for chart in cfg.get("charts", []):
        st.markdown(f"### {chart['name']}")
        q = chart["query"]

        # Apply dynamic date filter safely
        if date_col and start_iso and end_iso:
            q = apply_date_filter(q, date_col, start_iso, end_iso)

        df = pd.read_sql(q, conn)

        x = chart["x"]
        y = chart["y"]
        ctype = chart.get("type", "line").lower()

        if ctype == "line":
            st.plotly_chart(line_chart(df, x, y, title=chart["name"]), use_container_width=True)
        elif ctype == "bar":
            st.plotly_chart(bar_chart(df, x, y, title=chart["name"]), use_container_width=True)
        else:
            # Fallback: show the data if type is unknown
            st.dataframe(df)