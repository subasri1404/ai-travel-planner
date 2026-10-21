# FastAPI backend

## Local development

From this directory, create a local `.env` file using `.env.example` as a guide,
set a private `JWT_SECRET_KEY`, and start the API:

```powershell
.\venv\Scripts\python.exe -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Do not commit `.env`. The API defaults to the SQLite database at
`../database/travel_planner.db`; set `DATABASE_PATH` to change it.

## Itinerary suggestions

The planner uses a small built-in set of curated Ooty place and activity
suggestions, based on the project's existing demo itinerary. These are static
suggestions, not live availability or AI-generated results. Other destinations
use places supplied in the request; when none are supplied, the API says that
curated suggestions are unavailable instead of presenting a generic interest
as a place or daily activity.

## Deployment configuration

Configure `JWT_SECRET_KEY` as a secret environment variable and set
`CORS_ORIGINS` to the exact comma-separated frontend origins (scheme and host,
including a non-default port if applicable). Do not use `*` for authenticated
cross-origin requests.

SQLite data is only durable if `DATABASE_PATH` points to a persistent volume
provided by the hosting platform. Set the platform's start command to:

```text
python -m uvicorn main:app --host 0.0.0.0 --port $PORT
```
