# Summaries Folder — File Guide

This folder contains aggregated outputs generated from `enrolment_cleaned.csv` (Aadhaar enrolment dataset).  
Each file is a **summary table** created by grouping the raw rows and summing the enrolment counts for the age categories.

> **Age columns used**
- `age_0_5` → enrolments for ages 0–5  
- `age_5_17` → enrolments for ages 5–17  
- `age_18_greater` → enrolments for ages 18+  
- `total_enrolments` → row-wise total = `age_0_5 + age_5_17 + age_18_greater`

---

## 1) `total_per_state.csv`

**What it contains:**  
State-level aggregation of enrolment counts.

**How it is computed:**  
All rows are grouped by `state`, and the values of `age_0_5`, `age_5_17`, `age_18_greater`, and `total_enrolments` are summed.

**Why it is useful:**  
Helps identify which states have the highest overall enrolment volume and enables state-to-state comparison.

---

## 2) `total_per_district.csv`

**What it contains:**  
District-level aggregation within each state.

**How it is computed:**  
Rows are grouped by `state` and `district`, then enrolment counts are summed across the same age columns and `total_enrolments`.

**Why it is useful:**  
Helps drill down beyond state totals to find top-performing districts and understand local patterns.

---

## 3) `total_per_pincode.csv` *(optional)*

**When it is created:**  
Only generated if the dataset contains a pincode column such as `pincode` / `pin_code`.

**What it contains:**  
Pincode-level aggregation within each district and state.

**How it is computed:**  
Rows are grouped by `state`, `district`, and `pincode`, then enrolment counts are summed.

**Why it is useful:**  
Provides fine-grained geographic analysis (micro-region insights) helpful for mapping, targeted outreach, and service planning.

---

## 4) `trend_daily.csv`

**What it contains:**  
Day-by-day time-series totals.

**How it is computed:**  
Rows are grouped by `date` (after converting it into a valid datetime).  
Enrolment counts are summed for each day.

**Why it is useful:**  
Helps track spikes/drops in enrolment over time and analyze operational or seasonal patterns.

---

## 5) `trend_monthly.csv`

**What it contains:**  
Month-by-month time-series totals.

**How it is computed:**  
Each row’s `date` is converted to a month bucket (e.g., `2025-11`).  
Rows are grouped by month and summed.

**Why it is useful:**  
Makes long-term trends easier to interpret than daily data and supports reporting dashboards.

---

## 6) `overall_totals.csv`

**What it contains:**  
A single-row summary of grand totals.

**How it is computed:**  
Total sum of each age column across the entire dataset, plus:
- `grand_total_enrolments` = total of `total_enrolments`
- `rows_used` = number of rows processed

**Why it is useful:**  
Quick “one-glance” KPI snapshot for the entire dataset and a useful validation checkpoint.

---

## Notes / Interpretation Tips

- These files are **not raw data** — they are aggregated outputs created for analysis and visualization.
- If your dataset contains missing/invalid `date`, those rows may be excluded from `trend_daily.csv` and `trend_monthly.csv`.
- If state/district spellings differ (e.g., extra spaces, different casing), totals may split across multiple entries unless standardized.
