-- Reset tables (for development / lab purposes)
DROP TABLE IF EXISTS alerts;
DROP TABLE IF EXISTS wallets;
DROP TABLE IF EXISTS transactions;

-- =====================================================================
-- TRANSACTIONS (multi-chain)
-- =====================================================================
CREATE TABLE IF NOT EXISTS transactions (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    tx_hash           TEXT,                     -- not UNIQUE, because same hash patterns may appear across sources
    block_timestamp   TEXT NOT NULL,            -- BigQuery export format or ISO8601
    block_number      INTEGER,
    from_wallet_id    TEXT NOT NULL,
    to_wallet_id      TEXT NOT NULL,
    amount_native     REAL NOT NULL,            -- native value (ETH, BTC, etc.)
    native_symbol     TEXT NOT NULL,            -- 'ETH', 'BTC', ...
    amount_usd        REAL NOT NULL,            -- USD estimate
    chain             TEXT NOT NULL             -- 'ethereum', 'bitcoin', ...
);

CREATE INDEX IF NOT EXISTS idx_transactions_to_wallet_time
    ON transactions (to_wallet_id, block_timestamp);

CREATE INDEX IF NOT EXISTS idx_transactions_from_wallet_time
    ON transactions (from_wallet_id, block_timestamp);

CREATE INDEX IF NOT EXISTS idx_transactions_chain_time
    ON transactions (chain, block_timestamp);

-- =====================================================================
-- WALLETS (optional enrichment; currently not enforced by FK)
-- =====================================================================
CREATE TABLE IF NOT EXISTS wallets (
    wallet_id          TEXT PRIMARY KEY,
    first_seen         TEXT,
    last_seen          TEXT,
    tx_count           INTEGER DEFAULT 0,
    total_inflow_usd   REAL DEFAULT 0.0,
    total_outflow_usd  REAL DEFAULT 0.0,
    total_volume_usd   REAL DEFAULT 0.0,
    is_whale           INTEGER DEFAULT 0,   -- 0 = no, 1 = yes
    risk_label         TEXT                -- 'normal', 'mixer', 'scam', etc.
);

-- =====================================================================
-- ALERTS (KPI results)
-- =====================================================================
CREATE TABLE IF NOT EXISTS alerts (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at  TEXT NOT NULL,
    kpi_name    TEXT NOT NULL,       -- e.g. 'HIGH_FAN_IN_VELOCITY'
    alert_type  TEXT NOT NULL,       -- e.g. 'HIGH_FAN_IN_WINDOW'
    wallet_id   TEXT NOT NULL,
    tx_hash     TEXT,                -- optional: specific transaction, if relevant
    severity    TEXT NOT NULL,       -- 'LOW', 'MEDIUM', 'HIGH'
    chain       TEXT NOT NULL,       -- 'ethereum', 'bitcoin', ...
    details     TEXT                 -- free-text / JSON
);

CREATE INDEX IF NOT EXISTS idx_alerts_wallet_kpi_chain
    ON alerts (wallet_id, kpi_name, chain);
