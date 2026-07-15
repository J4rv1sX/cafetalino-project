from pydantic import BaseModel


class Location(BaseModel):
    nombre: str
    lat: float
    lng: float


class RouteOptimizeRequest(BaseModel):
    current_location: Location


class RouteStop(BaseModel):
    orden: int
    nombre: str
    lat: float
    lng: float


class RouteOptimizeResponse(BaseModel):
    route: list[RouteStop]
    total_duration_seconds: int
