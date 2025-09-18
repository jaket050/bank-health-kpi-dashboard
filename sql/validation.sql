SELECT repdte, COUNT(*) AS banks
FROM staging_fdic_bank
GROUP BY repdte
ORDER BY repdte;

SELECT COUNT(*) AS fact_rows FROM bank_kpi_fact;
