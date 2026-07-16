import { useCallback, useMemo, useState } from 'react'
import { fetchConsumptions } from '../api/consumption'
import type { LocationConsumptionPrediction } from '../types/consumption'

function todayIsoDate(): string {
  return new Date().toISOString().slice(0, 10)
}

export function useConsumptionPredictions() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [predictions, setPredictions] = useState<LocationConsumptionPrediction[] | null>(null)
  const [reloadIds, setReloadIds] = useState<number[]>([])

  const fetchPredictions = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const result = await fetchConsumptions(todayIsoDate())
      setPredictions(result.predictions)
      setReloadIds([])
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error desconocido al obtener los consumos.')
    } finally {
      setLoading(false)
    }
  }, [])

  const markForReload = useCallback((locationId: number) => {
    setReloadIds((prev) => (prev.includes(locationId) ? prev : [...prev, locationId]))
  }, [])

  const unmarkForReload = useCallback((locationId: number) => {
    setReloadIds((prev) => prev.filter((id) => id !== locationId))
  }, [])

  const available = useMemo(
    () =>
      (predictions ?? [])
        .filter((prediction) => !reloadIds.includes(prediction.location_id))
        .sort((a, b) => b.days_since_previous_refill - a.days_since_previous_refill),
    [predictions, reloadIds],
  )

  const toReload = useMemo(() => {
    const byId = new Map(predictions?.map((prediction) => [prediction.location_id, prediction]))
    return reloadIds
      .map((id) => byId.get(id))
      .filter((prediction): prediction is LocationConsumptionPrediction => prediction != null)
  }, [predictions, reloadIds])

  return {
    loading,
    error,
    hasFetched: predictions !== null,
    available,
    toReload,
    fetchPredictions,
    markForReload,
    unmarkForReload,
  }
}
