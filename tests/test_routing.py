from nauplan.reference import ports
from nauplan.routing import VARIANTS, distances, route


def test_distance_table_covers_every_pair_and_variant():
    d = distances()
    p = ports()
    n_load, n_dis = (p["role"] == "load").sum(), (p["role"] == "discharge").sum()
    assert len(d) == n_load * n_dis * len(VARIANTS)
    assert d["distance_nm"].between(1_000, 16_000).all()


def test_restricted_variants_are_never_shorter():
    d = distances().pivot_table(index=["origin", "destination"], columns="variant", values="distance_nm")
    assert (d["deep_draft"] >= d["shortest"]).all()
    assert (d["avoid_suez"] >= d["deep_draft"]).all()


def test_deep_draft_routes_avoid_torres_strait():
    d = distances()
    assert not d.loc[d["variant"] != "shortest", "via_torres_strait"].astype(str).eq("True").any()


def test_queensland_shortest_route_uses_torres_strait():
    hay_point, paradip = (149.30, -21.28), (86.72, 20.26)
    assert route(hay_point, paradip, "shortest")["via_torres_strait"]
    assert not route(hay_point, paradip, "deep_draft")["via_torres_strait"]
