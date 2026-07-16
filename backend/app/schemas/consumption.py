from datetime import date

from pydantic import BaseModel


class ConsumptionPredictionRequest(BaseModel):
    location_id: int
    days_since_previous_refill: int
    target_date: date


class PredictionInterval(BaseModel):
    estimate: float
    low: float
    high: float


class ConsumptionPredictionResponse(BaseModel):
    location_id: int
    days_since_previous_refill: int
    target_date: date
    bottled_water_ml: PredictionInterval
    cup_units: PredictionInterval
    coffee_mix_g: PredictionInterval
    chocolate_mix_g: PredictionInterval
    cappuccino_mix_g: PredictionInterval
