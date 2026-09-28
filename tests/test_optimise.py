import copy

import numpy as np
import pandas as pd
import pytest

from nauplan.optimise.model import Programme, solve
from nauplan.optimise.scenarios import hire_multipliers
from nauplan.vessels import assumptions, fit, port_limit, recommend, vessel_specs, voyage


def test_min_dwt_rules_out_handysize_at_hay_point():
    f = fit("Handysize", "hay_point", "paradip")
    assert not f.feasible
    assert any("minimum" in r for r in f.reasons)


def test_capesize_cannot_berth_inside_haldia_but_can_use_sandheads():
    assert not fit("Capesize", "tanjung_bara", "haldia").feasible
    assert fit("Capesize", "tanjung_bara", "sandheads").feasible
    assert port_limit("sandheads").transloading


def test_draft_limit_cuts_cargo_by_tpc():
    a = assumptions()
    v = vessel_specs().loc["Capesize"]
    intake = v.dwt_t * (1 - a["voyage"]["non_cargo_share"])
    f = fit("Capesize", "vostochny", "paradip")  # Vostochny 16.0 m is tighter than Paradip 16.5 m
    assert f.cargo_t == pytest.approx(intake - (v.draft_ssw_m - 16.0) * 100 * v.tpc_t_per_cm)
    assert f.laden_draft_m == pytest.approx(16.0)


def test_deep_draft_ships_avoid_torres_strait():
    _, cape = voyage("Capesize", "hay_point", "paradip")
    _, handy = voyage("Handysize", "gladstone", "vizag")
    assert cape.variant == "deep_draft"
    assert handy.variant == "shortest"  # 10.5 m laden draft fits Torres Strait (12.5 m)


def test_spot_freight_equals_timecharter_cost_without_commission():
    a = copy.deepcopy(assumptions())
    a["voyage"]["commission"] = 0.0
    _, vy = voyage("Panamax/Kamsarmax", "hay_point", "paradip", a=a)
    assert vy.spot_freight_per_t(20000) == pytest.approx(vy.tc_cost_per_t(20000))


def test_recommend_ranks_feasible_classes_by_cost():
    rec = recommend("gladstone", "vizag")
    feas = rec[rec.feasible]
    assert feas["spot_usd_per_t"].is_monotonic_increasing
    assert len(feas) >= 1


def test_scenarios_have_expected_hire_equal_to_today():
    weekly = pd.Series(np.exp(np.cumsum(np.random.default_rng(1).normal(0, 0.08, 300))),
                       index=pd.date_range("2019-01-04", periods=300, freq="W-FRI"))
    m = hire_multipliers(6, 500, seed=3, weekly_close=weekly)
    assert m.shape == (500, 6)
    assert np.allclose(m[:, 0], 1.0)
    assert np.allclose(m.mean(axis=0), 1.0)


@pytest.fixture(scope="module")
def small_case():
    prog = Programme("2026-10", 3, [
        {"origin": "hay_point", "destination": "paradip", "tonnes_per_month": [240000, 160000, 240000]},
        {"origin": "tanjung_bara", "destination": "haldia", "tonnes_per_month": [60000, 60000, 0]},
    ])
    rng = np.random.default_rng(0)
    mult = np.hstack([np.ones((30, 1)), np.exp(rng.normal(0, 0.2, (30, 2)))])
    mult /= mult.mean(axis=0, keepdims=True)
    return prog, mult


def test_every_plan_ships_exactly_the_programme(small_case):
    prog, mult = small_case
    for allowed in (("spot",), ("spot", "tc", "coa")):
        p = solve(prog, None, 0.5, allowed, mult)
        assert p.status == "Optimal"
        got = p.shipments.groupby(["month", "route"])["tonnes"].sum()
        for r, route in enumerate(prog.routes):
            for m, t in enumerate(route["tonnes_per_month"]):
                assert got.get((prog.month_label(m), prog.label(r)), 0) == pytest.approx(t, abs=1)


def test_contracts_never_worsen_the_risk_adjusted_objective(small_case):
    prog, mult = small_case
    a = assumptions()
    alpha, lam = a["risk"]["cvar_alpha"], 0.5
    spot = solve(prog, a, lam, ("spot",), mult).summary(alpha)
    full = solve(prog, a, lam, ("spot", "tc", "coa"), mult).summary(alpha)
    def objective(s):
        return s["expected_cost_usd_m"] + lam * s["cvar_usd_m"]

    assert objective(full) <= objective(spot) + 1e-3
    assert solve(prog, a, 0.0, ("spot",), mult).time_charters == []
