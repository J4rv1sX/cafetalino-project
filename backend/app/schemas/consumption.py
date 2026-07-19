from datetime import date

from pydantic import BaseModel


class ConsumptionPredictionRequest(BaseModel):
    target_date: date


class PredictionInterval(BaseModel):
    estimate: float
    low: float
    high: float


class RemainingStock(BaseModel):
    capacity: float
    remaining: PredictionInterval
    remaining_pct: PredictionInterval


class LocationConsumptionPrediction(BaseModel):
    location_id: int
    location_name: str
    lat: float
    lng: float
    days_since_previous_refill: int
    cup_units: PredictionInterval
    bottled_water: RemainingStock
    coffee_mix: RemainingStock
    chocolate_mix: RemainingStock
    cappuccino_mix: RemainingStock


class ConsumptionPredictionResponse(BaseModel):
    target_date: date
    predictions: list[LocationConsumptionPrediction]
