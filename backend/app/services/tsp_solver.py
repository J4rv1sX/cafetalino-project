import numpy as np
from ortools.constraint_solver import pywrapcp, routing_enums_pb2


def solve_tsp(matrix: np.ndarray) -> list[int]:
    """Solve a single-vehicle round trip starting/ending at index 0.

    Ported from rutas_cafetalino.ipynb's resolver_tsp. Returns the visiting
    order as a list of indices into `matrix`, starting and ending at 0.
    """
    manager = pywrapcp.RoutingIndexManager(len(matrix), 1, 0)
    routing = pywrapcp.RoutingModel(manager)

    def distance_callback(from_index, to_index):
        return int(matrix[manager.IndexToNode(from_index)][manager.IndexToNode(to_index)])

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    search_params = pywrapcp.DefaultRoutingSearchParameters()
    search_params.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )

    solution = routing.SolveWithParameters(search_params)
    if solution is None:
        raise RuntimeError("No solution found for the given distance matrix.")

    index = routing.Start(0)
    route = []
    while not routing.IsEnd(index):
        route.append(manager.IndexToNode(index))
        index = solution.Value(routing.NextVar(index))
    route.append(manager.IndexToNode(index))
    return route


def total_route_duration(matrix: np.ndarray, route: list[int]) -> int:
    """Sum the leg durations (seconds) along a solved route."""
    return int(sum(matrix[route[i]][route[i + 1]] for i in range(len(route) - 1)))
