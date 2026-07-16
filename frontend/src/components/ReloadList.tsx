import { useState } from 'react'
import type { DragEvent } from 'react'
import { ConsumptionCard } from './ConsumptionCard'
import type { LocationConsumptionPrediction } from '../types/consumption'
import './ConsumptionList.css'

interface ReloadListProps {
  items: LocationConsumptionPrediction[]
  onDropItem: (locationId: number) => void
}

export function ReloadList({ items, onDropItem }: ReloadListProps) {
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
        <h1>Máquinas a recargar</h1>
        <p>
          {items.length === 0
            ? 'Arrastra aquí las máquinas que quieres recargar.'
            : `${items.length} máquina${items.length === 1 ? '' : 's'} seleccionada${items.length === 1 ? '' : 's'}.`}
        </p>
      </header>

      <div
        className={`prediction-cards-scroll prediction-cards-scroll--fill${isDragOver ? ' is-drag-over' : ''}`}
        onDragOver={handleDragOver}
        onDragLeave={() => setIsDragOver(false)}
        onDrop={handleDrop}
      >
        {items.length === 0 ? (
          <p className="prediction-cards-empty">Suelta aquí las máquinas que quieres recargar.</p>
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
