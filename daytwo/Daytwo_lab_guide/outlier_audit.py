"""Week 11 Class 2 independent lab — Wine Chemistry Outlier Audit."""
from pathlib import Path
import pandas as pd

REQUIRED = ["sample_id", "alcohol", "malic_acid", "color_intensity", "proline", "target"]

def _z_flags(s: pd.Series) -> pd.Series:
    # |Z| > 3, ddof=0, zero-variance safe
    mean, std = s.mean(), s.std(ddof=0)
    if pd.isna(std) or std == 0:
        return pd.Series(False, index=s.index)
    return ((s - mean) / std).abs() > 3

def _iqr_flags(s: pd.Series) -> pd.Series:
    # 1.5x IQR, default Pandas quantiles, zero-variance safe
    q1, q3 = s.quantile(0.25), s.quantile(0.75)
    iqr = q3 - q1
    if pd.isna(iqr) or iqr == 0:
        return pd.Series(False, index=s.index)
    lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    return (s < lower) | (s > upper)

def audit_data(data: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Return retained, quarantine and quality summary tables."""
    # 1. Validate schema - fail clearly
    missing = [c for c in REQUIRED if c not in data.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    df = data.copy()  # preserve raw values

    # 2. Z and IQR for two columns, independently
    for col in ["malic_acid", "proline"]:
        df[f"{col}_z_flag"] = _z_flags(df[col])
        df[f"{col}_iqr_flag"] = _iqr_flags(df[col])

    # 3. Domain sanity checks - ONLY these are invalid
    df["proline_invalid"] = df["proline"] <= 0
    df["malic_acid_invalid"] = (df["malic_acid"] < 0) | (df["malic_acid"].isna())

    # 4. review_needed = any statistical OR validity flag
    flag_cols = [c for c in df.columns if c.endswith("_flag") or c.endswith("_invalid")]
    df["review_needed"] = df[flag_cols].any(axis=1)

    # 5. Quarantine ONLY domain-invalid. Statistical outlier alone stays.
    is_invalid = df["proline_invalid"] | df["malic_acid_invalid"]
    quarantined = df[is_invalid].copy()
    retained = df[~is_invalid].copy()

    # 6. Summary - total, retained, quarantined, Z and IQR separately
    summary = pd.DataFrame([
        {"metric": "total_input", "malic_acid": len(df), "proline": len(df)},
        {"metric": "retained", "malic_acid": len(retained), "proline": len(retained)},
        {"metric": "quarantined", "malic_acid": len(quarantined), "proline": len(quarantined)},
        {"metric": "z_flag_count", "malic_acid": int(df["malic_acid_z_flag"].sum()), "proline": int(df["proline_z_flag"].sum())},
        {"metric": "iqr_flag_count", "malic_acid": int(df["malic_acid_iqr_flag"].sum()), "proline": int(df["proline_iqr_flag"].sum())},
        {"metric": "review_needed_count", "malic_acid": int(df["review_needed"].sum()), "proline": int(df["review_needed"].sum())},
    ])

    return {
        "retained": retained,
        "quarantined": quarantined,
        "summary": summary,
        # also return full for tests if needed
        "flagged": df,
    }

if __name__ == "__main__":
    # File is next to this script: wine_quality_case_PUBLIC_DERIVED.csv
    base = Path(__file__).parent
    data_path = base / "wine_quality_case_PUBLIC_DERIVED.csv"
    data = pd.read_csv(data_path)
    results = audit_data(data)

    # Save all three CSVs with documented relative paths
    out_dir = base / "outputs"
    out_dir.mkdir(exist_ok=True)
    results["retained"].to_csv(out_dir / "retained_flagged.csv", index=False)
    results["quarantined"].to_csv(out_dir / "quarantined_records.csv", index=False)
    results["summary"].to_csv(out_dir / "quality_summary.csv", index=False)

    print(results["summary"])
    print(f"Retained: {len(results['retained'])} | Quarantined: {len(results['quarantined'])}")