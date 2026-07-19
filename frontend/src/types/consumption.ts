export interface PredictionInterval {
  estimate: number
  low: number
  high: number
}

export interface RemainingStock {
  capacity: number
  remaining: PredictionInterval
  remaining_pct: PredictionInterval
}

export interface LocationConsumptionPrediction {
  location_id: number
  location_name: string
  lat: number
  lng: number
  days_since_previous_refill: number
  cup_units: PredictionInterval
  bottled_water: RemainingStock
  coffee_mix: RemainingStock
  chocolate_mix: RemainingStock
  cappuccino_mix: RemainingStock
}

export interface ConsumptionPredictionResponse {
  target_date: string
  predictions: LocationConsumptionPrediction[]
}
