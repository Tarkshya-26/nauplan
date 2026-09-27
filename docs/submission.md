# Idea submission (portal text)

As prepared on 28 Sep 2026. Deck: `~/SIH/SIH2026_NauPlan_Vector66.pdf` (built by `~/SIH/freight/build_freight.py`).

## Idea title (89 chars)

NauPlan: Freight Forecast-Driven Planning of Bulk Cargo Procurement and Vessel Chartering

## Abstract (971 chars)

Importing bulk cargo to India's East Coast ports means timing two coupled decisions under volatile markets: when to buy cargo and when and how to charter a vessel. Dry bulk freight rates can swing sharply within weeks, and port congestion or cyclone season can add delay and demurrage. NauPlan is a proposed decision-support system that forecasts freight rates by vessel class with uncertainty bands (quantile gradient boosting over statistical baselines), forecasts cargo requirement from consumption and stock, and estimates voyage time and port waiting. A mixed-integer optimisation model then recommends a joint procurement and chartering plan (quantity, origin, laycan window, vessel size, charter type, discharge port) that minimises total landed logistics cost across forecast scenarios. The prototype will be validated by walk-forward backtesting against simple rule-based policies, measuring forecast error, interval coverage, cost, stock-out and demurrage days.

## Description (4632 chars)

```
PROBLEM
Organisations importing bulk cargo (for example coking coal, thermal coal or fertiliser raw materials) to East Coast ports such as Paradip, Visakhapatnam, Haldia and Dhamra face two linked decisions. Procurement decides how much cargo to buy, from which origin and when. Chartering decides which vessel size, which charter type (voyage, time charter or contract of affreightment) and which loading window. Today these are often planned separately. Dry bulk freight rates can move sharply within weeks, so fixing a vessel too early or too late is expensive. Buying cargo without a matching vessel plan leads to rushed spot fixtures, and poor timing against port congestion or the cyclone and monsoon season leads to waiting time, demurrage or stock-outs at the plant.

PROPOSED SOLUTION: NauPlan
NauPlan is a decision-support system that turns freight and demand forecasts into a joint procurement and chartering plan. It has four modules.

1. Data layer
Market data: dry bulk freight index history by vessel class (Baltic Exchange, licence needed for production use), bunker fuel prices, commodity prices (World Bank Pink Sheet), USD/INR reference rate (RBI). Operational data from the user organisation: daily consumption, stock levels, supply contracts, past charter fixtures, voyage times and demurrage records. Port and weather data: historical waiting and berthing times, draft limits, marine weather (Open-Meteo Marine API) and IMD cyclone bulletins.

2. Forecasting engine
a) Freight rates for each relevant vessel class over a 1 to 12 week horizon. Statistical baselines (seasonal naive, SARIMAX) are compared with LightGBM using lagged rates, bunker prices, commodity prices and seasonality. Quantile regression gives P10, P50 and P90 bands, not a single number.
b) Cargo requirement from consumption forecasts, current stock, stock in transit and safety stock policy.
c) Voyage time and expected port waiting by port and season, used to set realistic arrival windows.

3. Optimisation engine
A mixed-integer linear programme (Python, PuLP or OR-Tools with an open-source solver) chooses purchase quantity and timing, origin, vessel class, charter type, laycan window and discharge port. The objective is total landed logistics cost: freight, demurrage, inventory holding and a stock-out penalty. Constraints include safety stock, port draft and berth limits, vessel sizes and contract minimums. The plan is evaluated across scenarios sampled from the forecast bands, reporting expected cost and a downside-risk measure (CVaR), so the user can choose a cautious or cost-focused plan.

4. Planner dashboard
A web dashboard shows freight forecast fan charts, a procurement and shipment calendar, a "fix now or wait" recommendation with expected saving and risk, stock projections and alerts for congestion or cyclone risk. Key drivers behind each forecast are shown using SHAP so planners can see why a recommendation was made. Plans are re-run every week with new data (rolling horizon), and the planner always approves the final decision.

WHAT MAKES IT DIFFERENT
Most tools forecast freight or plan procurement in isolation. NauPlan links them in one loop: forecast uncertainty feeds directly into the optimisation, and the output is a concrete, explainable action with a cost and risk estimate rather than a price prediction alone.

FEASIBILITY
Status: proposed solution; no prototype has been built yet. In the hackathon we will build the full pipeline for one commodity and one or two import routes to an East Coast port, using public market data where licences permit and clearly labelled synthetic data for consumption, stock and contracts. All core tools are open source (Python, pandas, LightGBM, statsmodels, PuLP or OR-Tools, FastAPI, React). Features needing industry partnership are separated out: licensed route-level freight assessments, broker fixture data, AIS vessel tracking, berth-level port data and integration with the organisation's ERP.

VALIDATION
Forecasts: walk-forward backtesting with MAPE, MASE, pinball loss, prediction interval coverage and directional accuracy against the baselines. Decisions: replaying historical periods and comparing NauPlan's plan with simple rule-based policies (fixed lead-time fixing, buy-when-needed) on total cost, stock-out days and demurrage days. We will report measured results only after these tests.

EXPECTED IMPACT
Better-timed fixtures and purchases, fewer rushed spot charters, lower demurrage and inventory cost, and fewer stock-outs. Planners get a transparent, data-based view of freight and supply risk instead of relying on judgement alone.
```

## Technology bucket

AI/ML, Cloud Computing, Blockchain
