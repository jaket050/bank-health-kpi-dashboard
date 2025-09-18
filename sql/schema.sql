
-- Staging Tables
CREATE TABLE staging_fdic (
    reporting_period DATE,
    bank_id VARCHAR(20),
    bank_name TEXT,
    total_assets NUMERIC,
    total_loans NUMERIC,
    total_deposits NUMERIC,
    net_income NUMERIC,
    interest_income NUMERIC,
    interest_expense NUMERIC,
    nonperforming_loans NUMERIC
);

CREATE TABLE staging_fred (
    series_id VARCHAR(50),
    observation_date DATE,
    value NUMERIC
);

-- Dimension Tables

CREATE TABLE bank_dim (
    bank_id SERIAL PRIMARY KEY,
    fdic_cert VARCHAR(20) UNIQUE,
    bank_name TEXT,
    city TEXT,
    state TEXT,
    charter_type TEXT
);

CREATE TABLE date_dim (
    date_id SERIAL PRIMARY KEY,
    date_actual DATE UNIQUE,
    year INT,
    quarter INT,
    month INT
);

-- Fact Table

CREATE TABLE bank_kpi_fact (
    kpi_id SERIAL PRIMARY KEY,
    bank_id INT REFERENCES bank_dim(bank_id),
    date_id INT REFERENCES date_dim(date_id),
    nim NUMERIC,   -- Net Interest Margin
    roa NUMERIC,   -- Return on Assets
    roe NUMERIC,   -- Return on Equity
    npl_ratio NUMERIC, -- Non-performing loan ratio
    capital_ratio NUMERIC,
    created_at TIMESTAMP DEFAULT NOW()
);
