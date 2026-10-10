
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).with_name("travel_planner.db")


def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def create_tables():
    connection = get_connection()

    try:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS trips (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                destination TEXT NOT NULL,
                days INTEGER NOT NULL,
                budget REAL NOT NULL,
                travelers INTEGER NOT NULL,
                places TEXT,
                activities TEXT
            )
        """)
        connection.commit()
    finally:
        connection.close()


if __name__ == "__main__":
    create_tables()
    print("Database and trips table created successfully!")
