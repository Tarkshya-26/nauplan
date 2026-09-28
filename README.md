# NauPlan

Freight forecasting and vessel chartering decision support for bulk cargo imports to India's East Coast.
Team Vector66, Smart India Hackathon 2026, problem statement **SIH26006** (Ministry of Steel, SAIL).

**Status:** early build. Public data pipeline, port and route reference data, freight forecasting with a walk-forward backtest, vessel-port fit, the charter strategy optimiser and the dashboard work (on a synthetic cargo programme with placeholder costs).

## Setup

Requires [uv](https://docs.astral.sh/uv/). On macOS, LightGBM also needs OpenMP: `brew install libomp`.

```bash
uv sync
uv run nauplan fetch       # download public data into data/raw/
uv run nauplan distances   # recompute sea distances
uv run nauplan backtest    # freight model backtest, writes reports/backtest.md
uv run nauplan forecast    # latest forecast, writes data/processed/forecast_latest.json
uv run nauplan plan        # vessel choice + charter plan, writes reports/plan_example.md
uv run pytest
```

### Dashboard

Requires Node 20+.

```bash
cd web && npm install && npm run build && cd ..
uv run nauplan serve       # dashboard and API on http://127.0.0.1:8000
```

For front-end work, run `uv run nauplan serve` and `cd web && npm run dev` (Vite on :5173, proxying /api).

## Layout

```
src/nauplan/
  data/fetch.py         public data fetchers (freight proxy, Brent, USD/INR, Pink Sheet, marine weather)
  reference/            ports, berth limits, passages, vessel classes, distances (every limit cites a source)
  routing.py            sea distances (searoute over MARNET), with deep-draft and avoid-Suez variants
  forecast/             weekly panel, features, models, walk-forward backtest, volatility warning
  vessels.py            vessel-port fit (draft, LOA, beam) and voyage economics (Baltic TCE relation)
  optimise/             scenarios and stochastic MILP: spot vs time charter vs COA, CVaR
  api.py                FastAPI endpoints for the dashboard; serves web/dist
web/                    React + Vite dashboard (chart map, draft gauge, outlook, charter plan, warnings)
config/
  assumptions.toml      costs and parameters; every value marked SOURCED or PLACEHOLDER
  synthetic_programme.toml  demo cargo programme (synthetic, not SAIL data)
  cli.py                `nauplan` command
docs/
  problem-statement.md  official PS text and our reading of the asks
  data-sources.md       what data we have, what is missing, and the limits
  forecasting.md        forecasting method, protocol and results
  optimiser.md          vessel fit and charter optimiser: method, example result, limits
  demo-script.md        7-minute judge demo: clicks, lines, fallback, likely questions
  plan.md               milestones
reports/backtest.md     latest backtest tables
reports/plan_example.md example charter plan
  submission.md         idea submission portal text
```
