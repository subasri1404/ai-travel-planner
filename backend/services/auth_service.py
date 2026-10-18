
import hashlib
import hmac
import secrets
import os
import jwt

from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime, timedelta, timezone

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

if not JWT_SECRET_KEY:
    raise RuntimeError("JWT_SECRET_KEY environment variable is not set")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_access_token(user_id: int, email: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": str(user_id),
        "email": email,
        "exp": expire,
    }

    return jwt.encode(
        payload,
        JWT_SECRET_KEY,
        algorithm=ALGORITHM
    )


from database.database import get_db_connection


# Secure password hashing using PBKDF2
def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    iterations = 600_000

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        iterations
    ).hex()

    return f"pbkdf2_sha256${iterations}${salt}${password_hash}"


# Verify both new PBKDF2 hashes and old SHA-256 hashes
def verify_password(password: str, password_hash: str) -> bool:
    if password_hash.startswith("pbkdf2_sha256$"):
        try:
            algorithm, iterations, salt, stored_hash = password_hash.split("$")

            calculated_hash = hashlib.pbkdf2_hmac(
                "sha256",
                password.encode("utf-8"),
                salt.encode("utf-8"),
                int(iterations)
            ).hex()

            return hmac.compare_digest(calculated_hash, stored_hash)

        except (ValueError, TypeError):
            return False

    # Support accounts created with the previous SHA-256 method
    legacy_hash = hashlib.sha256(
        password.encode("utf-8")
    ).hexdigest()

    return hmac.compare_digest(legacy_hash, password_hash)


def register_user(request):
    connection = get_db_connection()

    try:
        existing = connection.execute(
            "SELECT id FROM users WHERE email = ?",
            (str(request.email),)
        ).fetchone()

        if existing:
            raise ValueError("Email already registered")

        cursor = connection.execute(
            """
            INSERT INTO users (name, email, password_hash)
            VALUES (?, ?, ?)
            """,
            (
                request.name,
                str(request.email),
                hash_password(request.password)
            )
        )

        connection.commit()

        return {
            "id": cursor.lastrowid,
            "name": request.name,
            "email": str(request.email)
        }

    finally:
        connection.close()



def login_user(request):
    connection = get_db_connection()

    try:
        user = connection.execute(
            "SELECT * FROM users WHERE email = ?",
            (str(request.email),)
        ).fetchone()

        if not user or not verify_password(
            request.password,
            user["password_hash"]
        ):
            raise ValueError("Invalid email or password")

        # Upgrade old password hash if needed
        if not user["password_hash"].startswith("pbkdf2_sha256$"):
            new_hash = hash_password(request.password)

            connection.execute(
                "UPDATE users SET password_hash = ? WHERE id = ?",
                (new_hash, user["id"])
            )
            connection.commit()

        # Create token for every successful login
        access_token = create_access_token(
            user_id=user["id"],
            email=user["email"]
        )

        return {
            "message": "Login successful",
            "access_token": access_token,
            "token_type": "bearer",
            "id": user["id"],
            "name": user["name"],
            "email": user["email"]
        }

    finally:
        connection.close()
