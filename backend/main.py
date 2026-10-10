
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List

from services.travel_planner import generate_travel_plan
from services.trip_storage import (
    save_trip,
    get_all_trips,
    update_trip,
    delete_trip
)


# 1. Create FastAPI Application
app = FastAPI(
    title="AI Travel Planner",
    description="Generate and save personalized travel plans",
    version="1.0.0"
)


# 2. Allow Frontend Connections
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# 3. Validate Travel Request
class TravelRequest(BaseModel):
    destination: str = Field(min_length=1)
    days: int = Field(gt=0, le=30)
    budget: float = Field(gt=0)
    travelers: int = Field(gt=0, le=100)
    places: List[str] = Field(default_factory=list)
    activities: List[str] = Field(default_factory=list)


# 4. Home API
@app.get("/")
def home():
    return {
        "message": "AI Travel Planner API is running"
    }


# 5. Generate and Save Travel Plan
@app.post("/plan-trip")
def plan_trip(request: TravelRequest):
    try:
        result = generate_travel_plan(
            destination=request.destination,
            days=request.days,
            budget=request.budget,
            travelers=request.travelers,
            places=request.places,
            activities=request.activities
        )

        trip_id = save_trip(result)
        result["trip_id"] = trip_id

        print("FINAL API RESPONSE:", result)

        return result

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )
    except Exception as error:
        print("PLAN TRIP ERROR:", str(error))
        raise HTTPException(
            status_code=500,
            detail="Unable to generate or save travel plan"
        )


# 6. Get All Saved Trips
@app.get("/trips")
def get_trips():
    try:
        return {
            "trips": get_all_trips()
        }
    except Exception as error:
        print("GET TRIPS ERROR:", str(error))
        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve saved trips"
        )



# Update an existing trip
@app.put("/trips/{trip_id}")
def edit_trip(trip_id: int, request: TravelRequest):
    try:
        result = generate_travel_plan(
            destination=request.destination,
            days=request.days,
            budget=request.budget,
            travelers=request.travelers,
            places=request.places,
            activities=request.activities
        )

        updated = update_trip(trip_id, result)

        if not updated:
            raise HTTPException(
                status_code=404,
                detail="Trip not found"
            )

        result["trip_id"] = trip_id
        return result

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))


# Delete an existing trip
@app.delete("/trips/{trip_id}")
def remove_trip(trip_id: int):
    deleted = delete_trip(trip_id)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Trip not found"
        )

    return {
        "message": "Trip deleted successfully",
        "trip_id": trip_id
    }
