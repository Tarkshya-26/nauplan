# NauPlan

Freight forecasting and vessel chartering decision support for bulk cargo imports to India's East Coast.
Team Vector66, Smart India Hackathon 2026, problem statement **SIH26006** (Ministry of Steel, SAIL).

**Status:** early build. Public data pipeline, port and route reference data, and freight forecasting with a walk-forward backtest work. Optimisation and dashboard are not built yet.

## Setup

Requires [uv](https://docs.astral.sh/uv/). On macOS, LightGBM also needs OpenMP: `brew install libomp`.

```bash
uv sync
uv run nauplan fetch       # download public data into data/raw/
uv run nauplan distances   # recompute sea distances
uv run nauplan backtest    # freight model backtest, writes reports/backtest.md
uv run nauplan forecast    # latest forecast, writes data/processed/forecast_latest.json
uv run pytest
```

## Layout

```
src/nauplan/
  data/fetch.py         public data fetchers (freight proxy, Brent, USD/INR, Pink Sheet, marine weather)
  reference/            ports, berth limits, passages, vessel classes, distances (every limit cites a source)
  routing.py            sea distances (searoute over MARNET), with deep-draft and avoid-Suez variants
  forecast/             weekly panel, features, models, walk-forward backtest, volatility warning
  cli.py                `nauplan` command
docs/
  problem-statement.md  official PS text and our reading of the asks
  data-sources.md       what data we have, what is missing, and the limits
  forecasting.md        forecasting method, protocol and results
  plan.md               milestones
reports/backtest.md     latest backtest tables
  submission.md         idea submission portal text
```
