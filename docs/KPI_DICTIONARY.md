# KPI Dictionary

This document defines the core metrics used in the **Bank Health KPI Dashboard**, including formulas, interpretation, and edge cases.

---
### Return on Assets (ROA)
Formula: `NETINC / ASSET`  

**Interpretation:**  
Measures profitability relative to total assets. Indicates how efficiently a bank generates income from its asset base.  

**Inputs:** `netinc`, `asset`  

**Edge Cases:**  
- If `asset <= 0` or NULL → set ROA = NULL  
- No imputation; surface missingness in Issue Log 

### Return on Equity (ROE)
Formula: `NETINC / EQ`  

**Interpretation:**  
Measures profitability relative to equity. Shows how much profit is generated per dollar of shareholder equity.  

**Inputs:** `netinc`, `eq`  

**Edge Cases:**  
- If `eq <= 0` or NULL → set ROE = NULL  
- Negative equity can produce extreme values; retain but document in Issue Log 

### Capital Ratio
Formula: `EQ / ASSET`  

**Interpretation:**  
Basic proxy for capital adequacy. Higher ratios indicate stronger ability to absorb losses.  

**Inputs:** `eq`, `asset`  

**Edge Cases:**  
- If `asset <= 0` or NULL → set Capital Ratio = NULL

### Net Interest Margin (NIM)
Formula: `(INTINC - INTEXP) / EARNASST`

**Interpretation:**  
Core banking metric showing net interest income relative to earning assets. Captures lending efficiency.  

**Inputs:** `intinc`, `intexp`, `earnasst`  

**Edge Cases:**  
- If `earnasst <= 0` or missing → set NIM = NULL  
- If any input missing, document in Issue Log  

### Non-Performing Loan Ratio (NPL)
Formula: `NPL / LOANS`

**Interpretation:**  
Credit quality proxy. Shows the proportion of loans that are non-performing.  

**Inputs:** `npl`, `loans`  

**Edge Cases:**  
- If `loans <= 0` or NULL → set NPL Ratio = NULL  
- Outliers (sudden spikes) should be retained but documented  

---

## Data Lineage
- All KPI inputs are sourced from **FDIC BankFind Financials API**.  
- Staging table: `staging_fdic_bank` (cert, repdte, assets, equity, income, loans, etc.).  
- Dimensions:  
  - `bank_dim` (metadata, location, charter info)  
  - `date_dim` (calendar)  
- Facts: `bank_kpi_fact` (one row per bank per reporting date).  

---

## Data-Quality Principles
- Prefer NULL over imputation unless there is a strong business rule.  
- Outliers are not removed if they reflect real events.  
- Track all anomalies in **docs/Issue_Log.csv**.  

---

## Units & Rounding
- Ratios stored as decimal fractions (e.g., `0.034 = 3.4%`).  
- Round for presentation (1–2 decimals in dashboards). 