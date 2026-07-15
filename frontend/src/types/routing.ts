export interface Location {
  name: string
  lat: number
  lng: number
}

export interface RouteStop extends Location {
  order: number
}

export interface RouteOptimizeResponse {
  route: RouteStop[]
  total_duration_seconds: number
}
