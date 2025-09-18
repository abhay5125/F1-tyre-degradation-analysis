#Dashboard Baseline

A reusable baseline for data ingestion → transformation → dashboarding. Drop in any dataset, edit `config.yml`, run the ingest step, and launch the Streamlit app.

## Quickstart

```bash
# 1) Create & activate venv (optional but recommended)
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 2) Install deps
pip install -r requirements.txt

# 3) Configure
# Edit config.yml to point to your data file(s) and column mappings

# 4) Ingest data into SQLite
python src/ingest.py

# 5) (Optional) Build analytical tables
python src/transform.py

# 6) Run the app
streamlit run app/streamlit_app.py
```

## Project Layout

```
project/
├── data_raw/           # your raw CSV/JSON files
├── db/                 # SQLite database lives here
├── notebooks/          # scratchpads
├── src/                # pipeline code
│   ├── ingest.py
│   ├── transform.py
│   ├── viz_utils.py
│   ├── config.py
│   └── utils.py
├── app/
│   └── streamlit_app.py
├── config.yml
├── requirements.txt
└── README.md
```

## Philosophy
- 90% reusable (ingest/transform/viz scaffolding)
- 10% dataset-specific via `config.yml` and small custom transforms
- SQL-backed for reproducibility and performance
