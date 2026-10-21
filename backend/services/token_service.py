
import os
import jwt
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

if not JWT_SECRET_KEY:
    raise RuntimeError("JWT_SECRET_KEY is not set")

ALGORITHM = "HS256"


def create_access_token(user_id: int, email: str | None = None) -> str:
    payload = {
        "sub": str(user_id),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=30)
    }

    if email is not None:
        payload["email"] = email

    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=ALGORITHM)


def verify_access_token(token: str) -> int | None:
    try:
        payload = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[ALGORITHM],
            options={"require": ["sub", "exp"]}
        )
        user_id = int(payload["sub"])
        return user_id if user_id > 0 else None
    except (jwt.InvalidTokenError, KeyError, TypeError, ValueError):
        return None
