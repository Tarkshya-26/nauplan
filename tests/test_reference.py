import pandas as pd

from nauplan.config import REFERENCE
from nauplan.reference import LIMIT_COLUMNS, berths, discharge_ports, ports, vessel_classes

PS_PORTS = {"paradip", "vizag", "gangavaram", "gopalpur", "dhamra", "sandheads", "haldia"}
PS_ORIGINS = {"Australia", "United States", "Mozambique", "Russia", "Indonesia"}
SOURCE_TYPES = {"official_port", "official_operator", "official_terminal", "official_pilotage", "official",
                "government", "government_dataset", "secondary"}


def test_discharge_ports_match_problem_statement():
    assert set(discharge_ports()["port_id"]) == PS_PORTS


def test_every_port_has_berth_limits():
    assert set(berths()["port_id"]) == set(ports()["port_id"])


def test_load_ports_cover_every_origin_in_problem_statement():
    p = ports()
    assert set(p.loc[p["role"] == "load", "country"]) == PS_ORIGINS


def test_source_types_are_known():
    assert set(berths()["source_type"]) <= SOURCE_TYPES
    assert set(pd.read_csv(REFERENCE / "passages.csv")["source_type"]) <= SOURCE_TYPES


def test_every_filled_limit_has_a_source():
    b = berths()
    filled = b[LIMIT_COLUMNS].notna().any(axis=1)
    sourced = b["source_url"].str.startswith("http") & b["accessed"].notna()
    assert sourced[filled].all(), b.loc[filled & ~sourced, ["port_id", "berth"]]


def test_limits_are_physically_plausible():
    b = berths()
    checks = {"max_draft_m": (5, 25), "max_loa_m": (100, 400), "max_beam_m": (20, 70),
              "max_dwt_t": (10_000, 400_000), "max_displacement_t": (10_000, 450_000),
              "water_depth_m": (5, 60), "load_rate_tph": (500, 20_000)}
    for col, (lo, hi) in checks.items():
        vals = b[col].dropna()
        assert vals.between(lo, hi).all(), (col, vals[~vals.between(lo, hi)])


def test_vessel_classes_cover_problem_statement():
    v = vessel_classes()
    ps = set(v.loc[v["in_problem_statement"] == "yes", "vessel_class"])
    assert ps == {"Handysize", "Supramax/Ultramax", "Panamax/Kamsarmax", "Capesize"}
    assert (v["dwt_min"] < v["dwt_max"]).all()
    assert pd.Series(v["source_url"]).str.startswith("http").all()
