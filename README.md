# OctaQuant

Python-based Multi-Market Trading Engine with FastAPI and WebSockets.

## Features
- **Data integration**
  - DhanHQ for Indian indices (Nifty, BankNifty, Midcap, Sensex, Bankex)
  - Delta Exchange for crypto
  - Forex provider placeholder (MT5/OANDA)
- **Confluence strategy**
  - 26 EMA trend filter
  - SMC order blocks, value gaps, retail trap detection
  - Fibonacci 0.618/0.786 retracement zone entries
  - Gamma Blast scanning for NSE option chain OI spikes and gamma shifts
- **Risk management**
  - 10,000-iteration Monte Carlo risk-of-ruin gate before trade placement
  - RR enforcement between 1:2 and 1:10
- **Execution controls**
  - Default `PAPER_TRADING`
  - Logs virtual trades to PostgreSQL/Supabase-compatible database
  - 30-day validation gate before `LIVE_TRADING`
- **Infra**
  - FastAPI backend
  - WebSocket endpoint for real-time heartbeat/streaming events

## Run
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
uvicorn octaquant.api.app:app --reload
```

## API
- `GET /status`
- `POST /scan-and-trade` with payload:
```json
{"market":"india|crypto|forex", "symbol":"NIFTY"}
```
- `WS /ws/market`

## Deployment
- **Frontend (Vercel):** Deploy this repository as a static site and explicitly set **Output Directory** to `.` (dot) in the Vercel project settings to override framework presets.
- **Backend (Render):** Deploy with the root `Procfile` command: `web: python -m uvicorn octaquant.api.app:app --host 0.0.0.0 --port $PORT`.
- The Python backend source lives under `src/octaquant` so frontend hosting can remain independent from backend execution.
