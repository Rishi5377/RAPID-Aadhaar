import os
import re
from pathlib import Path
import pandas as pd
import numpy as np

# -----------------------------
# CONFIG (DO NOT CHANGE NOW)
# -----------------------------
BASE_DIR = Path(r"C:\Users\Tanuja\Downloads\api")
INPUT_DIR = BASE_DIR
OUTPUT_DIR = BASE_DIR / "cleaned"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

CLEANED_OUT = OUTPUT_DIR / "enrolment_cleaned.csv"
REPORT_OUT = OUTPUT_DIR / "data_quality_report.csv"

EXPECTED_COLS = [
    "date", "state", "district", "pincode",
    "age_0_5", "age_5_17", "age_18_greater"
]

AGE_COLS = ["age_0_5", "age_5_17", "age_18_greater"]

# -----------------------------
# Helpers
# -----------------------------
def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.lower()
        .str.replace(r"[^\w]+", "_", regex=True)
        .str.strip("_")
    )
    rename_map = {
        "pin_code": "pincode",
        "pin": "pincode",
        "district_name": "district",
        "state_name": "state",
        "age_18": "age_18_greater",
        "age_18_plus": "age_18_greater",
    }
    df = df.rename(columns={c: rename_map.get(c, c) for c in df.columns})
    return df


def clean_text(s: pd.Series) -> pd.Series:
    s = s.astype(str)
    s = s.str.replace(r"\s+", " ", regex=True).str.strip()
    s = s.str.lower().str.title()
    s = s.replace({"Nan": np.nan, "None": np.nan, "": np.nan})
    return s


def clean_date(col: pd.Series) -> pd.Series:
    return pd.to_datetime(col, errors="coerce", dayfirst=True)


def clean_pincode(col: pd.Series) -> pd.Series:
    col = col.astype(str).str.replace(r"\D", "", regex=True)
    col = col.where(col.str.len() == 6, np.nan)
    return col


def clean_numeric(col: pd.Series) -> pd.Series:
    col = col.astype(str).str.replace(",", "").str.strip()
    return pd.to_numeric(col, errors="coerce")


def find_excel_files(folder: Path):
    exts = (".xlsx", ".xls", ".xlsm")
    return [p for p in folder.rglob("*") if p.suffix.lower() in exts]


# -----------------------------
# Main pipeline
# -----------------------------

def load_all_excels(input_dir: Path) -> pd.DataFrame:
    files = find_excel_files(input_dir)
    if not files:
        raise FileNotFoundError(f"No Excel files found in {input_dir}")

    dfs = []

    for f in files:
        # Read ALL sheets from the Excel file
        sheets_dict = pd.read_excel(f, sheet_name=None)

        for sheet_name, df in sheets_dict.items():
            df["__source_file"] = str(f)
            df["__sheet_name"] = sheet_name
            dfs.append(df)

    # Combine all sheets from all files into ONE dataframe
    return pd.concat(dfs, ignore_index=True)


def clean_enrolment(df: pd.DataFrame):
    df = standardize_columns(df)

    for c in EXPECTED_COLS:
        if c not in df.columns:
            df[c] = np.nan

    cols = EXPECTED_COLS.copy()
    if "__source_file" in df.columns:
        cols.append("__source_file")

    df = df[cols]

    df["date"] = clean_date(df["date"])
    df["state"] = clean_text(df["state"])
    df["district"] = clean_text(df["district"])
    df["pincode"] = clean_pincode(df["pincode"])

    for c in AGE_COLS:
        df[c] = clean_numeric(df[c])
        df.loc[df[c] < 0, c] = np.nan

    before = len(df)
    df = df.drop_duplicates(subset=EXPECTED_COLS)
    duplicates_removed = before - len(df)

    report = pd.DataFrame([
        {"metric": "rows_final", "value": len(df)},
        {"metric": "duplicates_removed", "value": duplicates_removed}
    ])

    return df, report


def main():
    print("Loading Excel files...")
    raw = load_all_excels(INPUT_DIR)

    print("Cleaning data...")
    cleaned, report = clean_enrolment(raw)

    cleaned.to_csv(CLEANED_OUT, index=False)
    report.to_csv(REPORT_OUT, index=False)

    print("✅ DONE")
    print(f"Cleaned file saved at: {CLEANED_OUT}")
    print(f"Report saved at: {REPORT_OUT}")


if __name__ == "__main__":
    main()
