export interface PredictionInterval {
  estimate: number
  low: number
  high: number
}

export interface LocationConsumptionPrediction {
  location_id: number
  location_name: string
  lat: number
  lng: number
  days_since_previous_refill: number
  bottled_water_ml: PredictionInterval
  cup_units: PredictionInterval
  coffee_mix_g: PredictionInterval
  chocolate_mix_g: PredictionInterval
  cappuccino_mix_g: PredictionInterval
}

export interface ConsumptionPredictionResponse {
  target_date: string
  predictions: LocationConsumptionPrediction[]
}
