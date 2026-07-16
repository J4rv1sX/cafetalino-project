import { ConsumptionList } from './components/ConsumptionList'
import { RoutePlanner } from './components/RoutePlanner'
import './App.css'

function App() {
  return (
    <div className="app-layout">
      <aside className="app-layout-sidebar">
        <ConsumptionList />
      </aside>
      <main className="app-layout-main">
        <RoutePlanner />
      </main>
    </div>
  )
}

export default App
