import { useState } from 'react'
import type { DragEvent } from 'react'
import { ConsumptionCard } from './ConsumptionCard'
import type { LocationConsumptionPrediction } from '../types/consumption'
import './ConsumptionList.css'

interface ConsumptionListProps {
  loading: boolean
  error: string | null
  hasFetched: boolean
  items: LocationConsumptionPrediction[]
  targetDate: string
  onTargetDateChange: (targetDate: string) => void
  onFetch: () => void
  onDropItem: (locationId: number) => void
}

export function ConsumptionList({
  loading,
  error,
  hasFetched,
  items,
  targetDate,
  onTargetDateChange,
  onFetch,
  onDropItem,
}: ConsumptionListProps) {
  const [isDragOver, setIsDragOver] = useState(false)

  const handleDragOver = (event: DragEvent<HTMLDivElement>) => {
    event.preventDefault()
    setIsDragOver(true)
  }

  const handleDrop = (event: DragEvent<HTMLDivElement>) => {
    event.preventDefault()
    setIsDragOver(false)
    const locationId = Number(event.dataTransfer.getData('text/plain'))
    if (!Number.isNaN(locationId)) onDropItem(locationId)
  }

  return (
    <section className="prediction-column prediction-column--fill">
      <header className="prediction-column-header">
        <h1>Consumo de máquinas</h1>
        <p>Consulta el consumo estimado de cada máquina para la fecha seleccionada.</p>
      </header>

      <div className="prediction-column-controls">
        <input
          type="date"
          value={targetDate}
          onChange={(event) => onTargetDateChange(event.target.value)}
          disabled={loading}
        />
        <button type="button" onClick={onFetch} disabled={loading}>
          {loading ? 'Cargando…' : 'Ver consumos'}
        </button>
      </div>

      {error && <p className="prediction-column-error">{error}</p>}

      <div
        className={`prediction-cards-scroll prediction-cards-scroll--fill${isDragOver ? ' is-drag-over' : ''}`}
        onDragOver={handleDragOver}
        onDragLeave={() => setIsDragOver(false)}
        onDrop={handleDrop}
      >
        {!hasFetched ? null : items.length === 0 ? (
          <p className="prediction-cards-empty">Todas las máquinas están en la lista de recarga.</p>
        ) : (
          <div className="prediction-cards">
            {items.map((prediction) => (
              <ConsumptionCard key={prediction.location_id} prediction={prediction} />
            ))}
          </div>
        )}
      </div>
    </section>
  )
}
