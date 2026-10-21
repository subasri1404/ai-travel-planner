import os
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

os.environ["JWT_SECRET_KEY"] = "unit-test-only-secret-not-for-production"

import jwt
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from database import database
from database.database import create_users_table
from main import get_current_user
from schemas.auth import LoginRequest, RegisterRequest
from services.auth_service import login_user, register_user
from services.token_service import JWT_SECRET_KEY, verify_access_token


class AuthenticationTokenTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.database_patch = patch.object(
            database,
            "DB_PATH",
            Path(self.temp_dir.name) / "auth.db",
        )
        self.database_patch.start()

        create_users_table()
        register_user(
            RegisterRequest(
                name="Test User",
                email="auth-test@example.com",
                password="test-password-123",
            )
        )

    def tearDown(self):
        self.database_patch.stop()
        self.temp_dir.cleanup()

    def test_login_token_is_accepted_by_protected_route_dependency(self):
        login = login_user(
            LoginRequest(
                email="auth-test@example.com",
                password="test-password-123",
            )
        )
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=login["access_token"],
        )

        self.assertEqual(verify_access_token(login["access_token"]), login["id"])
        self.assertEqual(get_current_user(credentials), login["id"])

    def test_invalid_and_expired_tokens_are_rejected(self):
        self.assertIsNone(verify_access_token("not-a-jwt"))

        expired_token = jwt.encode(
            {
                "sub": "1",
                "exp": datetime.now(timezone.utc) - timedelta(minutes=1),
            },
            JWT_SECRET_KEY,
            algorithm="HS256",
        )

        self.assertIsNone(verify_access_token(expired_token))
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=expired_token,
        )
        with self.assertRaises(HTTPException) as context:
            get_current_user(credentials)
        self.assertEqual(context.exception.status_code, 401)


if __name__ == "__main__":
    unittest.main()
