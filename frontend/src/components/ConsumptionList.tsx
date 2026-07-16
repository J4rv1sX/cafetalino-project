import { useCallback, useState } from 'react'
import { fetchConsumptions } from '../api/consumption'
import type { ConsumptionPredictionResponse, LocationConsumptionPrediction } from '../types/consumption'
import './ConsumptionList.css'

const TARGET_CONFIG: Array<{
  key: keyof Pick<
    LocationConsumptionPrediction,
    'bottled_water_ml' | 'cup_units' | 'coffee_mix_g' | 'chocolate_mix_g' | 'cappuccino_mix_g'
  >
  label: string
  unit: string
}> = [
  { key: 'bottled_water_ml', label: 'Agua embotellada', unit: 'ml' },
  { key: 'cup_units', label: 'Vasos', unit: 'u' },
  { key: 'coffee_mix_g', label: 'Mezcla de café', unit: 'g' },
  { key: 'chocolate_mix_g', label: 'Mezcla de chocolate', unit: 'g' },
  { key: 'cappuccino_mix_g', label: 'Mezcla de capuchino', unit: 'g' },
]

function todayIsoDate(): string {
  return new Date().toISOString().slice(0, 10)
}

function formatAmount(value: number): string {
  return Math.round(value).toLocaleString('es-BO')
}

export function ConsumptionList() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<ConsumptionPredictionResponse | null>(null)

  const handleFetch = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      setResult(await fetchConsumptions(todayIsoDate()))
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error desconocido al obtener los consumos.')
    } finally {
      setLoading(false)
    }
  }, [])

  return (
    <section className="consumption-list">
      <header className="consumption-list-header">
        <h1>Consumo de máquinas</h1>
        <p>Consulta el consumo estimado de cada máquina para hoy.</p>
      </header>

      <button type="button" onClick={handleFetch} disabled={loading}>
        {loading ? 'Cargando…' : 'Ver consumos'}
      </button>

      {error && <p className="consumption-list-error">{error}</p>}

      {result && (
        <div className="consumption-cards-scroll">
          <div className="consumption-cards">
            {[...result.predictions]
              .sort((a, b) => b.days_since_previous_refill - a.days_since_previous_refill)
              .map((prediction) => (
              <article key={prediction.location_id} className="consumption-card">
                <h2>{prediction.location_name}</h2>
                <p className="consumption-card-meta">
                  Última recarga hace {prediction.days_since_previous_refill} días
                </p>
                <ul className="consumption-card-items">
                  {TARGET_CONFIG.map(({ key, label, unit }) => {
                    const { estimate, low, high } = prediction[key]
                    return (
                      <li key={key}>
                        <span className="consumption-card-label">{label}</span>
                        <span className="consumption-card-value">
                          {formatAmount(estimate)} {unit}
                          <span className="consumption-card-range">
                            {' '}
                            ({formatAmount(low)}–{formatAmount(high)} {unit})
                          </span>
                        </span>
                      </li>
                    )
                  })}
                </ul>
              </article>
            ))}
          </div>
        </div>
      )}
    </section>
  )
}
