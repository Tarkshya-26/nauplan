import warnings

import pytest

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    from fastapi.testclient import TestClient

from nauplan.api import app

client = TestClient(app)
ROUTE = {"origin": "hay_point", "destination": "paradip", "tonnes_per_month": [200000, 150000, 200000]}


def test_fit_rejects_ports_in_the_wrong_role():
    r = client.post("/api/fit", json={"origin": "paradip", "destination": "hay_point"})
    assert r.status_code == 422
    assert "not a known load port" in r.json()["detail"]


def test_fit_uses_port_names_in_reasons():
    r = client.post("/api/fit", json={"origin": "hay_point", "destination": "paradip"})
    assert r.status_code == 200
    reasons = " ".join(o["why"] for o in r.json()["options"])
    assert "hay_point" not in reasons and "Hay Point" in reasons


def test_plan_needs_equal_months_per_route():
    bad = {**ROUTE, "tonnes_per_month": [1, 2]}
    r = client.post("/api/plan", json={"routes": [ROUTE, bad]})
    assert r.status_code == 422


@pytest.mark.skipif(not (__import__("nauplan.config").config.RAW / "bdry.parquet").exists(),
                    reason="needs `nauplan fetch` data for scenarios")
def test_plan_returns_both_strategies():
    r = client.post("/api/plan", json={"routes": [ROUTE], "scenarios": 20, "risk_weight": 0.5})
    assert r.status_code == 200
    body = r.json()
    assert [s["plan"] for s in body["strategies"]] == ["All spot (current practice)", "NauPlan"]
    assert len(body["costs_usd_m"]["spot"]) == 20
