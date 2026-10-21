import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

os.environ.setdefault(
    "JWT_SECRET_KEY",
    "unit-test-only-secret-not-for-production",
)

from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from database import database
from database.database import (
    add_idempotency_key_to_trips,
    add_user_id_to_trips,
    create_tables,
    create_users_table,
    get_db_connection,
)
from main import TravelRequest, get_current_user, get_trips, plan_trip
from services.token_service import create_access_token


class TripEndpointTests(unittest.TestCase):
    def test_plan_trip_saves_once_and_get_trips_does_not_save(self):
        request = TravelRequest(
            destination="Ooty",
            days=2,
            budget=5000,
            travelers=2,
            places=[],
            activities=["Tourist Places"],
        )
        generated_plan = {
            "destination": "Ooty",
            "days": 2,
            "budget": 5000,
            "travelers": 2,
            "places": ["Ooty Botanical Garden"],
            "activities": ["Walk through the botanical gardens"],
            "itinerary": [
                {
                    "day": 1,
                    "places": ["Ooty Botanical Garden"],
                    "activities": ["Walk through the botanical gardens"],
                }
            ],
            "recommendations": [],
            "budget_summary": {},
        }

        with (
            patch("main.generate_travel_plan", return_value=generated_plan),
            patch("main.save_trip", return_value=42) as save_trip_mock,
            patch("main.get_all_trips", return_value=[]) as get_trips_mock,
        ):
            response = plan_trip(
                request,
                user_id=7,
                idempotency_key="request-1",
            )
            self.assertEqual(response["trip_id"], 42)
            save_trip_mock.assert_called_once_with(
                generated_plan,
                7,
                "request-1",
            )

            self.assertEqual(get_trips(user_id=7), {"trips": []})
            get_trips_mock.assert_called_once_with(7)
            save_trip_mock.assert_called_once()

    def test_authenticated_user_can_generate_and_save_trip(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "trips.db"
            with patch.object(database, "DB_PATH", database_path):
                create_users_table()
                create_tables()
                add_user_id_to_trips()
                add_idempotency_key_to_trips()

                connection = get_db_connection()
                try:
                    cursor = connection.execute(
                        """
                        INSERT INTO users (name, email, password_hash)
                        VALUES (?, ?, ?)
                        """,
                        ("Test User", "test@example.com", "test-hash"),
                    )
                    user_id = cursor.lastrowid
                    connection.commit()
                finally:
                    connection.close()

                token = create_access_token(user_id)
                credentials = HTTPAuthorizationCredentials(
                    scheme="Bearer",
                    credentials=token,
                )
                authenticated_user_id = get_current_user(credentials)

                response = plan_trip(
                    TravelRequest(
                        destination="Ooty",
                        days=2,
                        budget=5000,
                        travelers=2,
                    ),
                    user_id=authenticated_user_id,
                    idempotency_key=None,
                )

                self.assertEqual(response["trip_id"], 1)
                saved_trips = get_trips(user_id=authenticated_user_id)
                self.assertEqual(len(saved_trips["trips"]), 1)
                self.assertEqual(
                    saved_trips["trips"][0]["user_id"],
                    user_id,
                )

    def test_valid_token_for_missing_user_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "trips.db"
            with patch.object(database, "DB_PATH", database_path):
                create_users_table()
                token = create_access_token(999)
                credentials = HTTPAuthorizationCredentials(
                    scheme="Bearer",
                    credentials=token,
                )

                with self.assertRaises(HTTPException) as context:
                    get_current_user(credentials)

                self.assertEqual(context.exception.status_code, 401)
                self.assertEqual(
                    context.exception.detail,
                    "Authenticated user no longer exists",
                )


if __name__ == "__main__":
    unittest.main()
