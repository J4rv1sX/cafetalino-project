import sqlite3
from datetime import date
from functools import lru_cache
from pathlib import Path

import joblib
import pandas as pd

from app.schemas.consumption import (
    ConsumptionPredictionResponse,
    LocationConsumptionPrediction,
    PredictionInterval,
)

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
MODELS_DIR = BACKEND_DIR / "data" / "models"
DB_PATH = BACKEND_DIR / "data" / "cafetalino.db"

TARGETS = [
    "bottled_water_ml",
    "cup_units",
    "coffee_mix_g",
    "chocolate_mix_g",
    "cappuccino_mix_g",
]


@lru_cache
def _load_artifacts() -> dict[str, dict]:
    artifacts = {}
    for target in TARGETS:
        path = MODELS_DIR / f"{target}.joblib"
        if not path.exists():
            raise RuntimeError(
                f"Missing model artifact: {path}. Run `uv run python scripts/train_consumption.py` first."
            )
        artifacts[target] = joblib.load(path)
    return artifacts


@lru_cache
def _load_location_features() -> dict[int, dict[str, float]]:
    conn = sqlite3.connect(DB_PATH)
    try:
        df = pd.read_sql(f"SELECT location_id, date, {', '.join(TARGETS)} FROM readings", conn)
    finally:
        conn.close()

    df = df.sort_values(["location_id", "date"])
    grouped = df.groupby("location_id")
    historical = grouped[TARGETS].mean()
    recent = grouped[TARGETS].apply(lambda g: g.tail(3).mean())

    return {
        int(loc_id): {
            **{f"historical_mean_{t}": float(historical.loc[loc_id, t]) for t in TARGETS},
            **{f"recent_mean_{t}": float(recent.loc[loc_id, t]) for t in TARGETS},
        }
        for loc_id in historical.index
    }


@lru_cache
def _load_location_metadata() -> dict[int, dict]:
    conn = sqlite3.connect(DB_PATH)
    try:
        locations_df = pd.read_sql("SELECT id, name FROM locations", conn)
        readings_df = pd.read_sql("SELECT location_id, date FROM readings", conn, parse_dates=["date"])
    finally:
        conn.close()

    last_reading_date = readings_df.groupby("location_id")["date"].max().dt.date
    names = locations_df.set_index("id")["name"]

    return {
        int(loc_id): {"name": names.loc[loc_id], "last_reading_date": last_reading_date.loc[loc_id]}
        for loc_id in last_reading_date.index
    }


def predict_all_consumption(target_date: date) -> ConsumptionPredictionResponse:
    artifacts = _load_artifacts()
    valid_location_ids = sorted(next(iter(artifacts.values()))["valid_location_ids"])
    location_metadata = _load_location_metadata()
    all_location_features = _load_location_features()

    predictions = []
    for location_id in valid_location_ids:
        days_since_previous_refill = (target_date - location_metadata[location_id]["last_reading_date"]).days

        features = pd.DataFrame(
            [
                {
                    "location_id": location_id,
                    "days_since_previous_refill": days_since_previous_refill,
                    "day_of_week": target_date.weekday(),
                    "month": target_date.month,
                    **all_location_features[location_id],
                }
            ]
        )

        target_predictions = {}
        for target, artifact in artifacts.items():
            estimate = max(0.0, float(artifact["pipeline"].predict(features)[0]))
            low = max(0.0, float(artifact["lower_pipeline"].predict(features)[0]))
            high = max(0.0, float(artifact["upper_pipeline"].predict(features)[0]))
            # Independently-fit quantile models have no monotonicity guarantee
            # between each other or the point estimate -- clamp so low <= estimate <= high.
            low, high = min(low, high, estimate), max(low, high, estimate)
            target_predictions[target] = PredictionInterval(estimate=estimate, low=low, high=high)

        predictions.append(
            LocationConsumptionPrediction(
                location_id=location_id,
                location_name=location_metadata[location_id]["name"],
                days_since_previous_refill=days_since_previous_refill,
                **target_predictions,
            )
        )

    return ConsumptionPredictionResponse(target_date=target_date, predictions=predictions)
