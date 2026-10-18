import sqlite3
from pathlib import Path

DB_PATH = (
    Path(__file__).resolve().parents[2]
    / "database"
    / "travel_planner.db"
)

def get_db_connection():
    connection = sqlite3.connect(DB_PATH)
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
