# Data sources

Checked working on 28 Sep 2026. `uv run nauplan fetch` downloads everything below into `data/raw/` (git-ignored).

## Free, working now

| File | Source | Coverage | Use | Limits |
|---|---|---|---|---|
| `bdry.parquet` | BDRY, Breakwave Dry Bulk Shipping ETF (Yahoo Finance via yfinance) | daily, Mar 2018 onward | freight market direction and volatility | ETF of freight futures: a blended market proxy, **not** a per-class or per-route rate |
| `brent_usd_bbl.parquet` | FRED `DCOILBRENTEU` | daily, 1987 onward | bunker fuel cost proxy | crude, not VLSFO bunker price |
| `usd_inr.parquet` | FRED `DEXINUS` | daily, 1973 onward | INR landed cost | |
| `pink_sheet.parquet` | World Bank Pink Sheet, monthly | 1960 onward | Australian and South African coal, iron ore, Brent | Australian coal is **thermal** coal; SAIL mainly imports **coking** coal |
| `marine.parquet` | Open-Meteo Marine API, ERA5 ocean model | daily, 2018 onward, 7 discharge ports | weather delay risk at discharge ports | ~5 day lag; total wave height only. Vizag and Gangavaram share one grid cell |

Port coordinates in `src/nauplan/reference/ports.csv` are approximate and only used for the weather lookup.

## Needed but not yet sourced

| Data | Why | Likely source |
|---|---|---|
| Per-class freight rates (Capesize, Panamax, Supramax, Handysize) and route rates | core forecasting target | Baltic Exchange (licensed), shipbroker reports, or SAIL's own fixture history |
| Period time charter rates (6 / 12 month) | spot vs period decision | same as above |
| Port limits: max draft, LOA, beam, DWT, handling rate for the 7 East Coast ports | vessel type feasibility | port authority websites and port handbooks; each value needs a cited source |
| Same for load ports (Queensland, US East Coast, Mozambique, Russia, Indonesia) | vessel type feasibility at origin | port authority websites |
| Sea distances per origin-destination pair | voyage days and cost | port-to-port distance tables or computed routes |
| Port congestion / waiting time | idle time and risk | port authority reports; AIS (commercial) |
| SAIL cargo programme, contract and demurrage history | real decisions and validation | SAIL (problem owner) |
| Cyclone history for the Bay of Bengal | disruption risk | IMD RSMC New Delhi best-track data |

Rule: no invented numbers. Until real data arrives, anything synthetic lives in files named `synthetic_*` and is labelled as such in the UI.
