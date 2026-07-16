import { useCallback, useEffect, useState } from 'react'
import { DirectionsRenderer, GoogleMap, MarkerF, useJsApiLoader } from '@react-google-maps/api'
import { optimizeRoute } from '../api/routing'
import type { LocationConsumptionPrediction } from '../types/consumption'
import type { RouteOptimizeResponse } from '../types/routing'
import './RoutePlanner.css'

const SUCRE_CENTER = { lat: -19.0333, lng: -65.2627 }
const MAP_CONTAINER_STYLE = { width: '100%', height: '480px' }

function formatDuration(seconds: number): string {
  const minutes = Math.round(seconds / 60)
  if (minutes < 60) return `${minutes} min`
  return `${Math.floor(minutes / 60)} h ${minutes % 60} min`
}

interface RoutePlannerProps {
  locations: LocationConsumptionPrediction[]
}

export function RoutePlanner({ locations }: RoutePlannerProps) {
  const { isLoaded, loadError } = useJsApiLoader({
    id: 'google-map-script',
    googleMapsApiKey: import.meta.env.VITE_GOOGLE_MAPS_API_KEY,
  })

  const [markerPos, setMarkerPos] = useState(SUCRE_CENTER)
  const [locating, setLocating] = useState(true)
  const [loadingRoute, setLoadingRoute] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [routeResult, setRouteResult] = useState<RouteOptimizeResponse | null>(null)
  const [directions, setDirections] = useState<google.maps.DirectionsResult | null>(null)

  useEffect(() => {
    if (!navigator.geolocation) {
      setLocating(false)
      return
    }
    navigator.geolocation.getCurrentPosition(
      (position) => {
        setMarkerPos({ lat: position.coords.latitude, lng: position.coords.longitude })
        setLocating(false)
      },
      () => setLocating(false),
      { enableHighAccuracy: true, timeout: 8000 },
    )
  }, [])

  const handleMarkerDragEnd = useCallback((event: google.maps.MapMouseEvent) => {
    if (!event.latLng) return
    setMarkerPos({ lat: event.latLng.lat(), lng: event.latLng.lng() })
  }, [])

  const handleOptimize = useCallback(async () => {
    setLoadingRoute(true)
    setError(null)
    setDirections(null)

    try {
      const result = await optimizeRoute([
        { name: 'Mi ubicación', lat: markerPos.lat, lng: markerPos.lng },
        ...locations.map((item) => ({ name: item.location_name, lat: item.lat, lng: item.lng })),
      ])
      setRouteResult(result)

      if (result.route.length > 1) {
        const [start, ...rest] = result.route
        const end = rest[rest.length - 1]
        const waypoints = rest.slice(0, -1).map((stop) => ({
          location: { lat: stop.lat, lng: stop.lng },
          stopover: true,
        }))

        const directionsService = new google.maps.DirectionsService()
        directionsService.route(
          {
            origin: { lat: start.lat, lng: start.lng },
            destination: { lat: end.lat, lng: end.lng },
            waypoints,
            optimizeWaypoints: false,
            travelMode: google.maps.TravelMode.DRIVING,
          },
          (result, status) => {
            if (status === google.maps.DirectionsStatus.OK && result) {
              setDirections(result)
            } else {
              setError(`No se pudo dibujar la ruta en el mapa (${status}).`)
            }
          },
        )
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error desconocido al calcular la ruta.')
    } finally {
      setLoadingRoute(false)
    }
  }, [markerPos, locations])

  if (!import.meta.env.VITE_GOOGLE_MAPS_API_KEY) {
    return (
      <section className="route-planner">
        <p className="route-planner-error">
          Falta configurar <code>VITE_GOOGLE_MAPS_API_KEY</code> en <code>frontend/.env.local</code>.
        </p>
      </section>
    )
  }

  if (loadError) {
    return (
      <section className="route-planner">
        <p className="route-planner-error">No se pudo cargar Google Maps: {loadError.message}</p>
      </section>
    )
  }

  return (
    <section className="route-planner">
      <header className="route-planner-header">
        <h1>Ruta de recarga</h1>
        <p>
          {locating
            ? 'Detectando tu ubicación actual…'
            : 'Ajusta el marcador si es necesario y calcula la ruta de recarga.'}
        </p>
      </header>

      <div className="route-planner-body">
        <div className="route-planner-map">
          {isLoaded ? (
            <GoogleMap mapContainerStyle={MAP_CONTAINER_STYLE} center={markerPos} zoom={13}>
              <MarkerF position={markerPos} draggable onDragEnd={handleMarkerDragEnd} label="Tú" />
              {directions && <DirectionsRenderer directions={directions} />}
            </GoogleMap>
          ) : (
            <div className="route-planner-map-placeholder">Cargando mapa…</div>
          )}
        </div>

        <aside className="route-planner-sidebar">
          <button
            type="button"
            onClick={handleOptimize}
            disabled={loadingRoute || !isLoaded || locations.length === 0}
          >
            {loadingRoute ? 'Calculando…' : 'Calcular ruta de recarga'}
          </button>

          {locations.length === 0 && (
            <p className="route-planner-hint">Agrega máquinas a la lista de recarga antes de calcular la ruta.</p>
          )}

          {error && <p className="route-planner-error">{error}</p>}

          {routeResult && (
            <div className="route-planner-result">
              <p className="route-planner-total">
                Duración total: <strong>{formatDuration(routeResult.total_duration_seconds)}</strong>
              </p>
              <ol className="route-planner-stops">
                {routeResult.route.map((stop, index) => (
                  <li key={`${stop.order}-${index}`}>{stop.name}</li>
                ))}
              </ol>
            </div>
          )}
        </aside>
      </div>
    </section>
  )
}
