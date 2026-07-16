import type { Location, RouteOptimizeResponse } from '../types/routing'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

export async function optimizeRoute(locations: Location[]): Promise<RouteOptimizeResponse> {
  const response = await fetch(`${API_BASE_URL}/reload-route`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ locations }),
  })

  if (!response.ok) {
    const detail = await response.text()
    throw new Error(`No se pudo calcular la ruta (${response.status}): ${detail}`)
  }

  return response.json()
}
