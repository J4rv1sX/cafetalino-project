import type { ConsumptionPredictionResponse } from '../types/consumption'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

export async function fetchConsumptions(targetDate: string): Promise<ConsumptionPredictionResponse> {
  const response = await fetch(`${API_BASE_URL}/predict-consumption`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ target_date: targetDate }),
  })

  if (!response.ok) {
    const detail = await response.text()
    throw new Error(`No se pudieron obtener los consumos (${response.status}): ${detail}`)
  }

  return response.json()
}
