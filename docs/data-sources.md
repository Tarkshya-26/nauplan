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

Vessel classes: `vessel_classes.csv` holds Baltic Exchange DWT bands; `vessel_specs.csv` holds the Baltic standard vessels (DWT, draft, LOA, beam, TPC, speed and fuel) from the Guide to Market Benchmarks v8.7 (Aug 2026), read from a copy saved manually (the site blocks scripted download). Current hire per class comes from the Baltic index ticker divided by the GMB multipliers (see config/assumptions.toml). The Baltic S8_63 route (Supramax, Indonesia to East Coast India, coal) is the licensed series closest to this problem.

## Load ports (sourced 28 Sep 2026)

12 load ports cover all five origins in the problem statement. Every row in `berths.csv` has a `source_type`: `official_*`, `government_dataset` (NGA World Port Index) or `secondary`. Secondary and conflicting values are flagged in `notes`; treat them as provisional.

| Origin | Port | Key limits | Source type |
|---|---|---|---|
| Australia | Hay Point (DBCT) | 220,000 DWT, 320 m, 52 m beam; draft tidal: (14.8 + tide - 1) / 1.05 | official terminal |
| Australia | Gladstone (RG Tanna) | 220,000 DWT, 315 m, 18.8 m berth pocket, 6,000 t/h | official port |
| US | Hampton Roads (Lamberts Point) | 50 ft draft, 175 ft beam, 8,000 t/h | official operator |
| US | Baltimore | 14 m depth category | WPI |
| Mozambique | Nacala | Capesize, limits not sourced | - |
| Mozambique | Maputo / Matola | 13 m draft | WPI |
| Mozambique | Beira | 8 m depth category | WPI |
| Russia | Vostochny | 350 m, 45 m beam, 16 m draft | WPI |
| Russia | Vanino | 292 m, 45 m, 18 m (conflicts with agent 13.5 m) | WPI |
| Russia | Ust-Luga | 260 m, 44 m, 14.55 m, 110,000 DWT | secondary |
| Indonesia | Tanjung Bara | 220,000 DWT, 17.2 m draft, 9,000 t/h | official operator |
| Indonesia | Taboneo anchorage | floating cranes, Handymax to Capesize | secondary |

Coordinates come from UN/LOCODE or WPI where available, otherwise approximate (used for routing only).

## Passages and sea distances

`passages.csv`: Torres Strait max draft 12.5 m (tidal windows above 12.2 m), Danish straits Route T depth 16.4 to 17 m, Suez Canal 20.1 m.

`distances.csv` (`uv run nauplan distances`): every load x discharge pair, computed with searoute over the Eurostat MARNET network, in three variants: `shortest`, `deep_draft` (no Torres Strait) and `avoid_suez` (Cape of Good Hope). These are modelled routes, not a published distance table; check against SAIL voyage records.

Example, to Paradip: Hay Point 4,899 nm shortest vs 5,813 nm deep draft; Hampton Roads 9,904 nm via Suez vs 12,222 nm via the Cape; Nacala 3,879 nm.

## Port congestion feeds (found, not yet parsed)

| Feed | What it has |
|---|---|
| SMP Kolkata, Haldia daily position PDFs (`smportkolkata.shipping.gov.in/smpk/hld/wp-content/uploads/sites/3/<yyyy>/<mm>/DP-<ddmmyyyy>.pdf`) | vessels at berth with LOA and draft, vessels waiting at Sandheads with readiness and ETA |
| Paradip Port daily traffic update PDFs (`paradipport.gov.in/uploads/<yyyy>/<mm>/dtr<ddmm>.pdf`) | daily traffic position |

## Needed but not yet sourced

| Data | Why | Likely source |
|---|---|---|
| Verified limits for Nacala, Baltimore, Vanino, Ust-Luga, Taboneo; Gladstone channel draft; Hay Point Coal Terminal | vessel type feasibility at origin | port authorities, SAIL agents |
| Per-class freight rates (Capesize, Panamax, Supramax, Handysize) and route rates | core forecasting target | Baltic Exchange (licensed), shipbroker reports, or SAIL's own fixture history |
| Period time charter rates (6 / 12 month) | spot vs period decision | same as above |
| Port congestion / waiting time | idle time and risk | port authority reports; AIS (commercial) |
| SAIL cargo programme, contract and demurrage history | real decisions and validation | SAIL (problem owner) |
| Cyclone history for the Bay of Bengal | disruption risk | IMD RSMC New Delhi best-track data |

Rule: no invented numbers. Until real data arrives, anything synthetic lives in files named `synthetic_*` and is labelled as such in the UI.
