from datetime import date

from pydantic import BaseModel


class ConsumptionPredictionRequest(BaseModel):
    target_date: date


class PredictionInterval(BaseModel):
    estimate: float
    low: float
    high: float


class LocationConsumptionPrediction(BaseModel):
    location_id: int
    location_name: str
    lat: float
    lng: float
    days_since_previous_refill: int
    bottled_water_ml: PredictionInterval
    cup_units: PredictionInterval
    coffee_mix_g: PredictionInterval
    chocolate_mix_g: PredictionInterval
    cappuccino_mix_g: PredictionInterval


class ConsumptionPredictionResponse(BaseModel):
    target_date: date
    predictions: list[LocationConsumptionPrediction]
