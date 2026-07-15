import numpy as np
import requests

from app.schemas.routing import Location

DISTANCE_MATRIX_URL = "https://maps.googleapis.com/maps/api/distancematrix/json"


def get_distance_matrix(locations: list[Location], api_key: str) -> np.ndarray:
    """Fetch a driving-duration matrix (seconds) between all locations.

    Ported from rutas_cafetalino.ipynb's obtener_matriz_distancias. Note: the
    Google Distance Matrix API caps origins*destinations per request, so for
    n > ~25 this would need to be split into batched calls.
    """
    n = len(locations)
    matrix = np.zeros((n, n))
    coords = [f"{loc.lat},{loc.lng}" for loc in locations]

    params = {
        "origins": "|".join(coords),
        "destinations": "|".join(coords),
        "mode": "driving",
        "key": api_key,
    }

    response = requests.get(DISTANCE_MATRIX_URL, params=params)
    response.raise_for_status()
    data = response.json()

    for i in range(n):
        for j in range(n):
            element = data["rows"][i]["elements"][j]
            matrix[i, j] = (
                element["duration"]["value"] if element["status"] == "OK" else 999999
            )
    return matrix
