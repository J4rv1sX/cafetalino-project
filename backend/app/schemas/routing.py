from pydantic import BaseModel


class Location(BaseModel):
    name: str
    lat: float
    lng: float


class RouteOptimizeRequest(BaseModel):
    locations: list[Location]


class RouteStop(BaseModel):
    order: int
    name: str
    lat: float
    lng: float


class RouteOptimizeResponse(BaseModel):
    route: list[RouteStop]
    total_duration_seconds: int
