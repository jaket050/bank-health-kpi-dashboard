CREATE INDEX IF NOT EXISTS idx_bank_kpi_fact_bank_id ON bank_kpi_fact(bank_id);
CREATE INDEX IF NOT EXISTS idx_bank_kpi_fact_date_id ON bank_kpi_fact(date_id);
