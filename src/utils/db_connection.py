import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]  # points to project root (crypto_fraud/)
DB_PATH = BASE_DIR / "db" / "crypto_fraud.db"


def get_connection():
    """
    Returns a SQLite3 connection to the crypto_fraud.db database.
    The database file will be created automatically if it does not exist.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn
