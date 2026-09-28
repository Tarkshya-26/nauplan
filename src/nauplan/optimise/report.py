"""`nauplan plan`: vessel recommendations, strategy comparison, recommended plan and sensitivity."""
from __future__ import annotations

import copy
import json
from datetime import UTC, datetime

import pandas as pd

from nauplan.config import PROCESSED, ROOT
from nauplan.forecast.run import _md
from nauplan.optimise.model import Programme, solve
from nauplan.optimise.scenarios import hire_multipliers
from nauplan.vessels import assumptions, recommend

PROGRAMME = ROOT / "config" / "synthetic_programme.toml"


def _strategies(prog, a, mult):
    lam = a["risk"]["risk_weight"]
    return [
        solve(prog, a, 0.0, ("spot",), mult, "all spot (current practice)"),
        solve(prog, a, 0.0, ("spot", "tc", "coa"), mult, "optimised, expected cost only"),
        solve(prog, a, lam, ("spot", "tc", "coa"), mult, f"optimised, risk-aware (weight {lam})"),
    ]


def _sensitivity(prog, a, mult) -> pd.DataFrame:
    rows = []
    for prem in (0.0, 0.05, 0.10):
        for lam in (0.0, a["risk"]["risk_weight"]):
            b = copy.deepcopy(a)
            b["contracts"]["period_premium"] = prem
            p = solve(prog, b, lam, ("spot", "tc", "coa"), mult)
            s = p.summary(a["risk"]["cvar_alpha"])
            rows.append({"period_premium": prem, "risk_weight": lam,
                         "expected_usd_m": s["expected_cost_usd_m"], "cvar_usd_m": s["cvar_usd_m"],
                         "tc_vessel_months": sum(t["vessels"] * t["months"] for t in p.time_charters),
                         "coa_kt": sum(c["tonnes"] for c in p.coa) / 1000})
    return pd.DataFrame(rows)


def plan_report(programme_path=PROGRAMME) -> str:
    a = assumptions()
    prog = Programme.load(programme_path)
    mult = hire_multipliers(prog.months, a["risk"]["scenarios"], a["risk"]["seed"])
    alpha = a["risk"]["cvar_alpha"]
    plans = _strategies(prog, a, mult)
    best = plans[-1]
    comp = pd.DataFrame([p.summary(alpha) for p in plans]).drop(columns="status")
    sens = _sensitivity(prog, a, mult)

    parts = [
        "# Charter plan (example)",
        (f"Generated {datetime.now(UTC).date()} by `uv run nauplan plan`. **The cargo programme is synthetic** "
         "(config/synthetic_programme.toml) and fuel, port, waiting and contract parameters are placeholders "
         "(config/assumptions.toml). Vessel specs are Baltic standard vessels; today's hire is converted from "
         f"the Baltic indices ({a['market']['index_date_note']}). Treat money figures as illustrative."),
        (f"{a['risk']['scenarios']} hire scenarios over {prog.months} months, resampled from real 4-week moves of "
         "the BDRY freight proxy and scaled so expected hire equals today's. CVaR = average cost of the worst "
         f"{1 - alpha:.0%} of scenarios."),
        "## Vessel choice per route (today's hire)",
    ]
    for route in prog.routes:
        rec = recommend(route["origin"], route["destination"], a)
        cols = ["vessel_class", "discharge_at", "feasible", "cargo_t", "laden_draft_m", "route",
                "round_trip_days", "spot_usd_per_t", "why"]
        parts += [f"### {route['origin']} > {route['destination']}", _md(rec[cols].fillna(""))]
    parts += ["## Strategies compared", _md(comp.round(2)),
              f"## Recommended plan: {best.label}", "### Period time charters",
              _md(pd.DataFrame(best.time_charters).fillna("")) if best.time_charters else "None.",
              "### COA liftings",
              _md(pd.DataFrame(best.coa).round(1)) if best.coa else "None.",
              "### Expected shipments by month and mode (tonnes)",
              _md(best.shipments.pivot_table(index="month", columns="mode", values="tonnes", aggfunc="sum")
                  .fillna(0).round(0).reset_index()),
              "### Chartered fleet use (vessel-days, scenario average)",
              _md(best.fleet.round(1)) if best.fleet is not None and len(best.fleet) else "No chartered fleet.",
              "## Sensitivity: period hire premium vs today's spot",
              _md(sens.round(2))]
    path = ROOT / "reports" / "plan_example.md"
    path.write_text("\n\n".join(parts) + "\n")

    PROCESSED.mkdir(parents=True, exist_ok=True)
    (PROCESSED / "plan.json").write_text(json.dumps({
        "synthetic_programme": True,
        "strategies": comp.to_dict(orient="records"),
        "recommended": {"label": best.label, "time_charters": best.time_charters, "coa": best.coa,
                        "shipments": best.shipments.to_dict(orient="records"),
                        "fleet": best.fleet.to_dict(orient="records") if best.fleet is not None else []},
        "sensitivity": sens.to_dict(orient="records"),
    }, indent=2, default=str))
    return str(path)
