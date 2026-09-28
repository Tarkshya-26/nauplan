# Demo walkthrough for the judges

SIH26006, team Vector66. A 7-minute live demo of the NauPlan dashboard, a 90-second fallback, and answers to the questions judges are likely to ask.

Two roles: the **speaker** talks to the judges, the **driver** clicks. Swap halfway if you like, but decide beforehand. Numbers below are as of 28 Sep 2026; re-read them from the screen during the checklist, because they change when the data is refreshed.

## Before the demo

Night before (needs internet):

```bash
uv run nauplan fetch
uv run nauplan forecast
cd web && npm run build && cd ..
```

On the day, 15 minutes before:

1. `uv run nauplan serve`, then open http://127.0.0.1:8000 in Chrome, full screen, zoom 100% on a 1440 px or wider window.
2. Wait for the hero card to show the recommended plan (about 2 seconds). If it says "Plan unavailable", restart the server.
3. Write today's numbers into the blanks in this script: the hero headline, the two worst-10% figures, the Paradip cheapest $/t.
4. Reload the page once more so the import plan shows the example figures and the sliders are back to default.
5. Have the backup ready in another tab or window: `submission/SIH2026_NauPlan_Vector66.pdf` and the two screenshots in `submission/`. A 2-minute screen recording made the night before is the best backup.

Do not run `nauplan fetch` right before the demo: the numbers will move away from what you rehearsed.

If there is no internet at the venue the app still runs; only the Google fonts fall back to system fonts.

## The 7-minute walkthrough

### 0:00 Open on the problem (30 s)

**Screen:** top of the page, hero visible.

**Say:** "SAIL imports coal for its steel plants through seven East Coast ports, and today most ships are fixed one at a time on the daily spot market. The problem statement asks for a move to short and medium term contracts: when to fix, which ship, and how to avoid idle time. NauPlan is a working prototype that does that, on real port data."

### 0:30 The answer first: the hero (60 s)

**Screen:** the recommendation card over the chart.

**Say:** "This is what a chartering manager sees on Monday morning. For the example import plan, the recommendation is: *fix 14 Panamax on 6-month charters now, plus 170 thousand tonnes on COA* [read today's headline]. The average cost in the worst 10% of freight markets falls from *$128.9M to $98.5M* [read], and the expected cost barely moves. The chart behind it shows the actual sea routes from the load ports in Australia, the US, Mozambique, Russia and Indonesia to our seven ports."

**Point at:** the magenta list of East Coast ports, then the tracks around the north of New Guinea. "Deep-laden ships from Queensland can't use Torres Strait, which is limited to 12.5 m, so the model routes them the long way. That adds about 900 nautical miles."

**Say, once:** "The import plan is example data and some costs are placeholders; the badge says so. The port limits, ship specs and market hire are real and cited."

### 1:30 Which ship fits this route? (90 s)

**Driver:** click **Vessel check** in the top bar. Leave Hay Point to Paradip selected.

**Say:** "Every Baltic standard ship is checked against the length, beam, size and draft limits at both ends. The magenta line is Paradip's 16.5 m draft limit."

**Point at:**
- Handysize, greyed out: "Hay Point's Dalrymple Bay terminal only takes ships of 40,000 deadweight tonnes and up, so the Handysize cannot call."
- Capesize, risen above its red waterline: "A full Capesize draws 18.2 m, so it has to leave cargo behind: about 21 thousand tonnes shut out. The model says it can carry 153,810 tonnes. On 6 September the first 16.5 m Capesize at Paradip, from Hay Point, carried 152,702 tonnes. We are within 1% of a real call."
- Top right: "At today's Baltic hire the cheapest is Panamax at *$23.78* a tonne [read], because Capesize hire is more than double Panamax right now."

**Driver:** change the discharge port to **Haldia Dock Complex** and the load port to **Tanjung Bara** (Indonesia).

**Say:** "Haldia is a river port, about 9 m draft and 230 m length inside the lock. Only a part-loaded Handysize fits. The model also offers discharging at Sandheads anchorage and moving the coal by barge, and a Panamax doing that is cheaper per tonne. Every reason is written out in the table."

### 3:00 Freight outlook, and an honest finding (60 s)

**Driver:** click **Outlook**.

**Say:** "We tested six forecasting models, from 'no change' to LightGBM, walking forward through 2021 to 2026 and only using data available on each date. None beat 'no change' on the direction of freight. Freight futures already price in what's public, so nobody can promise that. What we can do is give honest ranges. The shaded band is where the price should land 8 times in 10, and the table shows it did: 85 to 91% on the volatility-scaled version."

**Driver:** toggle to **Range scaled to today's volatility**.

**Say:** "The market is calm right now, quieter than 95% of weeks since 2018, so the band is narrower. The optimiser plans against these ranges instead of a single guess."

### 4:00 Build the charter plan, live (2 min)

**Driver:** click **Charter plan**. Scroll so the import plan table and the three result cards are on screen.

**Say:** "This is the monthly import plan: load port, discharge port, thousand tonnes per month. The optimiser tries every mix of spot voyages, 3 and 6 month time charters and COAs against 200 freight scenarios drawn from real market moves."

