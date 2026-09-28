"""Two-stage stochastic MILP for the chartering plan.

First stage (decided now, same in every scenario):
  * period time charters: how many vessels of each class, starting which month, for 3 or 6 months.
    Fixing in month 0 locks today's hire; a later start pays the market hire of that month.
  * COA liftings: tonnes per route and month at a fixed $/t agreed now.
Second stage (per freight scenario):
  * how many tonnes go on chartered ships vs spot voyages, and how many idle chartered
    vessel-days are relet to the market.

Objective: expected cost + risk_weight * CVaR (Rockafellar-Uryasev), over hire scenarios.
Units inside the model: kilotonnes and US$ million, for numerical conditioning.
"""
from __future__ import annotations

import math
import tomllib
from dataclasses import dataclass, field

import numpy as np
import pandas as pd
import pulp

from nauplan.optimise.scenarios import hire_multipliers
from nauplan.vessels import DISCHARGE_OPTIONS, Voyage, assumptions, vessel_specs, voyage

TC_LENGTHS = (3, 6)
COA_LENGTHS = (3, 6)


@dataclass
class Programme:
    start_month: str
    months: int
    routes: list[dict]

    @classmethod
    def load(cls, path) -> Programme:
        with open(path, "rb") as f:
            raw = tomllib.load(f)
        return cls(raw["start_month"], raw["months"], raw["route"])

    def label(self, r: int) -> str:
        return f"{self.routes[r]['origin']} > {self.routes[r]['destination']}"

    def month_label(self, m: int) -> str:
        return str(pd.Period(self.start_month, "M") + m)


@dataclass
class Option:
    """A feasible way to ship route r with vessel class vc (best discharge option at today's hire)."""
    r: int
    vc: str
    voyage: Voyage

    @property
    def days_per_kt(self) -> float:
        return self.voyage.total_days / self.voyage.cargo_t * 1000

    def running_cost_per_kt(self) -> float:  # $M per kt when carried on our own chartered ship
        return self.voyage.variable_cost_usd() / self.voyage.cargo_t / 1000

    def spot_per_kt(self, hire: float) -> float:  # $M per kt
        return self.voyage.spot_freight_per_t(hire) / 1000


def build_options(prog: Programme, a: dict) -> list[Option]:
    hire = a["market"]["spot_hire_usd_per_day"]
    opts = []
    for r, route in enumerate(prog.routes):
        for vc in vessel_specs().index:
            best = None
            for dis in DISCHARGE_OPTIONS.get(route["destination"], (route["destination"],)):
                _, vy = voyage(vc, route["origin"], route["destination"], dis, a)
                if vy and (best is None or vy.spot_freight_per_t(hire[vc]) < best.spot_freight_per_t(hire[vc])):
                    best = vy
            if best:
                opts.append(Option(r, vc, best))
    return opts


@dataclass
class Plan:
    label: str
    status: str
    risk_weight: float
    allowed: tuple[str, ...]
    scenario_costs_usd: np.ndarray
    total_tonnes: float
    time_charters: list[dict] = field(default_factory=list)
    coa: list[dict] = field(default_factory=list)
    shipments: pd.DataFrame | None = None  # expected tonnes by month, route, class, mode
    fleet: pd.DataFrame | None = None  # expected use of chartered vessels by class and month

    def summary(self, alpha: float) -> dict:
        c = np.sort(self.scenario_costs_usd)
        tail = c[math.floor(alpha * len(c)):]
        return {
            "plan": self.label, "status": self.status,
            "expected_cost_usd_m": c.mean() / 1e6,
            "cvar_usd_m": tail.mean() / 1e6,
            "p90_usd_m": float(np.quantile(c, 0.9)) / 1e6,
            "std_usd_m": c.std() / 1e6,
            "expected_usd_per_t": c.mean() / self.total_tonnes,
        }


