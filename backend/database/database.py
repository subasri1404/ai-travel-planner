import sqlite3
import os
from pathlib import Path

default_db_path = (
    Path(__file__).resolve().parents[2]
    / "database"
    / "travel_planner.db"
)
configured_db_path = os.getenv("DATABASE_PATH")
DB_PATH = (
    Path(configured_db_path).expanduser()
    if configured_db_path and configured_db_path.strip()
    else default_db_path
)

def get_db_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.execute("PRAGMA foreign_keys = ON")
    connection.row_factory = sqlite3.Row
    return connection

def create_users_table():
    connection = get_db_connection()
    try:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL
            )
        """)
        connection.commit()
    finally:
        connection.close()



        
def create_tables():
    connection = get_db_connection()

    try:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS trips (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                destination TEXT NOT NULL,
                days INTEGER NOT NULL,
                budget REAL NOT NULL,
                travelers INTEGER NOT NULL,
                places TEXT,
                activities TEXT,
                user_id INTEGER REFERENCES users(id),
                idempotency_key TEXT
            )
        """)
        connection.commit()
    finally:
        connection.close()


        
def add_user_id_to_trips():
    connection = get_db_connection()
    try:
        columns = connection.execute(
            "PRAGMA table_info(trips)"
        ).fetchall()

        column_names = [column["name"] for column in columns]

        if "user_id" not in column_names:
            connection.execute(
                "ALTER TABLE trips ADD COLUMN user_id INTEGER REFERENCES users(id)"
            )
            connection.commit()
    finally:
        connection.close()


def add_idempotency_key_to_trips():
    connection = get_db_connection()
    try:
        columns = connection.execute(
            "PRAGMA table_info(trips)"
        ).fetchall()

        column_names = [column["name"] for column in columns]

        if "idempotency_key" not in column_names:
            connection.execute(
                "ALTER TABLE trips ADD COLUMN idempotency_key TEXT"
            )

        connection.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS
                idx_trips_user_idempotency_key
            ON trips (user_id, idempotency_key)
            """
        )
        connection.commit()
    finally:
        connection.close()
