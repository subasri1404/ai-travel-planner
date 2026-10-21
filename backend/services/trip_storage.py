
import json

from database.database import get_db_connection


# 1. Save Trip


def save_trip(trip, user_id, idempotency_key=None):
    connection = get_db_connection()

    try:
        
        cursor = connection.execute(
            """
            INSERT INTO trips (
                destination, days, budget, travelers,
                places, activities, user_id, idempotency_key
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id, idempotency_key) DO NOTHING
            """,
            (
                trip["destination"],
                trip["days"],
                trip["budget"],
                trip["travelers"],
                json.dumps(trip["places"]),
                json.dumps(trip["activities"]),
                user_id,
                idempotency_key
            )
        )

        connection.commit()
        if cursor.rowcount == 0:
            row = connection.execute(
                """
                SELECT id FROM trips
                WHERE user_id = ? AND idempotency_key = ?
                """,
                (user_id, idempotency_key)
            ).fetchone()
            return row["id"]

        return cursor.lastrowid

    finally:
        connection.close()



# 2. Get All Saved Trips

def get_all_trips(user_id):
    connection = get_db_connection()

    try:
        rows = connection.execute(
            """
            SELECT id, destination, days, budget, travelers,
                   places, activities, user_id
            FROM trips
            WHERE user_id = ?
            ORDER BY id DESC
            """,
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
    connection = get_db_connection()

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
    connection = get_db_connection()

    try:
        cursor = connection.execute(
            "DELETE FROM trips WHERE id = ? AND user_id = ?",
            (trip_id, user_id)
        )

        connection.commit()
        return cursor.rowcount > 0

    finally:
        connection.close()
