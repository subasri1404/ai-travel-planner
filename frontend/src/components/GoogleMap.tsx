import {useEffect, useState } from 'react'
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import 'leaflet-routing-machine'
import 'leaflet-routing-machine/dist/leaflet-routing-machine.css'

type Place = {
  name: string
  lat: number
  lon: number
}
function RouteControl({ from, to }: { from: Place; to: Place }) {
  const map = useMap()

  useEffect(() => {
    const control = L.Routing.control({
      waypoints: [
        L.latLng(from.lat, from.lon),
        L.latLng(to.lat, to.lon),
      ],
      router: L.Routing.osrmv1({
        serviceUrl: 'https://router.project-osrm.org/route/v1',
      }),
      addWaypoints: false,
      routeWhileDragging: false,
      show: true,
      fitSelectedRoutes: true,
    }).addTo(map)

    control.on('routingerror', (event) => {
      console.error('Routing error:', event.error)
    })

    return () => {
      map.removeControl(control)
    }
  }, [map, from, to])

  return null
}
async function searchPlace(query: string): Promise<Place> {
  const url =
    `https://nominatim.openstreetmap.org/search?format=jsonv2&limit=5&countrycodes=in&q=${encodeURIComponent(query)}`

  const response = await fetch(url)

  if (!response.ok) {
    throw new Error('Place search service unavailable. Try again.')
  }
  console.log('Searching place:',url)
  const results = await response.json()

  if (!results.length) {
    throw new Error(
      `Place not found: ${query}. Try adding the city and Tamil Nadu.`
    )
  }

  const result = results[0]

  return {
    name: result.display_name,
    lat: Number(result.lat),
    lon: Number(result.lon),
  }
}


export default function GoogleMap({ destination = '' }: { destination?: string }) {
  const [fromText, setFromText] = useState('')
  const [toText, setToText] = useState(destination)
  useEffect(() => {
    setToText(destination)
  }, [destination])
  const [from, setFrom] = useState<Place | null>(null)
  const [to, setTo] = useState<Place | null>(null)
  const [error, setError] = useState('')
  const [searching, setSearching] = useState(false)

  async function handleSearch() {
    if (!fromText.trim() || !toText.trim()) {
      setError('Please enter both starting place and destination.')
      return
    }

    setSearching(true)
    setError('')
    setFrom(null)
    setTo(null)

    try {
      const [start, end] = await Promise.all([
        searchPlace(fromText),
        searchPlace(toText),
      ])
      setFrom(start)
      setTo(end)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Search failed.')
    } finally {
      setSearching(false)
    }
  }
  useEffect(() => {
  if (!fromText.trim() || !toText.trim()) return

  const timer = setTimeout(() => {
    handleSearch()
  }, 1000)

  return () => clearTimeout(timer)
}, [fromText, toText])
  const initial: [number, number] = [11.0168, 76.9558]

  return (
    <div>
      <div style={{ display: 'grid', gap: 10, marginBottom: 12 }}>
        <input
          value={fromText}
          onChange={(e) => setFromText(e.target.value)}
          placeholder="Starting location (e.g. Salem)"
          aria-label="Starting location"
        />
        <input
          value={toText}
          onChange={(e) => setToText(e.target.value)}
          placeholder="Destination (e.g. Meenakshi Amman Temple, Madurai)"
          aria-label="Destination"
        />
        <button onClick={handleSearch} disabled={searching}>
          {searching ? 'Searching...' : 'Search Route'}
        </button>
        {error && <p style={{ color: 'crimson' }}>{error}</p>}
      </div>

      <MapContainer
        center={initial}
        zoom={6}
        style={{ height: 400, width: '100%', borderRadius: 12 }}
      >
        <TileLayer
          attribution='&copy; OpenStreetMap contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {from && (
          <Marker position={[from.lat, from.lon]}>
            <Popup>Start: {from.name}</Popup>
          </Marker>
        )}

        {to && (
          <Marker position={[to.lat, to.lon]}>
            <Popup>Destination: {to.name}</Popup>
          </Marker>
        )}

        {from && to && <RouteControl from={from} to={to} />}
      </MapContainer>
    </div>
  )
}