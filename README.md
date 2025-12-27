# Crypto Fraud Analytics Lab

An end-to-end mini "on-chain fraud lab" built with real Ethereum and Bitcoin data.

The goal of this project is to simulate parts of a Chainalysis-style workflow:
- Ingest real blockchain transactions (from BigQuery) into a local data platform.
- Define fraud-related behavioral KPIs.
- Generate alerts per wallet.
- Investigate suspicious wallets with notebooks and visualizations.

---

## Features

- **Multi-chain transaction store** using SQLite:
  - Supports Ethereum and Bitcoin (easily extendable to more chains).
  - Unified schema across chains (same columns).
- **KPI engine** implemented in Python:
  - `HIGH_FAN_IN_VELOCITY` – wallets receiving funds from many distinct senders in a short time window with high USD inflow.
  - `WHALE_FAN_OUT_BURST` – wallets sending funds to many distinct recipients in a short time window with high USD outflow.
- **Alerting layer**:
  - KPI results are stored in an `alerts` table with metadata and severity.
- **Investigation notebooks**:
  - Notebooks for KPI analysis and wallet-level investigation with basic visualizations.

This project is designed as a realistic, hands-on exercise for blockchain fraud analytics and as a portfolio/POC for interviews.

---

## Project Structure

```text
crypto_fraud/
├── db/
│   └── crypto_fraud.db          # SQLite database (auto-created)
├── data/
│   └── raw/
│       ├── ethereum_transactions_30d.csv
│       └── bitcoin_transactions_30d.csv
├── notebooks/
│   ├── kpi_high_fan_in_analysis.ipynb
│   ├── kpi_whale_fan_out_analysis.ipynb
│   └── wallet_investigation.ipynb
├── sql/
│   └── schema.sql               # Database schema (transactions, wallets, alerts)
├── src/
│   ├── __init__.py
│   ├── build_schema.py          # Creates DB schema
│   ├── load_csv_to_sqlite.py    # Loads CSV files into transactions table
│   ├── compute_kpi_high_fan_in.py
│   ├── compute_kpi_whale_fan_out.py
│   └── utils/
│       ├── __init__.py
│       └── db_connection.py     # get_connection()
└── requirements.txt
