# Vessel choice and charter strategy optimiser

Covers the problem statement's objective (move from spot to short / medium term multi-voyage contracts) and asks a (market entry timing), b (vessel type vs port limits) and c (idle time).

## 1. Vessel and port fit (`src/nauplan/vessels.py`)

For each vessel class on a route:

- **Vessels**: Baltic standard vessels (Handysize 38k, Supramax 63k, Panamax 82k, Capesize 182k) from the Baltic Guide to Market Benchmarks v8.7: DWT, design draft, LOA, beam, TPC, speed and fuel (`reference/vessel_specs.csv`).
- **Ports**: the most capable coal berth at the load and discharge port (`reference/berths.csv`). LOA, beam and minimum size are hard limits. A draft limit below the vessel's design draft cuts cargo by `(design draft - port draft) x 100 x TPC`; below 60% of intake the class is treated as uneconomic (placeholder). Hay Point uses the DBCT tidal rule; ports with only a water depth use depth / 1.10 (placeholder).
- **Haldia**: vessels can also discharge at Sandheads anchorage and transload to Haldia (extra cost and slower rate, placeholders).
- **Sea route**: if the laden draft exceeds 12.5 m the Torres Strait is avoided (`deep_draft` distance); `routing.avoid_suez` forces the Cape route.
- **Cost**: round voyage (laden + equal ballast leg + port days) priced with the Baltic TCE relation (GMB Appendix 3): sea days include a 5% weather margin; spot freight is the $/t that gives an owner the market timecharter hire.

Sanity check: Hay Point to Paradip on a Capesize gives 153,810 t, limited by Paradip's 16.5 m draft. The first 16.5 m Capesize at Paradip (6 Sep 2026, from Hay Point) carried 152,702 t.

## 2. Charter strategy optimiser (`src/nauplan/optimise/`)

A two-stage stochastic mixed-integer programme, solved with HiGHS via PuLP.

- **Now (first stage)**: number of period time charters per class, start month and length (3 or 6 months; a month-0 start locks today's hire, a later start pays that month's market hire); COA tonnes per route and month at a fixed $/t.
- **Per scenario (second stage)**: tonnes carried on chartered ships vs spot voyages; idle chartered vessel-days relet to the market (at a discount).
- **Constraints**: every month's programme is shipped exactly; chartered ships' voyage-days plus relet days cannot exceed their available days; only feasible vessel classes per route.
- **Objective**: expected cost + risk weight x CVaR (average cost of the worst 10% of scenarios).
- **Scenarios**: 200 six-month hire paths resampled from real 4-week moves of the BDRY freight proxy, scaled so expected hire equals today's (no directional view, as the forecast backtest supports).
- **Idle time**: reported per class and month as voyage days, relet days and idle days.

## 3. Example result (synthetic programme, placeholder costs)

`uv run nauplan plan` writes [reports/plan_example.md](../reports/plan_example.md). For the 3.88 Mt synthetic programme over Oct 2026 to Mar 2027:

| Strategy | Expected cost | CVaR 90% |
|---|---|---|
| All spot (current practice) | $99.6M | $128.9M |
| Optimised, expected cost only | $98.1M | $120.2M |
| Optimised, risk-aware | $98.3M | $98.5M |

- With no directional view, period contracts change expected cost little (about 1.3% here); their value is removing most of the tail risk.
- The risk-aware plan fixes 14 Panamaxes on 6-month charters now, adds one for a 3-month slot and some COA, and relets spare days in the lighter months rather than leaving ships idle.
- Panamax beats Capesize per tonne on these routes at today's hire, because Capesize hire is currently more than twice Panamax hire.
- Sensitivity: if period hire carries a 5% premium over spot, a cost-only plan stays spot, while a risk-aware plan still hedges at about 1.4% higher expected cost; at 10% it switches to COA.

These figures depend on placeholders (bunker price, port costs, rates, waiting days, contract premiums) and a synthetic programme. With SAIL's programme, fixtures and cost data the same model gives a real plan.

## Limits of this version

- A ship's voyage is not split across months; voyages are continuous quantities (a planning view, not a schedule).
- Ballast leg equals the laden leg (round voyages); triangulation and backhaul cargoes are not modelled.
- One hire multiplier path per scenario applies to all vessel classes (no class-specific spreads).
- No plant inventory: each month's tonnes must ship that month.