**Point at:** the three cards, then the histogram. "Grey is all spot, today's practice: the cost could land anywhere from under $80M to over $150M. Blue is the plan: a narrow spike. We don't claim a big average saving; with no view on direction, contracts mostly buy certainty. That is exactly the case for moving off spot."

**Driver:** scroll to **What to fix and when**. **Say:** "14 Panamax fixed now for 6 months at today's hire, one more in November at whatever the market is then, and COA volume on Hay Point."

**Driver:** scroll to **Chartered ship days**. **Say:** "November and February are light months. Instead of leaving ships idle, the plan relets the spare days to the market. That is the idle-time ask in the problem statement."

**Live change:** drag **Period hire vs today's spot** to **+10%** and click **Optimise plan** (about 2 seconds).

**Say while it runs:** "What if owners want 10% over spot for period charters?" Then: "The plan switches to COAs instead: *$102.0M* expected, and the worst case is still far below all spot. Management can see the price of certainty before committing."

Optional if time allows: set **Weight on bad-case cost** to 0 and optimise again. "With no weight on bad outcomes, the plan takes more spot risk. The manager chooses the risk appetite; the model shows the consequence."

### 6:00 Early warnings (40 s)

**Driver:** click **Warnings**.

**Say:** "Sea state off each port from wave data, against the usual level for this month. Right now *Dhamra and Gopalpur* [read] are above their usual September swell, which slows cargo work and pilot boarding. And the tool lists what data is still missing, so nobody trusts a number that isn't backed."

### 6:40 Close (20 s)

**Say:** "So: which ship fits, what to fix and when, what it costs in a bad market, and what could disrupt it, all traceable to sources. Plug in SAIL's import plan, fixture history and cost data and the same pipeline gives a real plan. The code, method notes and backtest report are public on GitHub."

## 90-second fallback

If the app fails or time is cut, open the deck PDF at slide 3 (screenshots) and say:

"NauPlan is a working prototype for SAIL's move from spot to contract chartering. It checks every ship class against the draft, length and beam limits at 19 cited ports: for Hay Point to Paradip it loads a Capesize to 153,810 tonnes against 152,702 on a real call. We backtested six freight forecasting models; none beat 'no change' on direction, so we plan on honest ranges. A stochastic optimiser then picks spot, time charter or COA across 200 freight scenarios. On an example plan, the worst-case cost fell from $128.9M to $98.5M. Spare charter days are relet, and the dashboard warns of swell and volatility."

## Likely questions

**How accurate is your freight forecast?**
We tested six models on 2021 to 2026 data, walking forward. None reliably beat "no change" on direction, which is expected for a futures-based price. Our ranges are calibrated: the volatility-scaled 80% range held 84 to 91% of outcomes in 2024 to 2026. With licensed per-class rates and the FFA forward curve, the centre forecast becomes the market's own forward price.

**Is the data real?**
Port limits come from port authority and terminal documents, each stored with its source and date. Ship specs and the formula linking hire to freight are from the Baltic Exchange's Guide to Market Benchmarks. Hire per class is converted from the Baltic indices. The import plan is example data and fuel, port and waiting costs are placeholders, labelled on screen and in the config.

**Why Panamax and not Capesize?**
Right now Capesize hire is about $52,500 a day against about $21,700 for Panamax, and Paradip's draft forces a Capesize to leave around 21,000 tonnes behind. When Capesize hire falls, the ranking changes; the model recalculates.

**What is CVaR?**
The average cost in the worst 10% of scenarios. We minimise expected cost plus a weight on that, and the manager sets the weight.

**How is this better than a spreadsheet?**
It links three things a spreadsheet keeps apart: freight uncertainty, port limits at both ends, and the chartered fleet's use month by month. It tests every contract mix against 200 scenarios in seconds and explains each ship choice.

**What about port congestion and demurrage?**
Waiting days are a placeholder today. We found free daily feeds, Haldia's daily berth position and Paradip's daily traffic report, and parsing them into waiting-time estimates is the next step.

**What if the Red Sea or Suez closes?**
The model has an avoid-Suez setting that reroutes via the Cape: Hampton Roads to Dhamra on a Panamax goes from about $37.8 to $45.7 a tonne. It is a configuration flag today, not yet a dashboard button.

**Cyclones?**
Wave data for all seven ports is in. IMD cyclone bulletins are not yet integrated.

**How would SAIL deploy it?**
It runs on one server or a laptop: FastAPI backend, React dashboard, open-source solver. SAIL would load its import plan, past fixtures and cost data, and ideally a Baltic Exchange licence for per-class rates, for example the S8 route from Indonesia to East Coast India.

**How do you know the optimiser is right?**
Tests check that every plan ships exactly the import plan, that contracts never worsen the risk-adjusted cost against all spot, and that the model's cost identities hold. The plan and all-spot are compared on the same 200 scenarios.

**How long does it take to run?**
About 2 seconds for a 6-month plan with 200 scenarios on a laptop.

## Things not to say

- Don't claim the forecast predicts freight direction, or quote a saving as SAIL's real saving: the money figures come from an example plan.
- Don't call the cost figures market data; say "placeholder" if asked.
- Don't promise cyclone or congestion features as working; they are next steps.
