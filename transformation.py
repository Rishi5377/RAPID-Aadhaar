import os
import pandas as pd

# ---- File path ----
FILE_PATH = r"C:\Users\lenovo\Downloads\aadhaar_dataset\enrolment_cleaned.csv"

# ---- Output folder (inside enrolmentfile) ----
OUT_DIR = r"C:\Users\lenovo\Downloads\summaries"
os.makedirs(OUT_DIR, exist_ok=True)

df = pd.read_csv(FILE_PATH)

# ---- Standardize column names ----
df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

# ---- Detect pincode column name (optional) ----
pin_col = None
for c in ["pincode", "pin_code", "pin"]:
    if c in df.columns:
        pin_col = c
        break

# ---- Convert types safely ----
if "date" in df.columns:
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

for c in ["age_0_5", "age_5_17", "age_18_greater"]:
    if c in df.columns:
        df[c] = pd.to_numeric(df[c], errors="coerce")

# ---- Create a total column (sum of age groups if present) ----
age_cols = [c for c in ["age_0_5", "age_5_17", "age_18_greater"] if c in df.columns]
if age_cols:
    df["total_enrolments"] = df[age_cols].sum(axis=1, skipna=True)
else:
    raise ValueError("Age columns not found. Expected age_0_5, age_5_17, age_18_greater")

# =========================
# 1) Total enrolments per state
# =========================
state_summary = (
    df.groupby("state", dropna=False)[age_cols + ["total_enrolments"]]
    .sum(numeric_only=True)
    .sort_values("total_enrolments", ascending=False)
    .reset_index()
)
state_summary.to_csv(os.path.join(OUT_DIR, "total_per_state.csv"), index=False)

# =========================
# 2) Total enrolments per district (within state too)
# =========================
district_summary = (
    df.groupby(["state", "district"], dropna=False)[age_cols + ["total_enrolments"]]
    .sum(numeric_only=True)
    .sort_values("total_enrolments", ascending=False)
    .reset_index()
)
district_summary.to_csv(os.path.join(OUT_DIR, "total_per_district.csv"), index=False)

# =========================
# 3) Total enrolments per pincode (optional)
# =========================
if pin_col:
    pincode_summary = (
        df.groupby(["state", "district", pin_col], dropna=False)[age_cols + ["total_enrolments"]]
        .sum(numeric_only=True)
        .sort_values("total_enrolments", ascending=False)
        .reset_index()
    )
    pincode_summary.to_csv(os.path.join(OUT_DIR, "total_per_pincode.csv"), index=False)

# =========================
# 4) Trend over time (daily / monthly)
# =========================
if "date" in df.columns:
    # Daily trend
    daily_trend = (
        df.dropna(subset=["date"])
        .groupby("date")[age_cols + ["total_enrolments"]]
        .sum(numeric_only=True)
        .reset_index()
        .sort_values("date")
    )
    daily_trend.to_csv(os.path.join(OUT_DIR, "trend_daily.csv"), index=False)

    # Monthly trend
    df_valid_date = df.dropna(subset=["date"]).copy()
    df_valid_date["month"] = df_valid_date["date"].dt.to_period("M").astype(str)

    monthly_trend = (
        df_valid_date.groupby("month")[age_cols + ["total_enrolments"]]
        .sum(numeric_only=True)
        .reset_index()
        .sort_values("month")
    )
    monthly_trend.to_csv(os.path.join(OUT_DIR, "trend_monthly.csv"), index=False)

# =========================
# 5) Overall totals (age group totals)
# =========================
overall = pd.DataFrame([{
    "age_0_5_total": df["age_0_5"].sum(skipna=True) if "age_0_5" in df.columns else None,
    "age_5_17_total": df["age_5_17"].sum(skipna=True) if "age_5_17" in df.columns else None,
    "age_18_greater_total": df["age_18_greater"].sum(skipna=True) if "age_18_greater" in df.columns else None,
    "grand_total_enrolments": df["total_enrolments"].sum(skipna=True),
    "rows_used": len(df)
}])
overall.to_csv(os.path.join(OUT_DIR, "overall_totals.csv"), index=False)

# ---- Print quick highlights ----
print("\n✅ Summaries saved to:", OUT_DIR)

print("\n--- Top 10 States by Total Enrolments ---")
print(state_summary.head(10).to_string(index=False))

print("\n--- Top 10 Districts by Total Enrolments ---")
print(district_summary.head(10).to_string(index=False))

if "date" in df.columns:
    print("\n--- Latest 10 days in Daily Trend (if available) ---")
    print(daily_trend.tail(10).to_string(index=False))
