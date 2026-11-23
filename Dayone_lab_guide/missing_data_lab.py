"""Week 11 Class 1 — independent missing-data lab.

    python missing_data_lab.py
"""
from pathlib import Path
import pandas as pd

DATA = Path(__file__).with_name("gapminder_instructional_missing.csv")
OUTPUT = Path(__file__).with_name("outputs")
REQUIRED = {"country", "continent", "year", "lifeExp", "pop", "gdpPercap"}

def load_and_validate(path: Path) -> pd.DataFrame:
    """Read source, check schema, unique country/year and positive population."""
    df = pd.read_csv(path)

    # Task 1a: Check all 6 required columns exist
    missing_cols = REQUIRED - set(df.columns)
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")

    # Task 1b: One row per country/year - no duplicates
    if df.duplicated(subset=["country", "year"]).any():
        raise ValueError("Duplicate country/year rows found - expected one row per country/year")

    # Task 1c: Population must be positive
    if (df["pop"] <= 0).any():
        raise ValueError("Found pop <= 0 - population must be positive")

    return df

def missingness_report(df: pd.DataFrame) -> pd.DataFrame:
    """Return column, missing_count, missing_pct for every source column."""
    report = pd.DataFrame({
        "column": df.columns,
        "missing_count": df.isna().sum().values,
        # Percentages relative to len(df), rounded to 2 decimals
        "missing_pct": (df.isna().sum() / len(df) * 100).round(2).values
    })
    return report

def impute_data(df: pd.DataFrame) -> pd.DataFrame:
    """Preserve original observed values; mark and fill only specified missing cells."""
    # Work on a copy so we never change the original by accident
    df = df.copy()

    # Task 3: Flags BEFORE any filling - this is the most important order
    df["lifeExp_was_missing"] = df["lifeExp"].isna()
    df["gdpPercap_was_missing"] = df["gdpPercap"].isna()

    # Task 4: Fill continent from other rows of SAME country - no guessing
    # e.g. Brazil 1967 gets "Americas" from Brazil 1952
    df["continent"] = df.groupby("country")["continent"].transform(
        lambda x: x.ffill().bfill()
    )

    # Task 5: lifeExp + gdpPercap with continent median, fallback to global median
    for col in ["lifeExp", "gdpPercap"]:
        global_median = df[col].median()
        continent_median = df.groupby("continent")[col].transform("median")
        df[col] = df[col].fillna(continent_median).fillna(global_median)

    return df

def main() -> None:
    OUTPUT.mkdir(exist_ok=True)
    source = load_and_validate(DATA)
    report = missingness_report(source)
    cleaned = impute_data(source)

    # Task 6: Verify - no NA in targets, no new/deleted rows, observed values unchanged
    assert len(cleaned) == len(source) == 96, f"Row count changed! Got {len(cleaned)}"
    assert cleaned[["continent", "lifeExp", "gdpPercap"]].isna().sum().sum() == 0, "Nulls still left!"
    for col in ["lifeExp", "gdpPercap", "continent"]:
        mask = source[col].notna()
        assert (cleaned.loc[mask, col] == source.loc[mask, col]).all(), f"Observed values changed in {col}"
    print("Validation passed: 96 rows, no nulls, observed values unchanged")
    print(report)

    report.to_csv(OUTPUT / "missingness_report.csv", index=False)
    cleaned.to_csv(OUTPUT / "imputed_gapminder.csv", index=False)
    print("Created reports in", OUTPUT)

if __name__ == "__main__":
    main()