-- Quarterly bank counts
SELECT repdte, COUNT(*) AS banks
FROM staging_fdic_bank
GROUP BY repdte
ORDER BY repdte;

-- Check row counts
SELECT COUNT(*) FROM bank_kpi_fact;

-- Check for missing KPI values
SELECT 
    SUM(CASE WHEN roa IS NULL THEN 1 ELSE 0 END) AS missing_roa,
    SUM(CASE WHEN roe IS NULL THEN 1 ELSE 0 END) AS missing_roe,
    SUM(CASE WHEN capital_ratio IS NULL THEN 1 ELSE 0 END) AS missing_capital
FROM bank_kpi_fact;

-- KPI sanity ranges
SELECT 
    MIN(roa) AS min_roa, MAX(roa) AS max_roa,
    MIN(roe) AS min_roe, MAX(roe) AS max_roe,
    MIN(capital_ratio) AS min_cap, MAX(capital_ratio) AS max_cap
FROM bank_kpi_fact;

-- Count banks by state
SELECT state, COUNT(*) 
FROM bank_dim 
GROUP BY state 
ORDER BY COUNT(*) DESC;
