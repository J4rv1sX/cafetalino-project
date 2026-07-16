from fastapi import APIRouter

from app.schemas.consumption import ConsumptionPredictionRequest, ConsumptionPredictionResponse
from app.services.consumption_predictor import predict_all_consumption

router = APIRouter(tags=["consumption"])


@router.post("/predict-consumption", response_model=ConsumptionPredictionResponse)
def predict_consumption_endpoint(request: ConsumptionPredictionRequest) -> ConsumptionPredictionResponse:
    return predict_all_consumption(request.target_date)
