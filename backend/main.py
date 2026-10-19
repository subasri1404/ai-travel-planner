
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List


from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from services.token_service import verify_access_token

from services.travel_planner import generate_travel_plan
from services.trip_storage import (
    save_trip,
    get_all_trips,
    update_trip,
    delete_trip
)

from routes.auth import router as auth_router

from database.database import (
    create_users_table,
    add_user_id_to_trips
)


# 1. Create FastAPI Application
app = FastAPI(
    title="AI Travel Planner",
    description="Generate and save personalized travel plans",
    version="1.0.0"
)


security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    user_id = verify_access_token(token)

    if user_id is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

    return user_id


app.include_router(auth_router)



# Create users table when backend starts
@app.on_event("startup")
def startup():
    create_users_table()
    add_user_id_to_trips()

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
def plan_trip(
    request: TravelRequest,
    user_id: int = Depends(get_current_user)
):
    
    try:
        result = generate_travel_plan(
            destination=request.destination,
            days=request.days,
            budget=request.budget,
            travelers=request.travelers,
            places=request.places,
            activities=request.activities
        )

        trip_id = save_trip(result, user_id)
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
def get_trips(user_id: int = Depends(get_current_user)):
    try:
        return {
            "trips": get_all_trips(user_id)
        }
    except Exception as error:
        print("GET TRIPS ERROR:", str(error))
        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve saved trips"
        )



# Update an existing trip

@app.put("/trips/{trip_id}")
def edit_trip(
    trip_id: int,
    request: TravelRequest,
    user_id: int = Depends(get_current_user)
):
    try:
        result = generate_travel_plan(
            destination=request.destination,
            days=request.days,
            budget=request.budget,
            travelers=request.travelers,
            places=request.places,
            activities=request.activities
        )

        updated = update_trip(trip_id, result, user_id)

        if not updated:
            raise HTTPException(
                status_code=404,
                detail="Trip not found"
            )

        result["trip_id"] = trip_id
        return result

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


# Delete an existing trip

@app.delete("/trips/{trip_id}")
def remove_trip(
    trip_id: int,
    user_id: int = Depends(get_current_user)
):
    deleted = delete_trip(trip_id, user_id)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Trip not found"
        )

    return {
        "message": "Trip deleted successfully",
        "trip_id": trip_id
    }
