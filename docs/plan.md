# Build plan

Mapped to the asks in [problem-statement.md](problem-statement.md).

| # | Milestone | Covers | Output |
|---|---|---|---|
| M0 | Repo, public data pipeline | groundwork | `nauplan fetch` (done) |
| M1 | Reference data | ask b | ports and vessel class tables with cited constraint values; O-D distance table |
| M2 | Freight forecasting + backtest harness | ask a, d | walk-forward backtest; baselines (naive, seasonal naive, SARIMAX) vs LightGBM quantile; P10/P50/P90 |
| M3 | Voyage cost and vessel type model | ask b | for a cargo parcel and O-D pair: feasible classes, voyage days, cost per tonne incl. port time |
| M4 | Charter strategy optimiser | objective, ask a | MILP over a cargo programme: spot vs period time charter vs COA, timing, vessel class; evaluated on forecast scenarios (expected cost, CVaR) |
| M5 | Idle time and early warnings | ask c, d | ballast leg and idle-day estimates, repositioning suggestions; volatility, weather and congestion alerts |
| M6 | API and dashboard | UI | FastAPI + React: inputs (cargo, O-D, contract duration) to forecasts and recommendations |
| M7 | Validation and demo | all | backtest report vs rule-based policies; demo script |

Priority is M1 to M3: they decide whether the rest is credible.
