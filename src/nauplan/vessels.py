"""Vessel-port fit and voyage economics (problem statement ask b).

For a vessel class on an origin -> destination route this module:
  * checks LOA, beam and minimum size against the best coal berth at both ports,
  * cuts cargo where a port's draft limit is below the vessel's design draft (using TPC),
  * picks the sea route allowed by the laden draft (Torres Strait max 12.5 m),
  * prices the round voyage with the Baltic TCE relation (GMB v8.7, Appendix 3).

Parameters marked PLACEHOLDER in config/assumptions.toml drive the money figures.
"""
from __future__ import annotations

import math
import tomllib
from dataclasses import dataclass, field
from functools import lru_cache

import pandas as pd

from nauplan.config import REFERENCE, ROOT
from nauplan.reference import berths, passages, ports
from nauplan.routing import distances

# Hay Point sailing draft rule from the DBCT Terminal Information Booklet (Rev 21.0):
# max draft = (channel depth + tide - 1) / 1.05
TIDAL_RULES = {"hay_point": lambda depth, tide: (depth + tide - 1) / 1.05}

# Discharge alternatives: Haldia's river draft can be bypassed by transloading at Sandheads.
DISCHARGE_OPTIONS = {"haldia": ("haldia", "sandheads")}


@lru_cache
def assumptions(path: str | None = None) -> dict:
    with open(path or ROOT / "config" / "assumptions.toml", "rb") as f:
        return tomllib.load(f)


def vessel_specs() -> pd.DataFrame:
    return pd.read_csv(REFERENCE / "vessel_specs.csv").set_index("vessel_class")


def _num(x) -> float | None:
    return None if x is None or (isinstance(x, float) and math.isnan(x)) else float(x)


@dataclass
class PortLimit:
    port_id: str
    berth: str
    draft_m: float | None
    draft_basis: str
    loa_m: float | None = None
    beam_m: float | None = None
    max_dwt_t: float | None = None
    min_dwt_t: float | None = None
    transloading: bool = False


def port_limit(port_id: str, a: dict | None = None) -> PortLimit:
    """Limits of the most capable coal berth at a port (the one allowing the deepest draft)."""
    a = a or assumptions()
    if ports().set_index("port_id").loc[port_id, "operation"] == "transloading":
        return PortLimit(port_id, "anchorage", None, "anchorage, draft not binding", transloading=True)
    best = None
    for _, r in berths()[berths()["port_id"] == port_id].iterrows():
        depth = _num(r["water_depth_m"])
        if _num(r["max_draft_m"]) is not None:
            d, basis = float(r["max_draft_m"]), "published limit"
        elif port_id in TIDAL_RULES and depth is not None:
            tide = a["tidal"]["hay_point_planning_tide_m"]
            d, basis = TIDAL_RULES[port_id](depth, tide), f"tidal rule, {tide} m tide assumed"
        elif depth is not None:
            f = a["voyage"]["depth_to_draft_factor"]
            d, basis = depth / f, f"water depth / {f}, assumed"
        else:
            d, basis = None, "draft limit not sourced"
        cand = PortLimit(port_id, r["berth"], d, basis, _num(r["max_loa_m"]), _num(r["max_beam_m"]),
                         _num(r["max_dwt_t"]), _num(r["min_dwt_t"]))
        if best is None or (d or 0) > (best.draft_m or 0):
            best = cand
    return best


@dataclass
class Fit:
    vessel_class: str
    origin: str
    discharge_at: str
    feasible: bool
    cargo_t: float
    laden_draft_m: float
    reasons: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def fit(vessel_class: str, origin: str, discharge_at: str, a: dict | None = None) -> Fit:
    a = a or assumptions()
    v = vessel_specs().loc[vessel_class]
    intake = v.dwt_t * (1 - a["voyage"]["non_cargo_share"])
    cargo, feasible, reasons, warnings = intake, True, [], []
    for pid in (origin, discharge_at):
        lim = port_limit(pid, a)
        if lim.transloading:
            continue
        if lim.loa_m is not None and v.loa_m > lim.loa_m:
            feasible = False
            reasons.append(f"LOA {v.loa_m:g} m exceeds {lim.loa_m:g} m at {pid}")
        if lim.beam_m is not None and v.beam_m > lim.beam_m:
            feasible = False
            reasons.append(f"beam {v.beam_m:g} m exceeds {lim.beam_m:g} m at {pid}")
        if lim.min_dwt_t is not None and v.dwt_t < lim.min_dwt_t:
            feasible = False
            reasons.append(f"{v.dwt_t:,.0f} DWT is below the {lim.min_dwt_t:,.0f} DWT minimum at {pid}")
        if lim.draft_m is None:
            warnings.append(f"draft limit at {pid} not sourced")
        elif lim.draft_m < v.draft_ssw_m:
            cut = (v.draft_ssw_m - lim.draft_m) * 100 * v.tpc_t_per_cm
            if intake - cut < cargo:
                cargo = intake - cut
                reasons.append(f"draft {lim.draft_m:.2f} m at {pid} ({lim.draft_basis}) limits cargo")
        if lim.max_dwt_t is not None and cargo > lim.max_dwt_t:
            cargo = lim.max_dwt_t  # read as the largest parcel the port accepts
            reasons.append(f"cargo capped at {lim.max_dwt_t:,.0f} t at {pid}")
        if lim.loa_m is None:
            warnings.append(f"LOA limit at {pid} not sourced")
    if cargo < a["voyage"]["min_part_cargo_share"] * intake:
        feasible = False
        reasons.append(f"draft limits cut cargo to {cargo / intake:.0%} of intake")
    laden_draft = v.draft_ssw_m - (intake - cargo) / (100 * v.tpc_t_per_cm)
    return Fit(vessel_class, origin, discharge_at, feasible, max(cargo, 0.0), laden_draft, reasons, warnings)


