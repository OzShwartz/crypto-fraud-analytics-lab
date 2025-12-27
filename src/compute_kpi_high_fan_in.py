from datetime import datetime, timedelta

from .utils.db_connection import get_connection


def parse_timestamp(ts: str) -> datetime:
    """
    Parse timestamp strings coming from BigQuery CSV export.

    BigQuery usually exports TIMESTAMP as:
      '2024-11-30 15:12:34 UTC'
    or ISO-like:
      '2024-11-30T15:12:34Z'

    This helper normalizes both.
    """
    ts = ts.strip()
    ts = ts.replace(" UTC", "").replace("Z", "")
    return datetime.fromisoformat(ts)


def compute_and_store_high_fan_in(
    chain: str,
    window_hours: int = 2,
    min_senders: int = 10,
    min_total_usd: float = 2000.0,
):
    conn = get_connection()
    cur = conn.cursor()

    # 1) Find latest timestamp for this chain
    row = cur.execute(
        "SELECT MAX(block_timestamp) FROM transactions WHERE chain = ?",
        (chain,)
    ).fetchone()

    if not row or row[0] is None:
        print(f"⚠️ No data found for chain='{chain}', skipping.")
        conn.close()
        return

    max_ts_str = row[0]
    max_ts = parse_timestamp(max_ts_str)
    window_start = max_ts - timedelta(hours=window_hours)

    start_str = window_start.isoformat()
    end_str = max_ts.isoformat()

    print(
        f"\n🔎 Computing HIGH_FAN_IN for chain='{chain}' "
        f"window: {start_str} -> {end_str}"
    )

    # 2) Aggregate fan-in per destination wallet in the time window
    fan_in_rows = cur.execute(
        """
        SELECT
            to_wallet_id,
            COUNT(DISTINCT from_wallet_id) AS distinct_senders,
            SUM(amount_usd) AS total_inflow_usd
        FROM transactions
        WHERE chain = ?
          AND block_timestamp >= ?
          AND block_timestamp <= ?
        GROUP BY to_wallet_id
        HAVING distinct_senders >= ?
           AND total_inflow_usd > ?
        """,
        (chain, start_str, end_str, min_senders, min_total_usd)
    ).fetchall()

    if not fan_in_rows:
        print(
            f"ℹ️ No HIGH_FAN_IN alerts for chain='{chain}' "
            f"in the last {window_hours} hours."
        )
        conn.close()
        return

    now_iso = datetime.utcnow().isoformat() + "Z"

    # 3) Insert alerts into alerts table
    inserted = 0
    for wallet_id, distinct_senders, total_inflow_usd in fan_in_rows:
        details = (
            f"distinct_senders={distinct_senders}, "
            f"total_inflow_usd={total_inflow_usd:.2f}, "
            f"window_hours={window_hours}"
        )

        cur.execute(
            """
            INSERT INTO alerts (
                created_at,
                kpi_name,
                alert_type,
                wallet_id,
                tx_hash,
                severity,
                chain,
                details
            )
            VALUES (?, ?, ?, ?, NULL, ?, ?, ?)
            """,
            (
                now_iso,
                "HIGH_FAN_IN_VELOCITY",
                "HIGH_FAN_IN_WINDOW",
                wallet_id,
                "HIGH",
                chain,
                details,
            ),
        )
        inserted += 1

    conn.commit()
    conn.close()
    print(f"✅ Inserted {inserted} HIGH_FAN_IN alerts for chain='{chain}'.")


def main():
    chains = ["ethereum", "bitcoin"]

    for chain in chains:
        compute_and_store_high_fan_in(
            chain=chain,
            window_hours=24,     # was 2
            min_senders=3,       # was 10
            min_total_usd=500.0  # was 2000
        )


if __name__ == "__main__":
    main()
