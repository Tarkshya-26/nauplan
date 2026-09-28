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

## Port limits (sourced 28 Sep 2026)

`src/nauplan/reference/berths.csv`: coal-relevant berths of all 7 East Coast ports, each row with source URL, source date and access date. Blank means not yet sourced, never unlimited.

| Port | Berth | LOA m | Beam m | Draft m | Size | Source |
|---|---|---|---|---|---|---|
| Paradip | Cape-capable incl. WD-1 | 300 | 46 | 16.5 | 155,000 DWT | Paradip Port Authority site |
| Vizag | VGCB (outer harbour, coal import) | 300 | 50 | 18.1 | 200,000 DWT | VPA Traffic + Marine Dept (2021) |
| Gangavaram | Berths 5, 6 (coal priority) | 292 / 300 | - | 18.0 | 236,000 t displacement | Adani Gangavaram BPTS (Oct 2024) |
| Gopalpur | port level | - | - | 14.5 | - | Adani Ports page |
| Dhamra | BB1, BB2 (import) | 350 | - | 17.5 | 250,000 t displacement; 50,000 t/day | Dhamra BPTS (Oct 2025) |
| Haldia | impounded dock | 230 | 32 | 9.0 | - | MoPSW Sagar Vidya Kosh; SMP 2026 |
| Sandheads | transloading anchorage | - | - | not binding (40-50 m depth) | - | MoPSW Sagar Vidya Kosh |

Known gaps: Gopalpur berth-level LOA/beam (official PDF unreachable); beam at Gangavaram and Dhamra; discharge rates for all ports except Dhamra; Sandheads transloading rate; Paradip per-berth table (2020 circular taken offline). Dhamra and Haldia drafts change monthly / with tide.

Vessel classes: `vessel_classes.csv` holds Baltic Exchange DWT bands. Standard index vessel dimensions (draft, LOA, beam, TPC) are in the Baltic "Guide to Market Benchmarks" v8.4 (May 2026), which blocks scripted download; to add from a manually saved copy.

## Port congestion feeds (found, not yet parsed)

| Feed | What it has |
|---|---|
| SMP Kolkata, Haldia daily position PDFs (`smportkolkata.shipping.gov.in/smpk/hld/wp-content/uploads/sites/3/<yyyy>/<mm>/DP-<ddmmyyyy>.pdf`) | vessels at berth with LOA and draft, vessels waiting at Sandheads with readiness and ETA |
| Paradip Port daily traffic update PDFs (`paradipport.gov.in/uploads/<yyyy>/<mm>/dtr<ddmm>.pdf`) | daily traffic position |

## Needed but not yet sourced

| Data | Why | Likely source |
|---|---|---|
| Per-class freight rates (Capesize, Panamax, Supramax, Handysize) and route rates | core forecasting target | Baltic Exchange (licensed), shipbroker reports, or SAIL's own fixture history |
| Period time charter rates (6 / 12 month) | spot vs period decision | same as above |
| Port limits for load ports (Queensland, US East Coast, Mozambique, Russia, Indonesia) | vessel type feasibility at origin | port authority websites |
| Sea distances per origin-destination pair | voyage days and cost | port-to-port distance tables or computed routes |
| Port congestion / waiting time | idle time and risk | port authority reports; AIS (commercial) |
| SAIL cargo programme, contract and demurrage history | real decisions and validation | SAIL (problem owner) |
| Cyclone history for the Bay of Bengal | disruption risk | IMD RSMC New Delhi best-track data |

Rule: no invented numbers. Until real data arrives, anything synthetic lives in files named `synthetic_*` and is labelled as such in the UI.
