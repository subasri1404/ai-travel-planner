import { createFileRoute } from '@tanstack/react-router'
import { useCallback, useEffect, useRef, useState } from 'react'
import MapLoader from '../components/MapLoader'
import {
  ApiError,
  clearAccessToken,
  deleteTrip,
  generateItinerary,
  getAccessToken,
  getTrips,
} from '../services/travelapi'
import type { ItineraryResponse, SavedTrip } from '../services/travelapi'
import Login from '../Login'
import Signup from '../Signup'

export const Route = createFileRoute('/')({
  component: Home,
})

function Home() {
  const [isLoggedIn, setIsLoggedIn] = useState(false)
  const [showSignup, setShowSignup] = useState(false)
  const [destination, setDestination] = useState('')
  const [budget, setBudget] = useState('')
  const [duration, setDuration] = useState('1')
  const [interests, setInterests] = useState('')
  const [travelers, setTravelers] = useState('1')
  const [itinerary, setItinerary] = useState<ItineraryResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [savedTrips, setSavedTrips] = useState<SavedTrip[]>([])
  const [savedTripsError, setSavedTripsError] = useState('')
  const [savedTripsLoading, setSavedTripsLoading] = useState(false)
  const [tripsRefreshKey, setTripsRefreshKey] = useState(0)
  const [loginNotice, setLoginNotice] = useState('')
  const generationInProgress = useRef(false)

  const invalidateSession = useCallback(() => {
    clearAccessToken()
    setIsLoggedIn(false)
    setLoginNotice(
      'Your saved session is no longer valid. Please log in again.',
    )
  }, [])

  useEffect(() => {
    if (getAccessToken()) {
      setIsLoggedIn(true)
    }
  }, [])

  useEffect(() => {
    if (!isLoggedIn) {
      setSavedTrips([])
      return
    }

    const token = getAccessToken()
    if (!token) {
      setIsLoggedIn(false)
      return
    }

    let active = true
    setSavedTripsLoading(true)
    setSavedTripsError('')

    getTrips(token)
      .then(({ trips }) => {
        if (active) {
          setSavedTrips(trips)
        }
      })
      .catch((err: unknown) => {
        if (!active) return
        if (err instanceof ApiError && err.status === 401) {
          invalidateSession()
          return
        }
        setSavedTripsError(
          err instanceof Error ? err.message : 'Unable to load saved trips.',
        )
      })
      .finally(() => {
        if (active) {
          setSavedTripsLoading(false)
        }
      })

    return () => {
      active = false
    }
  }, [invalidateSession, isLoggedIn, tripsRefreshKey])

  const handleGenerate = async () => {
    if (generationInProgress.current || loading) return

    if (!destination.trim() || !budget || !duration) {
      setError('Please enter destination, budget, and trip duration.')
      return
    }
    if (!budget || Number(budget) <= 0 || !Number.isFinite(Number(budget))) {
      setError('Please enter a valid budget greater than 0.')
      return
    }

    if (
      !duration ||
      !Number.isInteger(Number(duration)) ||
      Number(duration) <= 0 ||
      Number(duration) > 30
    ) {
      setError('Please enter a trip duration between 1 and 30 days.')
      return
    }

    if (
      !travelers ||
      !Number.isInteger(Number(travelers)) ||
      Number(travelers) <= 0 ||
      Number(travelers) > 100
    ) {
      setError('Please enter between 1 and 100 travelers.')
      return
    }
    if (!interests || !interests.trim()) {
      setError('Please select your travel interests.')
      return
    }

    generationInProgress.current = true
    setLoading(true)
    setError('')

    try {
      const token = getAccessToken()
      if (!token) {
        setIsLoggedIn(false)
        throw new Error('Please log in again to generate an itinerary.')
      }

      const result = await generateItinerary(
        {
          destination: destination.trim(),
          days: Number(duration),
          budget: Number(budget),
          travelers: Number(travelers),
          places: [],
          activities: interests ? [interests] : [],
        },
        token,
        crypto.randomUUID(),
      )

      setItinerary(result)
      setTripsRefreshKey((key) => key + 1)
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) {
        invalidateSession()
        return
      }
      setError(err instanceof Error ? err.message : 'Something went wrong')
    } finally {
      generationInProgress.current = false
      setLoading(false)
    }
  }

  const handleDeleteTrip = async (tripId: number) => {
    const token = getAccessToken()
    if (!token) {
      setIsLoggedIn(false)
      return
    }

    setSavedTripsError('')
    try {
      await deleteTrip(tripId, token)
      setSavedTrips((trips) => trips.filter((trip) => trip.id !== tripId))
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) {
        invalidateSession()
        return
      }
      setSavedTripsError(
        err instanceof Error ? err.message : 'Unable to delete saved trip.',
      )
    }
  }

  if (!isLoggedIn) {
    if (showSignup) {
      return (
        <Signup
          onSignup={() => {
            setShowSignup(false)
            setIsLoggedIn(false)
          }}
          onBackToLogin={() => setShowSignup(false)}
        />
      )
    }

    return (
      <Login
        notice={loginNotice}
        onLogin={() => {
          setLoginNotice('')
          setIsLoggedIn(true)
        }}
        onShowSignup={() => setShowSignup(true)}
      />
    )
  }

  return (
    <div
      style={{
        minHeight: '100vh',
        background: '#f5f7fa',
        padding: '40px 20px',
        fontFamily: 'Arial, sans-serif',
      }}
    >
      <div
        style={{
          maxWidth: '900px',
          margin: '0 auto',
          background: 'white',
          padding: '40px',
          borderRadius: '20px',
          boxShadow: '0 8px 30px rgba(0,0,0,0.08)',
        }}
      >
        <button
          onClick={() => {
            clearAccessToken()
            setIsLoggedIn(false)
          }}
          style={{
            padding: '10px 16px',
            background: '#e2e8f0',
            color: '#1e293b',
            border: 'none',
            borderRadius: '8px',
            cursor: 'pointer',
            marginBottom: '20px',
          }}
        >
          ← Back to Login
        </button>

        <h1
          style={{
            textAlign: 'center',
            fontSize: '38px',
            marginBottom: '10px',
          }}
        >
          🌍 AI Travel Planner
        </h1>

        <p
          style={{
            textAlign: 'center',
            color: '#666',
            fontSize: '18px',
            marginBottom: '35px',
          }}
        >
          Plan your perfect trip with AI
        </p>

        <div style={{ display: 'grid', gap: '20px' }}>
          <div>
            <label>📍 Destination</label>
            <input
              type="text"
              placeholder="Enter destination"
              value={destination}
              onChange={(e) => setDestination(e.target.value)}
              style={inputStyle}
            />
          </div>

          <div>
            <label>💰 Budget</label>
            <input
              type="number"
              placeholder="Enter your budget"
              value={budget}
              onChange={(e) => setBudget(e.target.value)}
              style={inputStyle}
            />
          </div>

          <div>
            <label>📅 Trip Duration</label>
            <input
              type="number"
              placeholder="Number of days"
              value={duration}
              onChange={(e) => setDuration(e.target.value)}
              style={inputStyle}
            />
          </div>

          <div>
            <label>❤️ Travel Interests</label>
            <select
              value={interests}
              onChange={(e) => setInterests(e.target.value)}
              style={inputStyle}
            >
              <option value="">Select your interest</option>
              <option value="Tourist Places">Tourist Places 🏛️</option>
              <option value="parks">Parks 🌳</option>
              <option value="Temples">Temples 🛕</option>
              <option value="Museums">Museums 🏺</option>
              <option value="Restaurants">Restaurants 🍽️</option>
              <option value="Food">Food 🍲</option>
              <option value="Beaches">Beaches 🏖️</option>
              <option value="Nature">Nature 🌿</option>
              <option value="Hotels">Hotels 🏨</option>
              <option value="Resorts">Resorts 🏝️</option>
              <option value="Activities">Activities 🎯</option>
              <option value="Shopping">Shopping 🛍️</option>
            </select>
          </div>

          <div>
            <label>👥 Number of Travelers</label>
            <input
              type="number"
              placeholder="Number of travelers"
              min={1}
              value={travelers}
              onChange={(e) => setTravelers(e.target.value)}
              style={inputStyle}
            />
          </div>

          <button
            type="button"
            onClick={handleGenerate}
            disabled={loading || generationInProgress.current}
            style={{
              padding: '16px',
              border: 'none',
              borderRadius: '10px',
              background: '#2563eb',
              color: 'white',
              fontSize: '18px',
              fontWeight: 'bold',
              cursor: 'pointer',
            }}
          >
            {loading ? 'Generating...' : '✨ Generate My Itinerary'}
          </button>
          <MapLoader destination={destination} />
          {error && (
            <p style={{ color: 'red', textAlign: 'center' }}>{error}</p>
          )}

          {itinerary && (
            <section
              aria-live="polite"
              style={{ display: 'grid', gap: '18px' }}
            >
              <div>
                <h2>Your itinerary for {itinerary.destination}</h2>
                <p>
                  {itinerary.days} days · {itinerary.travelers} traveler
                  {itinerary.travelers === 1 ? '' : 's'}
                </p>
                {itinerary.itinerary.map((day) => (
                  <article key={day.day} style={sectionStyle}>
                    <h3>Day {day.day}</h3>
                    {day.places.length > 0 && (
                      <p>
                        <strong>Places:</strong> {day.places.join(', ')}
                      </p>
                    )}
                    {day.activities.length > 0 && (
                      <p>
                        <strong>Activities:</strong> {day.activities.join(', ')}
                      </p>
                    )}
                    {day.places.length === 0 && day.activities.length === 0 && (
                      <p>
                        Explore local attractions and choose activities that
                        interest you.
                      </p>
                    )}
                  </article>
                ))}
              </div>

              <article style={sectionStyle}>
                <h3>Recommendations</h3>
                <ul>
                  {itinerary.recommendations.map((recommendation) => (
                    <li key={recommendation}>{recommendation}</li>
                  ))}
                </ul>
              </article>

              <article style={sectionStyle}>
                <h3>Budget summary (same currency as entered)</h3>
                <p>
                  Total: {formatBudget(itinerary.budget_summary.total_budget)}
                </p>
                <p>
                  Per day: {formatBudget(itinerary.budget_summary.daily_budget)}
                </p>
                <p>
                  Per person:{' '}
                  {formatBudget(itinerary.budget_summary.budget_per_person)}
                </p>
                <p>
                  Per person, per day:{' '}
                  {formatBudget(
                    itinerary.budget_summary.daily_budget_per_person,
                  )}
                </p>
              </article>
            </section>
          )}

          <section style={{ marginTop: '28px' }}>
            <h2>Saved trips</h2>
            {savedTripsLoading && <p>Loading saved trips...</p>}
            {savedTripsError && (
              <p role="alert" style={{ color: 'red' }}>
                {savedTripsError}
              </p>
            )}
            {!savedTripsLoading &&
              savedTrips.length === 0 &&
              !savedTripsError && <p>Your generated trips will appear here.</p>}
            {savedTrips.map((trip) => (
              <article key={trip.id} style={sectionStyle}>
                <h3>{trip.destination}</h3>
                <p>
                  {trip.days} days · {trip.travelers} traveler
                  {trip.travelers === 1 ? '' : 's'} · Budget{' '}
                  {formatBudget(trip.budget)}
                </p>
                <button
                  type="button"
                  onClick={() => void handleDeleteTrip(trip.id)}
                  style={secondaryButtonStyle}
                >
                  Delete trip
                </button>
              </article>
            ))}
          </section>
        </div>
      </div>
    </div>
  )
}

function formatBudget(value: number): string {
  return value.toLocaleString(undefined, { maximumFractionDigits: 2 })
}

const sectionStyle = {
  padding: '16px',
  border: '1px solid #e2e8f0',
  borderRadius: '10px',
  background: '#f8fafc',
}

const secondaryButtonStyle = {
  padding: '8px 12px',
  border: '1px solid #cbd5e1',
  borderRadius: '8px',
  background: 'white',
  color: '#1e293b',
  cursor: 'pointer',
}

const inputStyle = {
  width: '100%',
  padding: '13px',
  marginTop: '8px',
  border: '1px solid #d1d5db',
  borderRadius: '8px',
  fontSize: '16px',
  boxSizing: 'border-box' as const,
}