@dataclass
class Voyage:
    vessel_class: str
    origin: str
    destination: str
    discharge_at: str
    variant: str
    distance_nm: float
    cargo_t: float
    laden_days: float
    ballast_days: float
    port_days: float
    fuel_usd: float
    port_costs_usd: float
    transload_usd: float
    commission: float

    @property
    def total_days(self) -> float:
        return self.laden_days + self.ballast_days + self.port_days

    def variable_cost_usd(self) -> float:
        """Voyage costs a charterer pays on top of hire when running its own chartered ship."""
        return self.fuel_usd + self.port_costs_usd + self.transload_usd

    def tc_cost_per_t(self, hire_usd_day: float) -> float:
        return (hire_usd_day * self.total_days + self.variable_cost_usd()) / self.cargo_t

    def spot_freight_per_t(self, hire_usd_day: float) -> float:
        """Voyage freight equivalent to a gross timecharter hire (Baltic TCE relation, inverted).

        Owner nets hire * (1 - commission) either way, so
        freight * cargo * (1 - c) = hire * (1 - c) * days + fuel + port costs.
        """
        c = self.commission
        freight = (hire_usd_day * (1 - c) * self.total_days + self.fuel_usd + self.port_costs_usd) / (1 - c)
        return (freight + self.transload_usd) / self.cargo_t


def _variant(laden_draft: float, a: dict) -> str:
    if a.get("routing", {}).get("avoid_suez", False):
        return "avoid_suez"
    torres = passages().set_index("passage").loc["torres_strait", "max_draft_m"]
    return "shortest" if laden_draft <= torres else "deep_draft"


def voyage(vessel_class: str, origin: str, destination: str, discharge_at: str | None = None,
           a: dict | None = None) -> tuple[Fit, Voyage | None]:
    a = a or assumptions()
    discharge_at = discharge_at or destination
    f = fit(vessel_class, origin, discharge_at, a)
    if not f.feasible:
        return f, None
    va, v = a["voyage"], vessel_specs().loc[vessel_class]
    variant = _variant(f.laden_draft_m, a)
    d = distances()
    dist = float(d[(d.origin == origin) & (d.destination == discharge_at) & (d.variant == variant)]["distance_nm"].iloc[0])
    sea = dist * (1 + va["sea_margin"]) / 24
    laden, ballast = sea / v.laden_speed_kn, sea / v.ballast_speed_kn
    transload = discharge_at != destination
    dis_rate = a["transloading"]["discharge_rate_t_per_day"] if transload else va["discharge_rate_t_per_day"]
    port = f.cargo_t / va["load_rate_t_per_day"] + f.cargo_t / dis_rate + va["wait_days_load"] + va["wait_days_discharge"]
    fuel_t = laden * v.laden_fuel_t_day + ballast * v.ballast_fuel_t_day + port * va["port_fuel_t_per_day"][vessel_class]
    return f, Voyage(
        vessel_class, origin, destination, discharge_at, variant, dist, f.cargo_t, laden, ballast, port,
        fuel_t * va["bunker_usd_per_t"], va["port_costs_usd_per_voyage"][vessel_class],
        a["transloading"]["extra_cost_usd_per_t"] * f.cargo_t if transload else 0.0, va["commission"],
    )


def recommend(origin: str, destination: str, a: dict | None = None) -> pd.DataFrame:
    """Every vessel class and discharge option for a route, ranked by spot cost per tonne at today's hire."""
    a = a or assumptions()
    hire = a["market"]["spot_hire_usd_per_day"]
    rows = []
    for vc in vessel_specs().index:
        for dis in DISCHARGE_OPTIONS.get(destination, (destination,)):
            f, vy = voyage(vc, origin, destination, dis, a)
            rows.append({
                "vessel_class": vc, "discharge_at": dis, "feasible": f.feasible, "cargo_t": round(f.cargo_t),
                "laden_draft_m": round(f.laden_draft_m, 2),
                "route": vy.variant if vy else None, "distance_nm": vy.distance_nm if vy else None,
                "round_trip_days": round(vy.total_days, 1) if vy else None,
                "spot_usd_per_t": round(vy.spot_freight_per_t(hire[vc]), 2) if vy else None,
                "why": "; ".join(f.reasons), "data_gaps": "; ".join(f.warnings),
            })
    out = pd.DataFrame(rows)
    return out.sort_values(["feasible", "spot_usd_per_t"], ascending=[False, True], na_position="last")
