import { useEffect } from 'react'
import { useMap } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet-routing-machine'
import 'leaflet-routing-machine/dist/leaflet-routing-machine.css'

type Props = {
  from: [number, number]
  to: [number, number]
}

export default function RouteMap({ from, to }: Props) {
  const map = useMap()

  useEffect(() => {
    const routing = L.Routing.control({
      waypoints: [
        L.latLng(from[0], from[1]),
        L.latLng(to[0], to[1]),
      ],
      routeWhileDragging: false,
      show: true,
      addWaypoints: false,
      fitSelectedRoutes: true,
      lineOptions: {
        styles: [{ color: '#2563eb', weight: 5 }],
        extendToWaypoints: true,
        missingRouteTolerance: 10,
      },
    }).addTo(map)

    return () => {
      map.removeControl(routing)
    }
  }, [map, from, to])

  return null
}