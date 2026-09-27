from nauplan.reference import discharge_ports, ports


def test_discharge_ports_match_problem_statement():
    ids = set(discharge_ports()["port_id"])
    assert ids == {"paradip", "vizag", "gangavaram", "gopalpur", "dhamra", "sandheads", "haldia"}


def test_every_filled_constraint_has_a_source():
    p = ports()
    constraint_cols = ["max_draft_m", "max_loa_m", "max_beam_m", "max_dwt_t", "discharge_rate_tpd"]
    filled = p[constraint_cols].notna().any(axis=1)
    assert p.loc[filled, "source"].notna().all(), "constraint values need a source"
