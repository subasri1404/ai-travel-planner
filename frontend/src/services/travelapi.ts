export const ACCESS_TOKEN_KEY = 'access_token'

const DEFAULT_API_BASE_URL = import.meta.env.DEV
  ? 'http://localhost:8000'
  : 'https://ai-travel-planner-backend-new.onrender.com'

const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL?.trim() || DEFAULT_API_BASE_URL
).replace(/\/+$/, '')

export type TravelRequest = {
  destination: string
  days: number
  budget: number
  travelers: number
  places: string[]
  activities: string[]
}

export type ItineraryResponse = TravelRequest & {
  trip_id: number
  itinerary: Array<{
    day: number
    places: string[]
    activities: string[]
  }>
  recommendations: string[]
  budget_summary: {
    total_budget: number
    daily_budget: number
    budget_per_person: number
    daily_budget_per_person: number
  }
}

export type SavedTrip = {
  id: number
  destination: string
  days: number
  budget: number
  travelers: number
  places: string[]
  activities: string[]
}

type LoginResponse = {
  access_token: string
  token_type: string
  id: number
  name: string
  email: string
}

export class ApiError extends Error {
  constructor(
    message: string,
    public readonly status: number,
  ) {
    super(message)
    this.name = 'ApiError'
  }
}

function getErrorDetail(payload: unknown): string | undefined {
  if (!payload || typeof payload !== 'object' || !('detail' in payload)) {
    return undefined
  }

  const detail = payload.detail
  if (typeof detail === 'string') {
    return detail
  }

  if (Array.isArray(detail)) {
    const messages = detail.flatMap((issue: unknown) => {
      if (!issue || typeof issue !== 'object' || !('msg' in issue)) {
        return []
      }
      return typeof issue.msg === 'string' ? [issue.msg] : []
    })
    return messages.length ? messages.join(' ') : undefined
  }

  return undefined
}

async function request<T>(
  path: string,
  init: RequestInit = {},
  token?: string,
  retryNetworkError = false,
): Promise<T> {
  const headers = new Headers(init.headers)
  if (init.body && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json')
  }
  if (token) {
    headers.set('Authorization', `Bearer ${token}`)
  }

  let response: Response | undefined
  for (let attempt = 0; !response; attempt += 1) {
    try {
      response = await fetch(`${API_BASE_URL}${path}`, {
        ...init,
        headers,
      })
    } catch (error) {
      if (error instanceof TypeError && retryNetworkError && attempt === 0) {
        continue
      }
      if (error instanceof TypeError) {
        throw new Error(
          `Unable to reach the backend at ${API_BASE_URL}. Check that it is running and allows this frontend origin in CORS.`,
        )
      }
      throw error
    }
  }

  const responseText = await response.text()
  let payload: unknown
  if (responseText) {
    try {
      payload = JSON.parse(responseText)
    } catch {
      if (response.ok) {
        throw new Error('The backend returned an invalid response.')
      }
    }
  }

  if (!response.ok) {
    throw new ApiError(
      getErrorDetail(payload) || `Request failed with HTTP ${response.status}.`,
      response.status,
    )
  }

  return payload as T
}

export function getAccessToken(): string | null {
  return typeof window === 'undefined'
    ? null
    : window.localStorage.getItem(ACCESS_TOKEN_KEY)
}

export function saveAccessToken(token: string): void {
  window.localStorage.setItem(ACCESS_TOKEN_KEY, token)
}

export function clearAccessToken(): void {
  if (typeof window !== 'undefined') {
    window.localStorage.removeItem(ACCESS_TOKEN_KEY)
  }
}

export function registerUser(data: {
  name: string
  email: string
  password: string
}): Promise<{ id: number; name: string; email: string }> {
  return request('/auth/register', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export function loginUser(data: {
  email: string
  password: string
}): Promise<LoginResponse> {
  return request('/auth/login', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export function generateItinerary(
  data: TravelRequest,
  token: string,
  idempotencyKey: string,
): Promise<ItineraryResponse> {
  return request(
    '/plan-trip',
    {
      method: 'POST',
      body: JSON.stringify(data),
      headers: { 'Idempotency-Key': idempotencyKey },
    },
    token,
    true,
  )
}

export function getTrips(token: string): Promise<{ trips: SavedTrip[] }> {
  return request('/trips', {}, token)
}

export function deleteTrip(tripId: number, token: string): Promise<void> {
  return request(`/trips/${tripId}`, { method: 'DELETE' }, token)
}
