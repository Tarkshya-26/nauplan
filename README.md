# NauPlan

Freight forecasting and vessel chartering decision support for bulk cargo imports to India's East Coast.
Team Vector66, Smart India Hackathon 2026, problem statement **SIH26006** (Ministry of Steel, SAIL).

**Status:** early build. Public data pipeline, port and route reference data, freight forecasting with a walk-forward backtest, vessel-port fit and the charter strategy optimiser work (on a synthetic cargo programme with placeholder costs). The dashboard is not built yet.

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

## Layout

```
src/nauplan/
  data/fetch.py         public data fetchers (freight proxy, Brent, USD/INR, Pink Sheet, marine weather)
  reference/            ports, berth limits, passages, vessel classes, distances (every limit cites a source)
  routing.py            sea distances (searoute over MARNET), with deep-draft and avoid-Suez variants
  forecast/             weekly panel, features, models, walk-forward backtest, volatility warning
  vessels.py            vessel-port fit (draft, LOA, beam) and voyage economics (Baltic TCE relation)
  optimise/             scenarios and stochastic MILP: spot vs time charter vs COA, CVaR
config/
  assumptions.toml      costs and parameters; every value marked SOURCED or PLACEHOLDER
  synthetic_programme.toml  demo cargo programme (synthetic, not SAIL data)
  cli.py                `nauplan` command
docs/
  problem-statement.md  official PS text and our reading of the asks
  data-sources.md       what data we have, what is missing, and the limits
  forecasting.md        forecasting method, protocol and results
  optimiser.md          vessel fit and charter optimiser: method, example result, limits
  plan.md               milestones
reports/backtest.md     latest backtest tables
reports/plan_example.md example charter plan
  submission.md         idea submission portal text
```
