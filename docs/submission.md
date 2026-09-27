# Idea submission (portal text)

Revised on 28 Sep 2026 to cover every ask in the full problem statement (see [problem-statement.md](problem-statement.md)).
Deck: `~/SIH/SIH2026_NauPlan_Vector66.pdf` (built by `~/SIH/freight/build_freight.py`).

## Idea title (94 / 100 chars)

NauPlan: Freight Forecast-Driven Charter Strategy for Bulk Cargo Imports to India's East Coast

## Abstract (905 / 1,000 chars)

SAIL charters vessels for coal imports to India's East Coast largely through daily spot fixtures, which leaves costs exposed to volatile freight markets and port constraints. NauPlan is a proposed decision-support system to move this to planned short and medium term multi-voyage contracts. It forecasts spot and period freight rates per vessel class with uncertainty bands, checks each vessel class against draft, LOA, beam and handling limits at both loading and discharge ports, and uses a mixed-integer optimisation model to recommend when to enter the market, which vessel class to use and whether to fix spot, time charter or contract of affreightment. A voyage scheduler minimises idle time and ballast legs, and an alert layer warns of freight volatility, port waiting and cyclone risk. Plans will be validated by backtesting against the current all-spot practice on cost, idle days and demurrage.

## Description (4509 / 5,000 chars)

```
PROBLEM
SAIL imports bulk cargo such as coal from Australia, the US, Mozambique, Russia and Indonesia to East Coast ports including Paradip, Vizag, Gangavaram, Gopalpur, Dhamra, Sagar-Sandheads and Haldia. Vessels are mostly fixed through daily engagement with the spot market. This reactive approach misses good moments to lock in short or medium term contracts, and without forecasts it is hard to choose the right vessel class (Handysize, Supramax, Panamax, Capesize) for each parcel and route. Each port has its own draft, LOA, beam and handling limits, so a poor vessel choice causes delays, idle time and higher cost per tonne.

PROPOSED SOLUTION: NauPlan
A decision-support system that helps chartering managers move from many single spot fixtures to planned short and medium term multi-voyage contracts. The user enters cargo details, origin and destination ports and desired contract duration, and receives forecasts and concrete recommendations.

1. Freight forecasting
Forecasts spot and period charter rates per vessel class and route, from weeks to months ahead. Statistical baselines (seasonal naive, SARIMAX) are compared with LightGBM using lagged rates, fuel prices, coal prices, exchange rates and seasonality. Quantile regression gives P10, P50 and P90 bands, so every forecast carries its uncertainty.

2. Vessel and port fit
A database of load and discharge port limits (draft, LOA, beam, maximum size, handling rate) filters the vessel classes that can safely use both ends of a route. For each feasible class the system estimates voyage days, port time and cost per tonne, and recommends the most economical option for the parcel size.

3. Charter strategy optimiser (market entry timing)
A mixed-integer linear programme (PuLP or OR-Tools) takes the cargo programme for the coming months and chooses the mix of spot voyages, period time charters and contracts of affreightment, the vessel class and the best window to enter the market. Each plan is tested on scenarios drawn from the forecast bands and reports expected cost and downside risk (CVaR).

4. Idle time management
For vessels on period contracts, a voyage scheduler sequences loadings to minimise idle days and ballast (empty) legs. It flags upcoming low-demand gaps and suggests options such as shifting cargo timing, repositioning, or reletting the vessel for a market trip, valued at the forecast rate.

5. Early warnings
Alerts for rising freight volatility or a forecast regime change, unusual port waiting, fuel price moves, and cyclone or rough sea conditions (IMD bulletins, marine weather data).

6. Dashboard
A web dashboard shows freight forecast fan charts, the recommended vessel class with its constraint checks, the contract plan and entry timing, a voyage calendar with idle days, and active alerts. SHAP explanations show the main drivers of each forecast. Plans re-run weekly, and the manager approves every decision.

WHAT MAKES IT DIFFERENT
It links rate forecasts, port constraints at both ends and the fleet schedule in one loop. Forecast uncertainty feeds the optimiser directly, and the output is an explainable contract and voyage plan with cost and risk, not just a price prediction.

FEASIBILITY
We have built a working pipeline for public data: a dry bulk freight market proxy, Brent crude, USD/INR, coal prices and daily marine weather for all seven East Coast ports named in the problem statement. Forecasting, optimisation and the dashboard are not built yet. In the hackathon we will cover coal from one or two origins to two or three East Coast ports, with port limits taken from published sources and a clearly labelled synthetic cargo programme until real data is shared. The stack is open source (Python, pandas, LightGBM, statsmodels, OR-Tools, FastAPI, React). Features needing partners: licensed per-class and period freight rates (Baltic Exchange or SAIL's fixture history), AIS vessel tracking and berth-level port data.

VALIDATION
Forecasts: walk-forward backtesting with MAPE, MASE, pinball loss, interval coverage and directional accuracy. Decisions: replaying past periods and comparing NauPlan's plans with the current all-spot practice on total freight cost, idle days, ballast days and demurrage. Results will be reported only after testing.

EXPECTED IMPACT
A proactive chartering strategy with lower freight and demurrage costs, better use of chartered vessels, fewer delays at restricted ports and a clear, data-based view of freight risk before committing to a contract.
```

## Technology bucket

AI/ML, Cloud Computing, Blockchain
