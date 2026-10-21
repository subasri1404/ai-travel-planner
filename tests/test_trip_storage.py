import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from database import database
from database.database import (
    add_idempotency_key_to_trips,
    add_user_id_to_trips,
    create_tables,
    create_users_table,
    get_db_connection,
)
from services.trip_storage import (
    delete_trip,
    get_all_trips,
    save_trip,
    update_trip,
)


class TripStorageTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.database_path = Path(self.temp_dir.name) / "trips.db"
        self.database_patch = patch.object(
            database, "DB_PATH", self.database_path
        )
        self.database_patch.start()

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
            self.user_id = cursor.lastrowid
            connection.commit()
        finally:
            connection.close()

    def tearDown(self):
        self.database_patch.stop()
        self.temp_dir.cleanup()

    def test_idempotency_migration_adds_column_and_unique_index(self):
        legacy_path = Path(self.temp_dir.name) / "legacy.db"
        legacy_patch = patch.object(database, "DB_PATH", legacy_path)
        legacy_patch.start()
        try:
            connection = get_db_connection()
            try:
                connection.execute(
                    """
                    CREATE TABLE trips (
                        id INTEGER PRIMARY KEY,
                        user_id INTEGER
                    )
                    """
                )
                connection.commit()
            finally:
                connection.close()

            add_idempotency_key_to_trips()

            connection = get_db_connection()
            try:
                columns = {
                    row["name"]
                    for row in connection.execute(
                        "PRAGMA table_info(trips)"
                    ).fetchall()
                }
                indexes = {
                    row["name"]
                    for row in connection.execute(
                        "PRAGMA index_list(trips)"
                    ).fetchall()
                }
            finally:
                connection.close()
        finally:
            legacy_patch.stop()

        self.assertIn("idempotency_key", columns)
        self.assertIn("idx_trips_user_idempotency_key", indexes)

    def test_separate_saves_keep_distinct_ids_and_list_once(self):
        trip = {
            "destination": "Ooty",
            "days": 3,
            "budget": 10000,
            "travelers": 2,
            "places": ["Ooty Botanical Garden"],
            "activities": ["Walk through the botanical gardens"],
        }

        first_id = save_trip(trip, self.user_id)
        second_id = save_trip(trip, self.user_id)
        saved_trips = get_all_trips(self.user_id)

        self.assertNotEqual(first_id, second_id)
        self.assertEqual(
            [saved_trip["id"] for saved_trip in saved_trips],
            [second_id, first_id],
        )
        self.assertEqual(len(saved_trips), 2)

    def test_repeated_idempotency_key_returns_existing_trip(self):
        trip = {
            "destination": "Ooty",
            "days": 3,
            "budget": 10000,
            "travelers": 2,
            "places": ["Ooty Botanical Garden"],
            "activities": ["Walk through the botanical gardens"],
        }

        first_id = save_trip(trip, self.user_id, "request-1")
        retry_id = save_trip(trip, self.user_id, "request-1")
        new_attempt_id = save_trip(trip, self.user_id, "request-2")
        saved_trips = get_all_trips(self.user_id)

        self.assertEqual(retry_id, first_id)
        self.assertNotEqual(new_attempt_id, first_id)
        self.assertEqual(
            [saved_trip["id"] for saved_trip in saved_trips],
            [new_attempt_id, first_id],
        )

    def test_idempotency_key_is_scoped_to_user(self):
        connection = get_db_connection()
        try:
            cursor = connection.execute(
                """
                INSERT INTO users (name, email, password_hash)
                VALUES (?, ?, ?)
                """,
                ("Other User", "other@example.com", "test-hash"),
            )
            other_user_id = cursor.lastrowid
            connection.commit()
        finally:
            connection.close()

        trip = {
            "destination": "Ooty",
            "days": 3,
            "budget": 10000,
            "travelers": 2,
            "places": ["Ooty Botanical Garden"],
            "activities": ["Walk through the botanical gardens"],
        }

        first_id = save_trip(trip, self.user_id, "shared-key")
        other_user_id_trip = save_trip(trip, other_user_id, "shared-key")

        self.assertNotEqual(first_id, other_user_id_trip)

    def test_trip_cannot_be_saved_for_a_nonexistent_user(self):
        trip = {
            "destination": "Ooty",
            "days": 3,
            "budget": 10000,
            "travelers": 2,
            "places": ["Ooty Botanical Garden"],
            "activities": ["Walk through the botanical gardens"],
        }

        with self.assertRaises(sqlite3.IntegrityError):
            save_trip(trip, self.user_id + 1)

    def test_trips_cannot_be_read_updated_or_deleted_by_another_user(self):
        connection = get_db_connection()
        try:
            cursor = connection.execute(
                """
                INSERT INTO users (name, email, password_hash)
                VALUES (?, ?, ?)
                """,
                ("Other User", "other@example.com", "test-hash"),
            )
            other_user_id = cursor.lastrowid
            connection.commit()
        finally:
            connection.close()

        trip = {
            "destination": "Ooty",
            "days": 3,
            "budget": 10000,
            "travelers": 2,
            "places": ["Ooty Botanical Garden"],
            "activities": ["Walk through the botanical gardens"],
        }
        trip_id = save_trip(trip, self.user_id)

        self.assertEqual(get_all_trips(other_user_id), [])
        self.assertFalse(update_trip(trip_id, trip, other_user_id))
        self.assertFalse(delete_trip(trip_id, other_user_id))
        self.assertEqual(
            [saved_trip["id"] for saved_trip in get_all_trips(self.user_id)],
            [trip_id],
        )


if __name__ == "__main__":
    unittest.main()
