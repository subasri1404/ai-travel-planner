
import json
import sqlite3
from pathlib import Path

# Existing database path
DB_PATH = (
    Path(__file__).resolve().parents[2]
    / "database"
    / "travel_planner.db"
)


# 1. Save Trip


def save_trip(trip, user_id):
    connection = sqlite3.connect(DB_PATH)

    try:
        
        cursor = connection.execute(
            """
            INSERT INTO trips (
                destination, days, budget, travelers,
                places, activities, user_id
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                trip["destination"],
                trip["days"],
                trip["budget"],
                trip["travelers"],
                json.dumps(trip["places"]),
                json.dumps(trip["activities"]),
                user_id
            )
        )


        connection.commit()
        return cursor.lastrowid

    finally:
        connection.close()



# 2. Get All Saved Trips

def get_all_trips(user_id):
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row

    try:
        rows = connection.execute(
            "SELECT * FROM trips WHERE user_id = ? ORDER BY id DESC",
            (user_id,)
        ).fetchall()

        trips = []

        for row in rows:
            trip = dict(row)
            trip["places"] = json.loads(trip["places"] or "[]")
            trip["activities"] = json.loads(trip["activities"] or "[]")
            trips.append(trip)

        return trips

    finally:
        connection.close()


        
def update_trip(trip_id, trip, user_id):
    connection = sqlite3.connect(DB_PATH)

    try:
        cursor = connection.execute(
            """
            UPDATE trips
            SET destination = ?,
                days = ?,
                budget = ?,
                travelers = ?,
                places = ?,
                activities = ?
            WHERE id = ? AND user_id = ?
            """,
            (
                trip["destination"],
                trip["days"],
                trip["budget"],
                trip["travelers"],
                json.dumps(trip["places"]),
                json.dumps(trip["activities"]),
                trip_id,
                user_id
            )
        )

        connection.commit()
        return cursor.rowcount > 0

    finally:
        connection.close()

def delete_trip(trip_id, user_id):
    connection = sqlite3.connect(DB_PATH)

    try:
        cursor = connection.execute(
            "DELETE FROM trips WHERE id = ? AND user_id = ?",
            (trip_id, user_id)
        )

        connection.commit()
        return cursor.rowcount > 0

    finally:
        connection.close()

