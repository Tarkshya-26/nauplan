"""HTTP API for the dashboard. Run with `uv run nauplan serve`."""
from __future__ import annotations

import copy
import json
import re
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from nauplan import routing
from nauplan.config import PROCESSED, RAW, ROOT
from nauplan.forecast.metrics import summarise
from nauplan.forecast.panel import weekly_panel
from nauplan.optimise.model import Programme, solve
from nauplan.optimise.report import PROGRAMME
from nauplan.reference import ports
from nauplan.vessels import DISCHARGE_OPTIONS, assumptions, port_limit, recommend, vessel_specs

app = FastAPI(title="NauPlan API")


def _records(df: pd.DataFrame) -> list[dict]:
    return json.loads(df.to_json(orient="records"))


@lru_cache
def _placeholders() -> list[str]:
    text = (ROOT / "config" / "assumptions.toml").read_text()
    names = re.findall(r"^\s*\"?([\w/ ]+?)\"?\s*=.*#\s*PLACEHOLDER", text, flags=re.MULTILINE)
    tables = re.findall(r"^\[([\w.]+)\]\s*#\s*PLACEHOLDER", text, flags=re.MULTILINE)
    return names + tables


def _forecast() -> dict:
    path = PROCESSED / "forecast_latest.json"
    if not path.exists():
        from nauplan.forecast.run import latest_forecast
        latest_forecast()
    return json.loads(path.read_text())


def _backtest() -> list[dict]:
    path = PROCESSED / "backtest_predictions.parquet"
    if not path.exists():
        return []
    s = summarise(pd.read_parquet(path))
    s = s[s["model"].isin(["random_walk", "vol_random_walk", "arima", "lgbm_quantile"])]
    return _records(s[["period", "model", "horizon", "coverage_80", "pinball_vs_rw", "mae_vs_rw", "direction_hit"]])


def _sea_state() -> list[dict]:
    path = RAW / "marine.parquet"
    if not path.exists():
        return []
    m = pd.read_parquet(path).dropna(subset=["wave_height_max"])
    out = []
    for pid, g in m.groupby("port"):
        g = g.sort_values("date")
        last = g.iloc[-1]
        same_month = g[g["date"].dt.month == last["date"].month]["wave_height_max"]
        out.append({"port": pid, "date": str(last["date"].date()), "wave_m": float(last["wave_height_max"]),
                    "max_30d_m": float(g.tail(30)["wave_height_max"].max()),
                    "p90_month_m": float(same_month.quantile(0.9)),
                    "history_m": [round(float(x), 2) for x in g.tail(60)["wave_height_max"]]})
    return out


def _limit(pid: str) -> dict:
    lim = port_limit(pid)
    return {"port": pid, "berth": lim.berth, "draft_m": lim.draft_m, "draft_basis": lim.draft_basis,
            "loa_m": lim.loa_m, "beam_m": lim.beam_m, "max_dwt_t": lim.max_dwt_t, "min_dwt_t": lim.min_dwt_t,
            "transloading": lim.transloading}


@app.get("/api/overview")
def overview() -> dict:
    a = assumptions()
    panel = weekly_panel()
    hist = panel["bdry"].tail(160)
    p = ports()
    prog = Programme.load(PROGRAMME)
    return {
        "market": {"note": a["market"]["index_date_note"], "hire_usd_day": a["market"]["spot_hire_usd_per_day"]},
        "forecast": _forecast(),
        "history": [{"date": str(d.date()), "price": round(float(v), 2)} for d, v in hist.items()],
        "backtest": _backtest(),
        "ports": _records(p[["port_id", "name", "country", "role", "operation", "lat", "lon"]]),
        "limits": [_limit(pid) for pid in p["port_id"]],
        "vessels": _records(vessel_specs().reset_index()[["vessel_class", "baltic_standard", "dwt_t", "draft_ssw_m",
                                                          "loa_m", "beam_m", "tpc_t_per_cm"]]),
        "programme": {"synthetic": True, "start_month": prog.start_month, "months": prog.months,
                      "routes": prog.routes},
        "risk": a["risk"], "contracts": a["contracts"],
        "placeholders": _placeholders(),
        "sea_state": _sea_state(),
    }


