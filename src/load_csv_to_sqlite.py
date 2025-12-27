import sys
from pathlib import Path

import pandas as pd

from .utils.db_connection import get_connection


def load_csv_to_transactions(csv_path: str):
    """
    Load a standardized CSV file into the transactions table.

    Expected CSV columns:
    tx_hash, block_timestamp, block_number,
    from_wallet_id, to_wallet_id,
    amount_native, native_symbol, amount_usd, chain
    """

    csv_file = Path(csv_path)
    if not csv_file.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_file}")

    print(f"\n📥 Loading CSV: {csv_file}")

    df = pd.read_csv(csv_file)

    required_cols = [
        "tx_hash",
        "block_timestamp",
        "block_number",
        "from_wallet_id",
        "to_wallet_id",
        "amount_native",
        "native_symbol",
        "amount_usd",
        "chain",
    ]

    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns in CSV: {missing}")

    # normalize numeric fields
    df["block_number"] = df["block_number"].astype("Int64")
    df["amount_native"] = df["amount_native"].astype(float)
    df["amount_usd"] = df["amount_usd"].astype(float)

    conn = get_connection()
    try:
        df.to_sql("transactions", conn, if_exists="append", index=False)
        print(f"✅ Inserted {len(df)} rows into 'transactions'")
    finally:
        conn.close()


if not __name__ == "__main__":
    sys.exit(0)

if len(sys.argv) < 2:
    print("Usage: python3 -m src.load_csv_to_sqlite <path_to_csv>")
    sys.exit(1)

load_csv_to_transactions(sys.argv[1])