def solve(prog: Programme, a: dict | None = None, risk_weight: float | None = None,
          allowed: tuple[str, ...] = ("spot", "tc", "coa"), mult: np.ndarray | None = None,
          label: str = "", time_limit: int = 120) -> Plan:
    a = a or assumptions()
    ct, rk = a["contracts"], a["risk"]
    lam = rk["risk_weight"] if risk_weight is None else risk_weight
    alpha, D, M = rk["cvar_alpha"], ct["days_per_month"], prog.months
    if mult is None:
        mult = hire_multipliers(M, rk["scenarios"], rk["seed"])
    S = mult.shape[0]
    hire = a["market"]["spot_hire_usd_per_day"]
    opts = build_options(prog, a)
    demand = [[t / 1000 for t in route["tonnes_per_month"]] for route in prog.routes]  # kt
    for r in range(len(prog.routes)):
        if not any(o.r == r for o in opts):
            raise ValueError(f"no feasible vessel class for {prog.label(r)}")
    classes = sorted({o.vc for o in opts})
    lp = pulp.LpProblem("charter_plan", pulp.LpMinimize)

    # ---- first stage
    tc = {}
    if "tc" in allowed:
        for vc in classes:
            need = max(sum(demand[o.r][m] * o.days_per_kt for o in opts if o.vc == vc) for m in range(M))
            ub = math.ceil(need / D) + 1
            for L in TC_LENGTHS:
                for m0 in range(M - L + 1):
                    tc[vc, m0, L] = pulp.LpVariable(f"tc_{vc[:4]}_{m0}_{L}", lowBound=0, upBound=ub, cat="Integer")
    coa = {}
    if "coa" in allowed:
        for i, o in enumerate(opts):
            for L in COA_LENGTHS:
                for m in range(min(L, M)):
                    coa[i, L, m] = pulp.LpVariable(f"coa_{i}_{L}_{m}", lowBound=0, upBound=demand[o.r][m])
    fleet = {(vc, m): pulp.lpSum(x for (c, m0, L), x in tc.items() if c == vc and m0 <= m < m0 + L)
             for vc in classes for m in range(M)}

    # ---- second stage and scenario costs
    y_tc, y_sp, relet, cost_expr = {}, {}, {}, []
    for s in range(S):
        cost = []
        for (vc, m0, L), x in tc.items():
            cost.append(hire[vc] * (1 + ct["period_premium"]) * mult[s, m0] * D * L / 1e6 * x)
        for (i, _L, _m), w in coa.items():
            cost.append(opts[i].spot_per_kt(hire[opts[i].vc]) * (1 + ct["coa_premium"]) * w)
        for m in range(M):
            for i, o in enumerate(opts):
                y_sp[s, i, m] = pulp.LpVariable(f"sp_{s}_{i}_{m}", lowBound=0)
                cost.append(o.spot_per_kt(hire[o.vc] * mult[s, m]) * y_sp[s, i, m])
                if tc:
                    y_tc[s, i, m] = pulp.LpVariable(f"tcu_{s}_{i}_{m}", lowBound=0)
                    cost.append(o.running_cost_per_kt() * y_tc[s, i, m])
            for r in range(len(prog.routes)):
                lp += (pulp.lpSum(y_sp[s, i, m] + y_tc.get((s, i, m), 0) for i, o in enumerate(opts) if o.r == r)
                       + pulp.lpSum(w for (i, _L, mm), w in coa.items() if mm == m and opts[i].r == r)
                       == demand[r][m])
            if tc:
                for vc in classes:
                    relet[s, vc, m] = pulp.LpVariable(f"rl_{s}_{vc[:4]}_{m}", lowBound=0)
                    cost.append(-hire[vc] * mult[s, m] * (1 - ct["relet_discount"]) / 1e6 * relet[s, vc, m])
                    lp += (pulp.lpSum(y_tc[s, i, m] * o.days_per_kt for i, o in enumerate(opts) if o.vc == vc)
                           + relet[s, vc, m] <= D * fleet[vc, m])
        cost_expr.append(pulp.lpSum(cost))

    eta = pulp.LpVariable("eta")
    u = [pulp.LpVariable(f"u_{s}", lowBound=0) for s in range(S)]
    for s in range(S):
        lp += u[s] >= cost_expr[s] - eta
    lp += pulp.lpSum(cost_expr) / S + lam * (eta + pulp.lpSum(u) / ((1 - alpha) * S))
    lp.solve(pulp.HiGHS(msg=False, timeLimit=time_limit, gapRel=1e-4))

    # ---- read back
    costs = np.array([pulp.value(e) * 1e6 for e in cost_expr])
    plan = Plan(label or "+".join(allowed), pulp.LpStatus[lp.status], lam, allowed, costs,
                sum(map(sum, demand)) * 1000)
    for (vc, m0, L), x in tc.items():
        n = round(x.value() or 0)
        if n:
            plan.time_charters.append({
                "vessel_class": vc, "vessels": n, "start": prog.month_label(m0), "months": L,
                "hire": "fixed now at today's rate" if m0 == 0 else "market rate at start",
                "hire_usd_day": hire[vc] * (1 + ct["period_premium"]) if m0 == 0 else None,
            })
    for (i, L, m), w in coa.items():
        if (w.value() or 0) > 1e-6:
            o = opts[i]
            plan.coa.append({"route": prog.label(o.r), "vessel_class": o.vc, "months": L,
                             "month": prog.month_label(m), "tonnes": w.value() * 1000,
                             "usd_per_t": o.spot_per_kt(hire[o.vc]) * (1 + ct["coa_premium"]) * 1000})
    rows = []
    for m in range(M):
        for i, o in enumerate(opts):
            sp = np.mean([y_sp[s, i, m].value() or 0 for s in range(S)]) * 1000
            tcv = np.mean([(y_tc[s, i, m].value() or 0) for s in range(S)]) * 1000 if tc else 0.0
            co = sum((w.value() or 0) for (j, _L, mm), w in coa.items() if j == i and mm == m) * 1000
            for mode, t in (("spot", sp), ("time charter", tcv), ("COA", co)):
                if t > 1:
                    rows.append({"month": prog.month_label(m), "route": prog.label(o.r), "vessel_class": o.vc,
                                 "discharge_at": o.voyage.discharge_at, "mode": mode, "tonnes": t})
    plan.shipments = pd.DataFrame(rows)
    if tc:
        frows = []
        for vc in classes:
            for m in range(M):
                n = pulp.value(fleet[vc, m]) or 0
                if n < 0.5:
                    continue
                used = np.mean([sum((y_tc[s, i, m].value() or 0) * o.days_per_kt
                                    for i, o in enumerate(opts) if o.vc == vc) for s in range(S)])
                rl = np.mean([relet[s, vc, m].value() or 0 for s in range(S)])
                frows.append({"vessel_class": vc, "month": prog.month_label(m), "vessels": round(n),
                              "vessel_days": round(n) * D, "voyage_days": used, "relet_days": rl,
                              "idle_days": max(0.0, round(n) * D - used - rl)})
        plan.fleet = pd.DataFrame(frows)
    return plan
