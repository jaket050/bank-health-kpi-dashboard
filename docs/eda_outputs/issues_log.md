# Issues Log

This file documents data and pipeline issues discovered during analysis, along with their resolutions.  
It serves as a quality audit trail for the project.

| Date       | Issue                                     | Impact                           | Resolution                                                         | Status  |
|------------|-------------------------------------------|----------------------------------|---------------------------------------------------------------------|---------|
| 2025-09-28 | Postgres AVG() returned NaN for ROA/ROE   | Blocked KPI validation           | Verified via Pandas (ROA 0.72%, ROE 6.3%); documented in EDA       | Closed  |
| 2025-09-28 | Duplicate rows flagged in Pandas check    | Raised concern about ETL quality | Confirmed no DB duplicates (bank_id+date_id). Caused by missing key in query; fixed by adding bank_id | Closed  |
| 2025-09-26 | Region mapping “Territories” missing      | Chart rendering KeyError         | Added “Territories” to region_order list in preprocessing           | Closed  |
| 2025-09-20 | Outliers in KPI distributions (ROA, ROE)  | Skewed averages & charts         | Applied winsorization at 1st/99th percentiles                       | Closed  |
|
