import { ConsumptionList } from './components/ConsumptionList'
import { ReloadList } from './components/ReloadList'
import { RoutePlanner } from './components/RoutePlanner'
import { useConsumptionPredictions } from './hooks/useConsumptionPredictions'
import './App.css'

function App() {
  const consumptions = useConsumptionPredictions()

  return (
    <div className="app-layout">
      <aside className="app-layout-sidebar">
        <ConsumptionList
          loading={consumptions.loading}
          error={consumptions.error}
          hasFetched={consumptions.hasFetched}
          items={consumptions.available}
          targetDate={consumptions.targetDate}
          onTargetDateChange={consumptions.setTargetDate}
          onFetch={consumptions.fetchPredictions}
          onDropItem={consumptions.unmarkForReload}
        />
      </aside>
      <aside className="app-layout-reload">
        <ReloadList items={consumptions.toReload} onDropItem={consumptions.markForReload} />
      </aside>
      <main className="app-layout-main">
        <RoutePlanner locations={consumptions.toReload} />
      </main>
    </div>
  )
}

export default App
