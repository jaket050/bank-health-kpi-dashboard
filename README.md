# Bank Health KPI Dashboard

A portfolio-ready data project that ingests FDIC bank-level financials, builds a dimensional model in PostgreSQL, computes KPIs (ROA, ROE, Capital Ratio, NIM, NPL Ratio), and publishes dashboards for peer benchmarking and risk monitoring.

## Business Question
**How has the financial health of U.S. banks changed over time, and which institutions or regions appear more at risk based on ROA, ROE, capital adequacy, and credit quality?**

## Data Sources
- FDIC BankFind Financials API (bank-level, quarterly)
- Institutions metadata (from FDIC CSV/API)

## Tech Stack
- Python (Pandas, NumPy, SQLAlchemy, psycopg2, Requests)
- PostgreSQL
- Tableau (dashboards)
- Jupyter (EDA)
- GitHub (repo & docs)

## Process
The ETL pipeline is designed to be **idempotent and repeatable**, ensuring consistency across refreshes.  
Instead of one-off manual cleaning, I implemented automated steps that:  
- Enforce data types and constraints (numeric casting, date parsing, boolean mapping)  
- Standardize fields like bank IDs, names, and reporting dates  
- Validate KPIs to surface missing values, outliers, and mismatches between institutions and reported financials  

This approach makes the workflow closer to production standards. Each run produces the same reliable KPIs, which is essential in financial analysis where consistency and auditability are critical.  


## Repo Structure

bank-health-kpi-dashboard/
├─ data/
│  ├─ raw/                # API extracts, scratch data
│  └─ archive/            # archived CSVs from earlier iteration
├─ docs/                  # documentation (KPI dictionary, pipeline notes, issue log, EDA plan)
├─ notebooks/             # exploratory analysis and validation
├─ sql/                   # schema, validation, indexing
├─ src/
│  ├─ etl/                # ETL scripts (load_fdic_api, transform_fdic_to_kpi, etc.)
│  └─ utils/              # helper functions
├─ config.ini             # DB + API config (ignored in GitHub)
├─ requirements.txt       # Python dependencies
└─ README.md
