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

### Quality Assurance
All data and pipeline issues are documented in the [Issues Log](docs/issues_log.md),  
with root causes, resolutions, and status tracking.

### EDA Highlights

As part of exploratory analysis, I validated KPIs and summarized key trends:

- **Exploratory Insights (During EDA):**
  - Profitability (ROA/ROE) is cyclical — median ROA dipped to ~0.27% in early 2024, rebounded to ~1.1% by year-end; ROE ended near 9.4%.  
  - NIM compressed in early 2024, then rebounded by Q4.  
  - NPL ratios trended upward, signaling growing loan book stress.  
  - Capital adequacy remained stable (~11%), providing a regulatory buffer.  

- **Executive Summary (2024Q4):**
  - ROA = **0.92%** (↓2.0% YoY)  
  - ROE = **9.4%** (↓6.5% YoY)  
  - NIM = **3.13%** (↓0.4% YoY)  
  - NPL = **26.1%** (↑35.4% YoY)  
  - Capital Ratio = **9.7%** (↑2.2% YoY)  

- **Data Quality:** <0.2% nulls, 0 duplicates, winsorized ratios at 1–99% to reduce outlier distortion.  

- **Key Visuals:**  
  ![ROA Trend](docs/eda_outputs/roa_trend_all.png)  
  ![NIM Trend](docs/eda_outputs/nim_trend.png)  
  ![NPL Trend](docs/eda_outputs/npl_trend.png)


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
