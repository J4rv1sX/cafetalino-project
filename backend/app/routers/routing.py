from fastapi import APIRouter

from app.core.config import get_google_maps_api_key
from app.schemas.routing import RouteOptimizeRequest, RouteOptimizeResponse, RouteStop
from app.services.distance_matrix import get_distance_matrix
from app.services.tsp_solver import solve_tsp, total_route_duration

router = APIRouter(tags=["routing"])

RELOAD_SERVICE_SECONDS = 25 * 60


@router.post("/reload-route", response_model=RouteOptimizeResponse)
def optimize_route(request: RouteOptimizeRequest) -> RouteOptimizeResponse:
    locations = request.locations

    api_key = get_google_maps_api_key()
    matrix = get_distance_matrix(locations, api_key)
    route_indices = solve_tsp(matrix)

    # locations[0] is the caller's current position, not a machine to reload,
    # so it doesn't get service time -- every other location does.
    machine_count = len(locations) - 1

    return RouteOptimizeResponse(
        route=[
            RouteStop(
                order=order,
                name=locations[idx].name,
                lat=locations[idx].lat,
                lng=locations[idx].lng,
            )
            for order, idx in enumerate(route_indices, start=1)
        ],
        total_duration_seconds=total_route_duration(matrix, route_indices) + machine_count * RELOAD_SERVICE_SECONDS,
    )
