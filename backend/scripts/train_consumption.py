"""Train per-target regression models predicting machine consumption.

Reads readings from cafetalino.db, trains 5 independent regressors (one
per ingredient/stock target) on [location_id, days_since_previous_refill,
day_of_week, month, historical_mean_<target> for each target], evaluates
each on a held-out test split, then refits the best-performing model type
on the full dataset and persists it to data/models/. Also writes a
consolidated metrics report to data/metrics/.
"""

from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingRegressor, RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score, root_mean_squared_error
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

BACKEND_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BACKEND_DIR / "data" / "cafetalino.db"
MODELS_DIR = BACKEND_DIR / "data" / "models"
METRICS_DIR = BACKEND_DIR / "data" / "metrics"

RAW_FEATURE_COLUMNS = ["location_id", "days_since_previous_refill"]
TARGETS = [
    "bottled_water_ml",
    "cup_units",
    "coffee_mix_g",
    "chocolate_mix_g",
    "cappuccino_mix_g",
]
HISTORICAL_MEAN_COLUMNS = [f"historical_mean_{target}" for target in TARGETS]
FEATURE_COLUMNS = [
    "location_id",
    "days_since_previous_refill",
    "day_of_week",
    "month",
    *HISTORICAL_MEAN_COLUMNS,
]

CANDIDATE_MODELS = {
    "random_forest": lambda: RandomForestRegressor(n_estimators=300, random_state=42, n_jobs=-1),
    "hist_gradient_boosting": lambda: HistGradientBoostingRegressor(random_state=42),
}


def load_training_data(conn: sqlite3.Connection) -> tuple[pd.DataFrame, int]:
    df = pd.read_sql(f"SELECT date, {', '.join(RAW_FEATURE_COLUMNS + TARGETS)} FROM readings", conn)

    parsed_date = pd.to_datetime(df["date"])
    df["day_of_week"] = parsed_date.dt.dayofweek
    df["month"] = parsed_date.dt.month

    # Historical mean must only look at strictly-prior readings for that
    # location (shift(1) before expanding()), otherwise a row would see its
    # own target value baked into its own feature.
    df = df.sort_values(["location_id", "date"]).reset_index(drop=True)
    for target in TARGETS:
        df[f"historical_mean_{target}"] = df.groupby("location_id")[target].transform(
            lambda s: s.shift(1).expanding().mean()
        )

    before = len(df)
    df = df.dropna(subset=FEATURE_COLUMNS).reset_index(drop=True)
    dropped = before - len(df)
    print(f"dropped {dropped} rows with missing features (cold-start/first readings) ({before} -> {len(df)})")
    return df, dropped


def build_pipeline(model) -> Pipeline:
    categorical_columns = ["location_id", "day_of_week", "month"]
    preprocess = ColumnTransformer(
        transformers=[
            ("categorical_ohe", OneHotEncoder(handle_unknown="ignore", sparse_output=False), categorical_columns)
        ],
        remainder="passthrough",
    )
    return Pipeline([("preprocess", preprocess), ("model", model)])


def evaluate_candidates(df: pd.DataFrame, target: str, train_idx, test_idx) -> tuple[str, dict]:
    X_train, X_test = df.loc[train_idx, FEATURE_COLUMNS], df.loc[test_idx, FEATURE_COLUMNS]
    y_train, y_test = df.loc[train_idx, target], df.loc[test_idx, target]

    results = {}
    for name, make_model in CANDIDATE_MODELS.items():
        pipeline = build_pipeline(make_model())
        pipeline.fit(X_train, y_train)
        preds = pipeline.predict(X_test)
        mae = mean_absolute_error(y_test, preds)
        rmse = root_mean_squared_error(y_test, preds)
        r2 = r2_score(y_test, preds)
        results[name] = {"mae": mae, "rmse": rmse, "r2": r2}
        print(f"    {name:>24}: MAE={mae:8.2f}  RMSE={rmse:8.2f}  R2={r2:6.3f}")

    best_name = min(results, key=lambda n: results[n]["mae"])
    return best_name, results[best_name]


def main() -> None:
    conn = sqlite3.connect(DB_PATH)
    try:
        df, dropped_rows = load_training_data(conn)
    finally:
        conn.close()

    train_idx, test_idx = train_test_split(df.index, test_size=0.2, random_state=42)

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    METRICS_DIR.mkdir(parents=True, exist_ok=True)
    valid_location_ids = sorted(df["location_id"].unique().tolist())

    print("\n=== Model selection (MAE/RMSE on held-out 20% test split) ===")
    summary = []
    for target in TARGETS:
        print(f"\n{target}:")
        best_name, best_metrics = evaluate_candidates(df, target, train_idx, test_idx)
        print(f"  -> selected: {best_name}")

        # Refit the winning model type on the FULL dataset for the deployed artifact.
        final_pipeline = build_pipeline(CANDIDATE_MODELS[best_name]())
        final_pipeline.fit(df[FEATURE_COLUMNS], df[target])

        artifact = {
            "pipeline": final_pipeline,
            "target": target,
            "model_name": best_name,
            "feature_columns": FEATURE_COLUMNS,
            "valid_location_ids": valid_location_ids,
            "test_mae": best_metrics["mae"],
            "test_rmse": best_metrics["rmse"],
            "test_r2": best_metrics["r2"],
            "n_train_rows": len(df),
        }
        out_path = MODELS_DIR / f"{target}.joblib"
        joblib.dump(artifact, out_path)
        summary.append((target, best_name, best_metrics["mae"], best_metrics["rmse"], best_metrics["r2"], out_path))

    print("\n=== Done ===")
    header = f"{'target':<20}{'model':<24}{'MAE':>10}{'RMSE':>10}{'R2':>8}"
    rows = [f"{target:<20}{name:<24}{mae:>10.2f}{rmse:>10.2f}{r2:>8.3f}" for target, name, mae, rmse, r2, path in summary]
    print(header)
    for row in rows:
        print(row)
    print(f"\nartifacts written to: {MODELS_DIR}")

    now = datetime.now()
    model_names = "-".join(sorted({name for _, name, *_ in summary}))
    metrics_path = METRICS_DIR / f"{model_names}_{now.strftime('%Y%m%d_%H%M%S')}.txt"
    metrics_path.write_text(
        "Cafetalino consumption model training run\n"
        f"timestamp: {now.isoformat(timespec='seconds')}\n"
        f"training rows: {len(df)} (dropped {dropped_rows} cold-start/null-feature rows)\n\n"
        f"{header}\n" + "\n".join(rows) + "\n"
    )
    print(f"metrics written to: {metrics_path}")


if __name__ == "__main__":
    main()
