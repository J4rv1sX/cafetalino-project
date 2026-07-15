from fastapi import APIRouter, HTTPException

from app.schemas.consumption import ConsumptionPredictionRequest, ConsumptionPredictionResponse
from app.services.consumption_predictor import predict_consumption

router = APIRouter(tags=["consumption"])


@router.post("/predict-consumption", response_model=ConsumptionPredictionResponse)
def predict_consumption_endpoint(request: ConsumptionPredictionRequest) -> ConsumptionPredictionResponse:
    try:
        return predict_consumption(request.location_id, request.days_since_previous_refill, request.target_date)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
