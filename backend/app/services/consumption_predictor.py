import sqlite3
from datetime import date
from functools import lru_cache
from pathlib import Path

import joblib
import pandas as pd

from app.schemas.consumption import ConsumptionPredictionResponse, PredictionInterval

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


def predict_consumption(
    location_id: int, days_since_previous_refill: int, target_date: date
) -> ConsumptionPredictionResponse:
    artifacts = _load_artifacts()
    valid_location_ids = set(next(iter(artifacts.values()))["valid_location_ids"])
    if location_id not in valid_location_ids:
        raise ValueError(f"Unknown location_id: {location_id}")

    location_features = _load_location_features()[location_id]

    features = pd.DataFrame(
        [
            {
                "location_id": location_id,
                "days_since_previous_refill": days_since_previous_refill,
                "day_of_week": target_date.weekday(),
                "month": target_date.month,
                **location_features,
            }
        ]
    )

    predictions = {}
    for target, artifact in artifacts.items():
        estimate = max(0.0, float(artifact["pipeline"].predict(features)[0]))
        low = max(0.0, float(artifact["lower_pipeline"].predict(features)[0]))
        high = max(0.0, float(artifact["upper_pipeline"].predict(features)[0]))
        # Independently-fit quantile models have no monotonicity guarantee
        # between each other or the point estimate -- clamp so low <= estimate <= high.
        low, high = min(low, high, estimate), max(low, high, estimate)
        predictions[target] = PredictionInterval(estimate=estimate, low=low, high=high)

    return ConsumptionPredictionResponse(
        location_id=location_id,
        days_since_previous_refill=days_since_previous_refill,
        target_date=target_date,
        **predictions,
    )
