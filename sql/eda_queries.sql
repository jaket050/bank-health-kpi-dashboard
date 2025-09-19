-- Quarterly KPI Averages
SELECT date_id, 
       ROUND(AVG(roa),4) AS avg_roa, 
       ROUND(AVG(roe),4) AS avg_roe,
       ROUND(AVG(capital_ratio),4) AS avg_capital,
       ROUND(AVG(nim),4) AS avg_nim,
       ROUND(AVG(npl_ratio),4) AS avg_npl
FROM bank_kpi_fact
GROUP BY date_id
ORDER BY date_id;

-- KPI Snapshot: latest quarter
SELECT bank_id, roa, roe, capital_ratio, nim, npl_ratio
FROM bank_kpi_fact
WHERE date_id = (SELECT MAX(date_id) FROM bank_kpi_fact);

-- KPIs by State
SELECT b.state, f.date_id,
       ROUND(AVG(f.roa),4) AS avg_roa,
       ROUND(AVG(f.roe),4) AS avg_roe,
       ROUND(AVG(f.capital_ratio),4) AS avg_capital
FROM bank_kpi_fact f
JOIN bank_dim b ON f.bank_id = b.bank_id
GROUP BY b.state, f.date_id
ORDER BY f.date_id, b.state;
