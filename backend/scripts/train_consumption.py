"""Train per-target regression models predicting machine consumption.

Reads readings from cafetalino.db, trains 5 independent regressors (one
per ingredient/stock target) on [location_id, days_since_previous_refill,
day_of_week, month, historical_mean_<target>, recent_mean_<target>,
historical_rate_<target>, recent_rate_<target> for each target]. The rate
features (mean-per-day-since-refill) let the model use that ratio directly
rather than re-deriving it from days_since_previous_refill interactions --
see docs/CONSUMPTION_MODEL.md for the CV MAE comparison that justified
adding them. For each target, searches each candidate model's
hyperparameter space via RandomizedSearchCV (5-fold CV), picks the
best-performing model type as the point estimate, and additionally fits
a HistGradientBoostingRegressor quantile-loss pair (5th/95th percentile)
for a prediction interval (empirically ~80% coverage after compensating
for small-data quantile under-coverage -- see docs/CONSUMPTION_MODEL.md).
Persists all three pipelines per target to data/models/, and writes a
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
from sklearn.model_selection import KFold, RandomizedSearchCV, cross_val_predict
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
RECENT_MEAN_COLUMNS = [f"recent_mean_{target}" for target in TARGETS]
HISTORICAL_RATE_COLUMNS = [f"historical_rate_{target}" for target in TARGETS]
RECENT_RATE_COLUMNS = [f"recent_rate_{target}" for target in TARGETS]
FEATURE_COLUMNS = [
    "location_id",
    "days_since_previous_refill",
    "day_of_week",
    "month",
    *HISTORICAL_MEAN_COLUMNS,
    *RECENT_MEAN_COLUMNS,
    *HISTORICAL_RATE_COLUMNS,
    *RECENT_RATE_COLUMNS,
]
# Guards historical_rate_/recent_rate_ divisions -- days-between-refills is
# never 0 in this dataset, but this keeps a same-day double-reading from
# ever producing a division by zero.
RATE_EPS = 1e-6

CANDIDATE_MODELS = {
    "random_forest": lambda: RandomForestRegressor(random_state=42),
    "hist_gradient_boosting": lambda: HistGradientBoostingRegressor(random_state=42),
}

PARAM_DISTRIBUTIONS = {
    "random_forest": {
        "model__n_estimators": [200, 300, 500],
        "model__max_depth": [None, 5, 10, 20],
        "model__min_samples_leaf": [1, 2, 5],
        "model__max_features": ["sqrt", 1.0],
    },
    "hist_gradient_boosting": {
        "model__max_depth": [None, 3, 5, 10, 15],
        "model__min_samples_leaf": [10, 20, 30, 50, 75, 100],
        "model__learning_rate": [0.01, 0.03, 0.05, 0.1, 0.2],
        "model__l2_regularization": [0.0, 0.1, 0.5, 1.0, 2.0],
    },
}
N_ITER = 30
INTERVAL_QUANTILES = (0.05, 0.95)

CV = KFold(n_splits=5, shuffle=True, random_state=42)
SCORING = {"mae": "neg_mean_absolute_error", "rmse": "neg_root_mean_squared_error", "r2": "r2"}


def load_training_data(conn: sqlite3.Connection) -> tuple[pd.DataFrame, int]:
    df = pd.read_sql(f"SELECT date, {', '.join(RAW_FEATURE_COLUMNS + TARGETS)} FROM readings", conn)

    parsed_date = pd.to_datetime(df["date"])
    df["day_of_week"] = parsed_date.dt.dayofweek
    df["month"] = parsed_date.dt.month

    # Both lag features must only look at strictly-prior readings for that
    # location (shift(1) before expanding()/rolling()), otherwise a row
    # would see its own target value baked into its own feature.
    df = df.sort_values(["location_id", "date"]).reset_index(drop=True)
    for target in TARGETS:
        grouped = df.groupby("location_id")[target]
        df[f"historical_mean_{target}"] = grouped.transform(lambda s: s.shift(1).expanding().mean())
        df[f"recent_mean_{target}"] = grouped.transform(lambda s: s.shift(1).rolling(window=3, min_periods=1).mean())

    grouped_days = df.groupby("location_id")["days_since_previous_refill"]
    df["historical_mean_days"] = grouped_days.transform(lambda s: s.shift(1).expanding().mean())
    df["recent_mean_days"] = grouped_days.transform(lambda s: s.shift(1).rolling(window=3, min_periods=1).mean())
    for target in TARGETS:
        df[f"historical_rate_{target}"] = df[f"historical_mean_{target}"] / (df["historical_mean_days"] + RATE_EPS)
        df[f"recent_rate_{target}"] = df[f"recent_mean_{target}"] / (df["recent_mean_days"] + RATE_EPS)

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


def _strip_prefix(params: dict, prefix: str = "model__") -> dict:
    return {k.removeprefix(prefix): v for k, v in params.items()}


def evaluate_candidates(df: pd.DataFrame, target: str) -> tuple[str, dict, dict]:
    X, y = df[FEATURE_COLUMNS], df[target]

    results = {}
    for name, make_model in CANDIDATE_MODELS.items():
        search = RandomizedSearchCV(
            build_pipeline(make_model()),
            param_distributions=PARAM_DISTRIBUTIONS[name],
            n_iter=N_ITER,
            cv=CV,
            scoring=SCORING,
            refit="mae",
            random_state=42,
            n_jobs=-1,
        )
        search.fit(X, y)
        idx = search.best_index_
        cvres = search.cv_results_

        metrics = {
            "mae": -cvres["mean_test_mae"][idx],
            "mae_std": cvres["std_test_mae"][idx],
            "rmse": -cvres["mean_test_rmse"][idx],
            "rmse_std": cvres["std_test_rmse"][idx],
            "r2": cvres["mean_test_r2"][idx],
            "r2_std": cvres["std_test_r2"][idx],
            "best_params": search.best_params_,
            "best_estimator": search.best_estimator_,
        }
        results[name] = metrics
        print(
            f"    {name:>24}: MAE={metrics['mae']:8.2f}±{metrics['mae_std']:<6.2f} "
            f"RMSE={metrics['rmse']:8.2f}±{metrics['rmse_std']:<6.2f} "
            f"R2={metrics['r2']:6.3f}±{metrics['r2_std']:.3f}  params={metrics['best_params']}"
        )

    best_name = min(results, key=lambda n: results[n]["mae"])
    return best_name, results[best_name], results


def fit_interval_pipelines(df: pd.DataFrame, target: str, hgb_params: dict) -> tuple[Pipeline, Pipeline, float]:
    X, y = df[FEATURE_COLUMNS], df[target]
    low_q, high_q = INTERVAL_QUANTILES

    def make_quantile_model(quantile: float) -> HistGradientBoostingRegressor:
        return HistGradientBoostingRegressor(loss="quantile", quantile=quantile, random_state=42, **hgb_params)

    lower_pipeline = build_pipeline(make_quantile_model(low_q))
    upper_pipeline = build_pipeline(make_quantile_model(high_q))

    # Out-of-fold predictions to measure empirical coverage -- fitting on the
    # full data first would let each row "see itself," giving an
    # over-optimistic coverage number.
    lower_oof = cross_val_predict(build_pipeline(make_quantile_model(low_q)), X, y, cv=CV)
    upper_oof = cross_val_predict(build_pipeline(make_quantile_model(high_q)), X, y, cv=CV)
    coverage = float(((y >= lower_oof) & (y <= upper_oof)).mean())

    lower_pipeline.fit(X, y)
    upper_pipeline.fit(X, y)
    return lower_pipeline, upper_pipeline, coverage


def main() -> None:
    conn = sqlite3.connect(DB_PATH)
    try:
        df, dropped_rows = load_training_data(conn)
    finally:
        conn.close()

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    METRICS_DIR.mkdir(parents=True, exist_ok=True)
    valid_location_ids = sorted(df["location_id"].unique().tolist())

    print(f"\n=== Model selection ({N_ITER}-iter randomized search, {CV.get_n_splits()}-fold CV, mean±std) ===")
    summary = []
    for target in TARGETS:
        print(f"\n{target}:")
        best_name, best_metrics, all_results = evaluate_candidates(df, target)
        print(f"  -> selected: {best_name}")

        hgb_params = _strip_prefix(all_results["hist_gradient_boosting"]["best_params"])
        lower_pipeline, upper_pipeline, coverage = fit_interval_pipelines(df, target, hgb_params)
        print(f"  -> {round(100 * (INTERVAL_QUANTILES[1] - INTERVAL_QUANTILES[0]))}% interval coverage: {coverage:.1%}")

        artifact = {
            "pipeline": best_metrics["best_estimator"],
            "lower_pipeline": lower_pipeline,
            "upper_pipeline": upper_pipeline,
            "target": target,
            "model_name": best_name,
            "feature_columns": FEATURE_COLUMNS,
            "valid_location_ids": valid_location_ids,
            "hyperparameters": best_metrics["best_params"],
            "test_mae": best_metrics["mae"],
            "test_mae_std": best_metrics["mae_std"],
            "test_rmse": best_metrics["rmse"],
            "test_rmse_std": best_metrics["rmse_std"],
            "test_r2": best_metrics["r2"],
            "test_r2_std": best_metrics["r2_std"],
            "interval_coverage": coverage,
            "n_train_rows": len(df),
        }
        out_path = MODELS_DIR / f"{target}.joblib"
        joblib.dump(artifact, out_path)
        summary.append((target, best_name, best_metrics, coverage, out_path))

    print("\n=== Done ===")
    header = f"{'target':<20}{'model':<24}{'MAE':>18}{'RMSE':>18}{'R2':>14}{'coverage':>10}  hyperparameters"
    rows = [
        f"{target:<20}{name:<24}"
        f"{m['mae']:>8.2f}±{m['mae_std']:<8.2f}"
        f"{m['rmse']:>8.2f}±{m['rmse_std']:<8.2f}"
        f"{m['r2']:>6.3f}±{m['r2_std']:<6.3f}"
        f"{coverage:>9.1%}  {m['best_params']}"
        for target, name, m, coverage, path in summary
    ]
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
