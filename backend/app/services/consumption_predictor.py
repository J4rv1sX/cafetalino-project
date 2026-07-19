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
    RemainingStock,
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
# Maps each capacity-bound target to its response field name, the location
# metadata key holding its capacity, and the factor to scale the target's
# consumption unit into the capacity's unit (water is predicted in ml but
# reported in liters; mix targets and capacity are both already in grams).
CAPACITY_TARGETS = {
    "bottled_water_ml": ("bottled_water", "water_capacity_l", 0.001),
    "coffee_mix_g": ("coffee_mix", "mix_capacity_g", 1.0),
    "chocolate_mix_g": ("chocolate_mix", "mix_capacity_g", 1.0),
    "cappuccino_mix_g": ("cappuccino_mix", "mix_capacity_g", 1.0),
}
# Matches RATE_EPS in scripts/train_consumption.py -- must stay in sync so
# inference-time rate features are computed the same way as training-time ones.
RATE_EPS = 1e-6


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
        df = pd.read_sql(
            f"SELECT location_id, date, days_since_previous_refill, {', '.join(TARGETS)} FROM readings", conn
        )
    finally:
        conn.close()

    df = df.sort_values(["location_id", "date"])
    grouped = df.groupby("location_id")
    historical = grouped[TARGETS].mean()
    recent = grouped[TARGETS].apply(lambda g: g.tail(3).mean())
    historical_days = grouped["days_since_previous_refill"].mean()
    recent_days = grouped["days_since_previous_refill"].apply(lambda g: g.tail(3).mean())

    return {
        int(loc_id): {
            **{f"historical_mean_{t}": float(historical.loc[loc_id, t]) for t in TARGETS},
            **{f"recent_mean_{t}": float(recent.loc[loc_id, t]) for t in TARGETS},
            **{
                f"historical_rate_{t}": float(historical.loc[loc_id, t] / (historical_days.loc[loc_id] + RATE_EPS))
                for t in TARGETS
            },
            **{
                f"recent_rate_{t}": float(recent.loc[loc_id, t] / (recent_days.loc[loc_id] + RATE_EPS))
                for t in TARGETS
            },
        }
        for loc_id in historical.index
    }


@lru_cache
def _load_location_metadata() -> dict[int, dict]:
    conn = sqlite3.connect(DB_PATH)
    try:
        locations_df = pd.read_sql(
            "SELECT id, name, lat, lng, water_capacity, mix_capacity FROM locations", conn
        )
        readings_df = pd.read_sql("SELECT location_id, date FROM readings", conn, parse_dates=["date"])
    finally:
        conn.close()

    last_reading_date = readings_df.groupby("location_id")["date"].max().dt.date
    locations_df = locations_df.set_index("id")

    return {
        int(loc_id): {
            "name": locations_df.loc[loc_id, "name"],
            "lat": float(locations_df.loc[loc_id, "lat"]),
            "lng": float(locations_df.loc[loc_id, "lng"]),
            "water_capacity_l": float(locations_df.loc[loc_id, "water_capacity"]),
            "mix_capacity_g": float(locations_df.loc[loc_id, "mix_capacity"]),
            "last_reading_date": last_reading_date.loc[loc_id],
        }
        for loc_id in last_reading_date.index
    }


def _remaining_stock(consumption: PredictionInterval, capacity: float, unit_scale: float = 1.0) -> RemainingStock:
    def clamp(value: float) -> float:
        return min(capacity, max(0.0, value))

    # Consumption low <= estimate <= high, so capacity - consumption keeps
    # that ordering reversed: remaining_low pairs with consumption_high.
    remaining_low = clamp(capacity - consumption.high * unit_scale)
    remaining_estimate = clamp(capacity - consumption.estimate * unit_scale)
    remaining_high = clamp(capacity - consumption.low * unit_scale)

    return RemainingStock(
        capacity=capacity,
        remaining=PredictionInterval(estimate=remaining_estimate, low=remaining_low, high=remaining_high),
        remaining_pct=PredictionInterval(
            estimate=remaining_estimate / capacity * 100,
            low=remaining_low / capacity * 100,
            high=remaining_high / capacity * 100,
        ),
    )


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

        remaining_stocks = {
            field_name: _remaining_stock(
                target_predictions[target], location_metadata[location_id][capacity_key], unit_scale
            )
            for target, (field_name, capacity_key, unit_scale) in CAPACITY_TARGETS.items()
        }

        predictions.append(
            LocationConsumptionPrediction(
                location_id=location_id,
                location_name=location_metadata[location_id]["name"],
                lat=location_metadata[location_id]["lat"],
                lng=location_metadata[location_id]["lng"],
                days_since_previous_refill=days_since_previous_refill,
                cup_units=target_predictions["cup_units"],
                **remaining_stocks,
            )
        )

    return ConsumptionPredictionResponse(target_date=target_date, predictions=predictions)