@lru_cache(maxsize=256)
def _track(origin: str, destination: str, variant: str) -> list:
    p = ports().set_index("port_id")
    o, d = p.loc[origin], p.loc[destination]
    return routing.geometry((o.lon, o.lat), (d.lon, d.lat), variant)


@app.get("/api/tracks")
def tracks() -> list[dict]:
    """Voyage tracks for the chart: the programme routes plus every load port to Paradip."""
    prog = Programme.load(PROGRAMME)
    p = ports()
    pairs = {(r["origin"], r["destination"], "main") for r in prog.routes}
    pairs |= {(o, "paradip", "context") for o in p.loc[p.role == "load", "port_id"]}
    out = []
    for o, d, kind in sorted(pairs):
        dest = "sandheads" if d == "haldia" else d
        out.append({"origin": o, "destination": d, "kind": kind, "points": _track(o, dest, "deep_draft")})
    return out


class FitRequest(BaseModel):
    origin: str
    destination: str


@app.post("/api/fit")
def fit_route(req: FitRequest) -> dict:
    p = ports().set_index("port_id")
    for pid, role in ((req.origin, "load"), (req.destination, "discharge")):
        if pid not in p.index or p.loc[pid, "role"] != role:
            raise HTTPException(422, f"{pid} is not a known {role} port")
    rec = recommend(req.origin, req.destination)
    names = p["name"].to_dict()
    for col in ("why", "data_gaps"):  # show port names, not ids, in the reasons
        rec[col] = rec[col].apply(lambda s: re.sub(r"\b(" + "|".join(map(re.escape, names)) + r")\b",
                                                   lambda m: names[m.group(1)], s or ""))
    best = rec[rec.feasible].head(1)
    track = None
    if len(best):
        b = best.iloc[0]
        track = _track(req.origin, b.discharge_at, b.route)
    dis = DISCHARGE_OPTIONS.get(req.destination, (req.destination,))
    return {"options": _records(rec), "limits": {pid: _limit(pid) for pid in (req.origin, *dis)},
            "track": track}


class RouteIn(BaseModel):
    origin: str
    destination: str
    tonnes_per_month: list[float]


class PlanRequest(BaseModel):
    start_month: str = "2026-10"
    routes: list[RouteIn] = Field(min_length=1)
    risk_weight: float = Field(0.5, ge=0, le=5)
    period_premium: float = Field(0.0, ge=-0.3, le=0.5)
    scenarios: int = Field(200, ge=20, le=400)


@app.post("/api/plan")
def plan(req: PlanRequest) -> dict:
    months = {len(r.tonnes_per_month) for r in req.routes}
    if len(months) != 1 or not 3 <= months.pop() <= 12:
        raise HTTPException(422, "Every route needs the same number of months, between 3 and 12.")
    a = copy.deepcopy(assumptions())
    a["contracts"]["period_premium"] = req.period_premium
    a["risk"]["scenarios"] = req.scenarios
    prog = Programme(req.start_month, len(req.routes[0].tonnes_per_month), [r.model_dump() for r in req.routes])
    from nauplan.optimise.scenarios import hire_multipliers
    mult = hire_multipliers(prog.months, req.scenarios, a["risk"]["seed"])
    try:
        spot = solve(prog, a, 0.0, ("spot",), mult, "All spot (current practice)")
        best = solve(prog, a, req.risk_weight, ("spot", "tc", "coa"), mult, "NauPlan")
    except ValueError as e:
        raise HTTPException(422, str(e)) from e
    alpha = a["risk"]["cvar_alpha"]
    return {
        "strategies": [spot.summary(alpha), best.summary(alpha)],
        "costs_usd_m": {"spot": list(np.round(spot.scenario_costs_usd / 1e6, 3)),
                        "plan": list(np.round(best.scenario_costs_usd / 1e6, 3))},
        "time_charters": best.time_charters,
        "coa": best.coa,
        "shipments": _records(best.shipments) if best.shipments is not None and len(best.shipments) else [],
        "fleet": _records(best.fleet) if best.fleet is not None and len(best.fleet) else [],
        "months": [prog.month_label(m) for m in range(prog.months)],
        "alpha": alpha,
    }


DIST = ROOT / "web" / "dist"
if Path(DIST).exists():
    app.mount("/", StaticFiles(directory=DIST, html=True), name="web")
