from pathlib import Path

from .utils.db_connection import get_connection

def run_schema():
    """
    Create database tables from the SQL schema file.
    """
    base_dir = Path(__file__).resolve().parents[1]  # project root (crypto_fraud)
    schema_path = base_dir / "sql" / "schema.sql"

    if not schema_path.exists():
        raise FileNotFoundError(f"Schema file not found at: {schema_path}")

    with open(schema_path, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.executescript(schema_sql)
        conn.commit()
        print("✅ Database schema created successfully.")
    finally:
        conn.close()


if __name__ == "__main__":
    run_schema()
