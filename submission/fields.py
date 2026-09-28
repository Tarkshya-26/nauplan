TITLE = "NauPlan: Freight Forecast-Driven Charter Strategy for Bulk Cargo Imports to India's East Coast"

ABSTRACT = """SAIL charters vessels for coal imports to India's East Coast largely through daily spot fixtures, leaving costs exposed to volatile freight markets and port limits. NauPlan is a working prototype that plans the move to short and medium term multi-voyage contracts. It checks each Baltic standard vessel class against draft, LOA and beam limits at 7 East Coast and 12 load ports, every limit cited, and prices voyages with the Baltic timecharter-equivalent method. Freight ranges come from models tested by walk-forward backtest. A two-stage stochastic optimiser then chooses spot voyages, 3 or 6 month time charters or COAs, and when to fix them, across 200 freight scenarios, reletting idle chartered days. A dashboard shows the plan, the reason behind each ship choice, and early warnings for sea state and freight volatility. Real results need SAIL's import plan and cost data."""

DESCRIPTION = """PROBLEM
SAIL imports bulk cargo such as coal from Australia, the US, Mozambique, Russia and Indonesia to East Coast ports including Paradip, Vizag, Gangavaram, Gopalpur, Dhamra, Sagar-Sandheads and Haldia. Vessels are mostly fixed through daily engagement with the spot market. This misses good moments to lock in short or medium term contracts, and makes the vessel class choice (Handysize, Supramax, Panamax, Capesize) hard, because each port has its own draft, LOA and beam limits.

SOLUTION: NauPlan (working prototype)
A decision-support system that helps chartering managers move from single spot fixtures to planned multi-voyage contracts. Built so far:

1. Data pipeline
One command refreshes public data: a dry bulk freight futures proxy (BDRY), Brent crude and USD/INR (FRED), coal prices (World Bank) and daily sea state at all seven East Coast ports (Open-Meteo ERA5).

2. Ports and routes
Berth limits (draft, LOA, beam, size and, where published, handling rate) for the 7 East Coast ports and 12 load ports across all five origins, each value stored with its source document and date. Sea distances for every route in three variants: shortest, deep-draft (avoiding Torres Strait, max 12.5 m) and via the Cape of Good Hope.

3. Vessel and port fit
Baltic Exchange standard vessels are checked at both ends of a route. Where a port is shallower than the ship, cargo is cut using tonnes per centimetre until the ship floats at the limit. Voyages are priced with the Baltic timecharter-equivalent method at today's hire for each class. Check: for Hay Point to Paradip the model loads a Capesize to 153,810 t at Paradip's 16.5 m limit; the first such call, on 6 Sep 2026, carried 152,702 t.

4. Freight forecasting
Six models, from "no change" to LightGBM, were compared by walk-forward backtest on 2021 to 2026 data, using only information available at each date. No model reliably beat "no change" on direction, so NauPlan plans on calibrated P10 / P50 / P90 ranges rather than a single price. Volatility-scaled ranges held 84 to 91% of 2024 to 2026 outcomes against an 80% target.

5. Charter strategy optimiser
A two-stage stochastic mixed-integer programme (PuLP with the HiGHS solver) chooses how many time charters of each class to fix, for 3 or 6 months and starting when, plus COA volumes, with spot voyages for the rest. It is tested on 200 freight scenarios resampled from real market moves and balances expected cost against the worst 10% of outcomes (CVaR). Idle chartered days are relet to the market. On a synthetic 3.88 Mt six-month programme with placeholder costs, the plan cut the worst-10% cost from $128.9M (all spot) to $98.5M, with expected cost $98.3M against $99.6M.

6. Dashboard
FastAPI and React. The manager enters the monthly import plan, a risk weight and the period hire premium, and sees the recommended contracts, a timeline of what to fix and when, which ship fits each route and why, and early warnings for swell above the usual level at each port, freight volatility and missing data.

WHAT MAKES IT DIFFERENT
It links freight uncertainty, port limits at both ends and the chartered fleet's schedule in one model, and it is honest about what can be forecast. Every number traces to a cited source or a clearly labelled placeholder.

FEASIBILITY
Open-source stack that runs on a laptop; 37 automated tests; code public at github.com/Tarkshya-26/nauplan. Cost inputs (bunker price, port costs, waiting days) are placeholders and the cargo programme is synthetic until SAIL data is available. Licensed per-class and period freight rates (for example the Baltic S8 route, Indonesia to East Coast India) or SAIL's own fixture history plug into the same pipeline.

EXPECTED IMPACT
A proactive, auditable chartering strategy with lower exposure to freight swings, ships sized to each port's draft, fewer idle days, and early warning of disruptions."""

for n, v, lim in (("Title", TITLE, 100), ("Description", DESCRIPTION, 5000), ("Abstract", ABSTRACT, 1000)):
    print(n, len(v), "/", lim, "OK" if len(v) <= lim else "OVER", "dash!" if any(c in v for c in "–—") else "")
