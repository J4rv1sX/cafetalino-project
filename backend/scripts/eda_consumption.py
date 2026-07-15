"""EDA over the historical vending-machine consumption export.

First concrete step toward replacing the hardcoded roster in
app/data/machines.py with real data. Produces a canonical location
roster (grouping by coordinates rather than machine_id, since units
churn independently of physical placement) for human review before any
DB schema is decided.
"""

from __future__ import annotations

import difflib
import unicodedata
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd

from _shared import CSV_PATH, build_canonical_locations, filter_active, load_data

BACKEND_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BACKEND_DIR / "data" / "eda_output"
PLOTS_DIR = OUTPUT_DIR / "plots"

pd.set_option("display.width", 200)
pd.set_option("display.max_columns", 20)
pd.set_option("display.max_colwidth", 60)


def print_overview(df: pd.DataFrame) -> None:
    print("=== Overview ===")
    print(f"shape: {df.shape}")
    print(f"\ndate range: {df['date'].min().date()} .. {df['date'].max().date()}")

    missing = df.isna().sum()
    missing_pct = (missing / len(df) * 100).round(1)
    print("\nmissing values per column:")
    print(pd.DataFrame({"n_missing": missing, "pct_missing": missing_pct}))

    print("\nstatus value counts:")
    print(df["status"].value_counts())

    print(
        f"\nbefore filtering: {df['raw_location_name'].nunique()} unique location-name strings "
        f"vs {df['machine_id'].nunique()} unique machine_id values "
        "(machine_id churns independently of physical location, hence it's dropped below)"
    )


def normalize_name(name: str) -> str:
    stripped = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode("ascii")
    return " ".join(stripped.lower().split())


def find_near_duplicate_names(roster: pd.DataFrame, threshold: float = 0.75) -> pd.DataFrame:
    print("\n=== Near-duplicate name check (coordinates differ, names look similar) ===")
    normalized = roster["name"].map(normalize_name)

    warnings = []
    for i in range(len(roster)):
        for j in range(i + 1, len(roster)):
            ratio = difflib.SequenceMatcher(None, normalized[i], normalized[j]).ratio()
            if ratio >= threshold:
                warnings.append(
                    {
                        "name_a": roster.loc[i, "name"],
                        "name_b": roster.loc[j, "name"],
                        "similarity": round(ratio, 2),
                        "lat_a": roster.loc[i, "lat"],
                        "lng_a": roster.loc[i, "lng"],
                        "lat_b": roster.loc[j, "lat"],
                        "lng_b": roster.loc[j, "lng"],
                    }
                )

    warnings_df = pd.DataFrame(warnings)
    if warnings_df.empty:
        print("none found.")
    else:
        print(f"{len(warnings_df)} possible duplicate pair(s) -- needs human review, nothing auto-merged:")
        print(warnings_df)
    return warnings_df


def report_missing_and_outliers(active: pd.DataFrame) -> None:
    print("\n=== Missing values (active rows) ===")
    missing = active.isna().sum()
    print(missing[missing > 0])

    print("\n=== Range sanity checks ===")
    bad_pct = active[(active["water_remaining_pct"] < 0) | (active["water_remaining_pct"] > 100)]
    print(f"water_remaining_pct out of [0, 100]: {len(bad_pct)} rows")

    count_cols = [
        "cups",
        "days_since_previous_refill",
        "bottled_water_ml",
        "cup_units",
        "coffee_mix_g",
        "chocolate_mix_g",
        "cappuccino_mix_g",
    ]
    for col in count_cols:
        n_negative = (active[col] < 0).sum()
        if n_negative:
            print(f"{col}: {n_negative} negative values")

    print("\n=== describe() with extended percentiles ===")
    print(active[count_cols].describe(percentiles=[0.01, 0.05, 0.5, 0.95, 0.99]))


def make_plots(active: pd.DataFrame, roster: pd.DataFrame, plots_dir: Path) -> None:
    plots_dir.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(8, 6))
    ordered = roster.sort_values("reading_count")
    ax.barh(ordered["name"], ordered["reading_count"])
    ax.set_xlabel("readings")
    ax.set_title("Readings per canonical location")
    fig.tight_layout()
    fig.savefig(plots_dir / "readings_per_location.png")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.hist(active["water_remaining_pct"].dropna(), bins=20)
    ax.set_xlabel("water_remaining_pct")
    ax.set_title("Distribution of water remaining (%)")
    fig.tight_layout()
    fig.savefig(plots_dir / "water_remaining_pct_distribution.png")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.hist(active["days_since_previous_refill"].dropna(), bins=20)
    ax.set_xlabel("days_since_previous_refill")
    ax.set_title("Distribution of days since previous refill")
    fig.tight_layout()
    fig.savefig(plots_dir / "days_since_previous_refill_distribution.png")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 4))
    monthly = active.set_index("date").resample("ME").size()
    ax.plot(monthly.index, monthly.values)
    ax.set_ylabel("active readings")
    ax.set_title("Active readings per month")
    fig.tight_layout()
    fig.savefig(plots_dir / "readings_per_month.png")
    plt.close(fig)

    print(f"\nsaved 4 plots to {plots_dir}")


def main() -> None:
    df = load_data(CSV_PATH)
    print_overview(df)

    active = filter_active(df)
    roster = build_canonical_locations(active)
    warnings_df = find_near_duplicate_names(roster)
    report_missing_and_outliers(active)
    make_plots(active, roster, PLOTS_DIR)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    roster_path = OUTPUT_DIR / "canonical_locations.csv"
    roster.to_csv(roster_path, index=False)

    print("\n=== Done ===")
    print(f"canonical roster: {roster_path} ({len(roster)} locations)")
    print(f"near-duplicate warnings: {len(warnings_df)}")
    print(f"plots: {PLOTS_DIR}")


if __name__ == "__main__":
    main()
