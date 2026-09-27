import pandas as pd

from nauplan.data.fetch import parse_pink_sheet


def test_parse_pink_sheet_keeps_known_series_and_handles_missing():
    header = [None, "Crude oil, Brent", "Coal, Australian", "Cocoa", "Iron ore, cfr spot"]
    rows = [["title"] + [None] * 4] * 4 + [
        header,
        [None, "($/bbl)", "($/mt)", "($/kg)", "($/dmtu)"],
        ["1960M01", 1.6, "…", 0.6, 10.0],
        ["2026M08", 80.0, 120.5, 7.0, 95.0],
        ["Note: footer", None, None, None, None],
    ]
    out = parse_pink_sheet(pd.DataFrame(rows))
    assert list(out.columns) == ["date", "brent_usd_bbl", "coal_australia_usd_t", "iron_ore_cfr_usd_t"]
    assert len(out) == 2
    assert pd.isna(out.loc[0, "coal_australia_usd_t"])
    assert out.loc[1, "date"] == pd.Timestamp("2026-08-01")
