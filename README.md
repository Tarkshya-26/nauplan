# NauPlan

Freight forecasting and vessel chartering decision support for bulk cargo imports to India's East Coast.
Team Vector66, Smart India Hackathon 2026, problem statement **SIH26006** (Ministry of Steel, SAIL).

**Status:** early build. The public data pipeline works; forecasting, optimisation and dashboard are not built yet.

## Setup

Requires [uv](https://docs.astral.sh/uv/).

```bash
uv sync
uv run nauplan fetch   # download public data into data/raw/
uv run pytest
```

## Layout

```
src/nauplan/
  data/fetch.py         public data fetchers (freight proxy, Brent, USD/INR, Pink Sheet, marine weather)
  reference/ports.csv   port constraints (values must cite a source)
  cli.py                `nauplan` command
docs/
  problem-statement.md  official PS text and our reading of the asks
  data-sources.md       what data we have, what is missing, and the limits
  plan.md               milestones
  submission.md         idea submission portal text
```
