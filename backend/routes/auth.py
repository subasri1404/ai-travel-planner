from fastapi import APIRouter, HTTPException

from backend.schemas.auth import RegisterRequest, LoginRequest, UserResponse
from backend.services.auth_service import register_user, login_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse)
def register(request: RegisterRequest):
    try:
        return register_user(request)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))


@router.post("/login")
def login(request: LoginRequest):
    try:
        return login_user(request)
    except ValueError as error:
        raise HTTPException(status_code=401, detail=str(error))