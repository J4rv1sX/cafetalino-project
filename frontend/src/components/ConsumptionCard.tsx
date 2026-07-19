import type { DragEvent } from 'react'
import type { LocationConsumptionPrediction } from '../types/consumption'
import './ConsumptionCard.css'

const STOCK_CONFIG: Array<{
  key: keyof Pick<LocationConsumptionPrediction, 'bottled_water' | 'coffee_mix' | 'chocolate_mix' | 'cappuccino_mix'>
  label: string
  unit: string
  decimals: number
}> = [
  { key: 'bottled_water', label: 'Agua embotellada', unit: 'l', decimals: 1 },
  { key: 'coffee_mix', label: 'Mezcla de café', unit: 'g', decimals: 0 },
  { key: 'chocolate_mix', label: 'Mezcla de chocolate', unit: 'g', decimals: 0 },
  { key: 'cappuccino_mix', label: 'Mezcla de capuchino', unit: 'g', decimals: 0 },
]

function formatAmount(value: number, decimals = 0): string {
  return value.toLocaleString('es-BO', { minimumFractionDigits: decimals, maximumFractionDigits: decimals })
}

function formatPct(value: number): string {
  return `${Math.round(value)}%`
}

interface ConsumptionCardProps {
  prediction: LocationConsumptionPrediction
}

export function ConsumptionCard({ prediction }: ConsumptionCardProps) {
  const handleDragStart = (event: DragEvent<HTMLElement>) => {
    event.dataTransfer.setData('text/plain', String(prediction.location_id))
    event.dataTransfer.effectAllowed = 'move'
  }

  return (
    <article className="consumption-card" draggable onDragStart={handleDragStart}>
      <h2>{prediction.location_name}</h2>
      <p className="consumption-card-meta">Última recarga hace {prediction.days_since_previous_refill} días</p>
      <ul className="consumption-card-items">
        <li>
          <span className="consumption-card-label">Vasos</span>
          <span className="consumption-card-value">
            {formatAmount(prediction.cup_units.estimate)} u
            <span className="consumption-card-range">
              {' '}
              ({formatAmount(prediction.cup_units.low)}–{formatAmount(prediction.cup_units.high)} u)
            </span>
          </span>
        </li>
        {STOCK_CONFIG.map(({ key, label, unit, decimals }) => {
          const { remaining, remaining_pct } = prediction[key]
          return (
            <li key={key}>
              <span className="consumption-card-label">{label}</span>
              <span className="consumption-card-value">
                {formatAmount(remaining.estimate, decimals)} {unit} ({formatPct(remaining_pct.estimate)})
                <span className="consumption-card-range">
                  {' '}
                  ({formatAmount(remaining.low, decimals)}–{formatAmount(remaining.high, decimals)} {unit})
                </span>
              </span>
            </li>
          )
        })}
      </ul>
    </article>
  )
}
