import { useEffect, useState } from 'react'

export default function MapLoader({
  destination,
}: {
  destination: string
}) {
  const [MapComponent, setMapComponent] =
    useState<React.ComponentType<{ destination?: string }> | null>(null)

  useEffect(() => {
    import('./GoogleMap').then((module) => {
      setMapComponent(() => module.default)
    })
  }, [])

  if (!MapComponent) {
    return <p>Loading map...</p>
  }

  return <MapComponent destination={destination} />
}