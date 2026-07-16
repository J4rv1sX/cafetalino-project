import type { DragEvent } from 'react'
import type { LocationConsumptionPrediction } from '../types/consumption'
import './ConsumptionCard.css'

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

function formatAmount(value: number): string {
  return Math.round(value).toLocaleString('es-BO')
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
  )
}
