# AI Travel Planner frontend

This React + Vite + TanStack Start app talks to the FastAPI backend.

## Backend connection and local development

The frontend uses `http://localhost:8000` while running Vite in development
and defaults to `https://ai-travel-planner-backend-new.onrender.com` in a
production build. `VITE_API_BASE_URL` overrides either default.

For local development, the frontend's default API URL is `http://localhost:8000`.
Start the backend and frontend in separate PowerShell terminals, from the
project root:

```powershell
Set-Location .\backend
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

```powershell
Set-Location .\frontend
npm ci
npm run dev
```

The development server uses port `5173`. The backend's `CORS_ORIGINS` setting
must include the exact frontend origin. The backend currently permits
`http://localhost:5173`; the deployed backend's CORS preflight has been checked
for that origin and allows the Authorization, Content-Type, and
Idempotency-Key headers. For a hosted frontend, configure the backend's
`CORS_ORIGINS` environment variable on Render with the exact hosted origin
(scheme and host, comma-separated if multiple); do not use `*`.

Login stores the returned access token in browser local storage. Protected
requests send it as a Bearer token. Tokens expire after 30 minutes; when a
protected request receives HTTP 401, the frontend clears the stale token and
asks the user to log in again. If a newly issued token is rejected repeatedly,
check that the deployed backend is using the expected `JWT_SECRET_KEY` and
database. Keep JWT secrets server-side; they are not frontend environment
variables.

## Build and deployment

Run `npm run build` to create the Nitro server in `.output`. Start the built app
with `node .output/server/index.mjs`. If you override the production API URL,
set `VITE_API_BASE_URL` at build time. Configure the backend's `CORS_ORIGINS`
with the deployed frontend origin. These values are public origins, not
secrets.

The map currently uses Leaflet with OpenStreetMap tiles, Nominatim place search,
and OSRM routing; it does not use Google Maps or require a Google Maps API key.
