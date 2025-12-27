from datetime import datetime, timedelta

from .utils.db_connection import get_connection


def parse_timestamp(ts: str) -> datetime:
    ts = ts.strip()
    ts = ts.replace(" UTC", "").replace("Z", "")
    return datetime.fromisoformat(ts)


def compute_and_store_whale_fan_out(
    chain: str,
    window_hours: int = 24,
    min_recipients: int = 5,
    min_total_usd: float = 1000.0,
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
        f"\n🔎 Computing WHALE_FAN_OUT for chain='{chain}' "
        f"window: {start_str} -> {end_str}"
    )

    # 2) Aggregate fan-out per source wallet in the time window
    rows = cur.execute(
        """
        SELECT
            from_wallet_id,
            COUNT(DISTINCT to_wallet_id) AS distinct_recipients,
            SUM(amount_usd) AS total_outflow_usd
        FROM transactions
        WHERE chain = ?
          AND block_timestamp >= ?
          AND block_timestamp <= ?
        GROUP BY from_wallet_id
        HAVING distinct_recipients >= ?
           AND total_outflow_usd >= ?
        """,
        (chain, start_str, end_str, min_recipients, min_total_usd)
    ).fetchall()

    if not rows:
        print(
            f"ℹ️ No WHALE_FAN_OUT alerts for chain='{chain}' "
            f"in the last {window_hours} hours."
        )
        conn.close()
        return

    now_iso = datetime.utcnow().isoformat() + "Z"

    inserted = 0
    for wallet_id, distinct_recipients, total_outflow_usd in rows:
        details = (
            f"distinct_recipients={distinct_recipients}, "
            f"total_outflow_usd={total_outflow_usd:.2f}, "
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
                "WHALE_FAN_OUT_BURST",
                "WHALE_FAN_OUT_WINDOW",
                wallet_id,
                "HIGH",
                chain,
                details,
            ),
        )
        inserted += 1

    conn.commit()
    conn.close()
    print(f"✅ Inserted {inserted} WHALE_FAN_OUT alerts for chain='{chain}'.")


def main():
    chains = ["ethereum", "bitcoin"]
    for chain in chains:
        compute_and_store_whale_fan_out(chain)


if __name__ == "__main__":
    main()
