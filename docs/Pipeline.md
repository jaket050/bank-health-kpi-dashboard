# Pipeline

1. Extract: FDIC API → staging_fdic_bank
2. Load: staging → Postgres
3. Transform: compute KPIs, join dims
4. Load: bank_kpi_fact
5. Consume: Tableau + Jupyter
