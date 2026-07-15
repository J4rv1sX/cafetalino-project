import sqlite3
from datetime import date
from functools import lru_cache
from pathlib import Path

import joblib
import pandas as pd

from app.schemas.consumption import ConsumptionPredictionResponse

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
def _load_location_history_means() -> dict[int, dict[str, float]]:
    conn = sqlite3.connect(DB_PATH)
    try:
        query = (
            f"SELECT location_id, {', '.join(f'AVG({t}) AS {t}' for t in TARGETS)} "
            "FROM readings GROUP BY location_id"
        )
        df = pd.read_sql(query, conn)
    finally:
        conn.close()
    return {int(row.location_id): {t: float(getattr(row, t)) for t in TARGETS} for row in df.itertuples()}


def predict_consumption(
    location_id: int, days_since_previous_refill: int, target_date: date
) -> ConsumptionPredictionResponse:
    artifacts = _load_artifacts()
    valid_location_ids = set(next(iter(artifacts.values()))["valid_location_ids"])
    if location_id not in valid_location_ids:
        raise ValueError(f"Unknown location_id: {location_id}")

    history_means = _load_location_history_means()[location_id]

    features = pd.DataFrame(
        [
            {
                "location_id": location_id,
                "days_since_previous_refill": days_since_previous_refill,
                "day_of_week": target_date.weekday(),
                "month": target_date.month,
                **{f"historical_mean_{t}": history_means[t] for t in TARGETS},
            }
        ]
    )

    predictions = {
        target: max(0.0, float(artifact["pipeline"].predict(features)[0]))
        for target, artifact in artifacts.items()
    }

    return ConsumptionPredictionResponse(
        location_id=location_id,
        days_since_previous_refill=days_since_previous_refill,
        target_date=target_date,
        **predictions,
    )
