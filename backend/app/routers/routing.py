from fastapi import APIRouter

from app.core.config import get_google_maps_api_key
from app.data.machines import MACHINE_LOCATIONS
from app.schemas.routing import RouteOptimizeRequest, RouteOptimizeResponse, RouteStop
from app.services.distance_matrix import get_distance_matrix
from app.services.tsp_solver import solve_tsp, total_route_duration

router = APIRouter(tags=["routing"])


@router.post("/reload-route", response_model=RouteOptimizeResponse)
def optimize_route(request: RouteOptimizeRequest) -> RouteOptimizeResponse:
    locations = [request.current_location, *MACHINE_LOCATIONS]

    api_key = get_google_maps_api_key()
    matrix = get_distance_matrix(locations, api_key)
    route_indices = solve_tsp(matrix)

    return RouteOptimizeResponse(
        route=[
            RouteStop(
                orden=order,
                nombre=locations[idx].nombre,
                lat=locations[idx].lat,
                lng=locations[idx].lng,
            )
            for order, idx in enumerate(route_indices, start=1)
        ],
        total_duration_seconds=total_route_duration(matrix, route_indices),
    )
