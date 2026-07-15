from datetime import date

from pydantic import BaseModel


class ConsumptionPredictionRequest(BaseModel):
    location_id: int
    days_since_previous_refill: int
    target_date: date


class ConsumptionPredictionResponse(BaseModel):
    location_id: int
    days_since_previous_refill: int
    target_date: date
    bottled_water_ml: float
    cup_units: float
    coffee_mix_g: float
    chocolate_mix_g: float
    cappuccino_mix_g: float
