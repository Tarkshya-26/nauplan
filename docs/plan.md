# Build plan

Mapped to the asks in [problem-statement.md](problem-statement.md).

| # | Milestone | Covers | Output |
|---|---|---|---|
| M0 | Repo, public data pipeline | groundwork | `nauplan fetch` (done) |
| M1 | Reference data | ask b | Done: berth limits for 7 discharge and 12 load ports, passage limits, vessel DWT bands, distance matrix (3 route variants). Open: gaps in data-sources.md, class dimensions |
| M2 | Freight forecasting + backtest harness | ask a, d | Done on the public proxy: walk-forward backtest, 6 models, dev/holdout split, volatility warning; see forecasting.md. Rerun on per-class rates when available |
| M3 | Voyage cost and vessel type model | ask b | Done: Baltic standard vessels, draft/LOA/beam fit at both ports, Sandheads transloading, Torres-aware routing, TCE-based cost per tonne |
| M4 | Charter strategy optimiser | objective, ask a, c | Done: two-stage stochastic MILP (HiGHS), spot vs period TC vs COA, entry month, relet of idle days, CVaR; sensitivity to period premium. Needs SAIL programme and cost data |
| M5 | Idle time and early warnings | ask c, d | ballast leg and idle-day estimates, repositioning suggestions; volatility, weather and congestion alerts |
| M6 | API and dashboard | UI | FastAPI + React: inputs (cargo, O-D, contract duration) to forecasts and recommendations |
| M7 | Validation and demo | all | backtest report vs rule-based policies; demo script |

Priority is M1 to M3: they decide whether the rest is credible.
