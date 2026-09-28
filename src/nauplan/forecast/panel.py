"""Weekly panel of freight proxy and drivers, using only data that was public at each week.

Release lags (conservative assumptions, documented in docs/forecasting.md):
  FRED daily series (Brent, USD/INR): usable 7 days after the observation date.
  World Bank Pink Sheet (monthly): month M usable from the 8th of month M+1.
"""
from __future__ import annotations

import pandas as pd

from nauplan.config import RAW

WEEK = "W-FRI"
FRED_LAG = pd.Timedelta(days=7)


def _weekly_last(s: pd.Series) -> pd.Series:
    return s.resample(WEEK).last()


def _asof(values: pd.Series, available_from: pd.Series, index: pd.DatetimeIndex) -> pd.Series:
    """Latest value whose availability date is on or before each week end."""
    src = pd.DataFrame({"available": pd.to_datetime(available_from.values).astype("datetime64[ns]"),
                        "v": values.values}).sort_values("available")
    weeks = pd.DataFrame({"week": pd.to_datetime(index).astype("datetime64[ns]")})
    out = pd.merge_asof(weeks, src, left_on="week", right_on="available")
    return pd.Series(out["v"].values, index=index)


def weekly_panel(raw_dir=RAW) -> pd.DataFrame:
    bdry = pd.read_parquet(raw_dir / "bdry.parquet").set_index("date")["bdry_close"]
    panel = _weekly_last(bdry).dropna().to_frame("bdry")
    idx = panel.index

    for name in ("brent_usd_bbl", "usd_inr"):
        s = pd.read_parquet(raw_dir / f"{name}.parquet")
        panel[name] = _asof(s[name], s["date"] + FRED_LAG, idx)

    pink = pd.read_parquet(raw_dir / "pink_sheet.parquet")
    available = pink["date"] + pd.offsets.MonthBegin(1) + pd.Timedelta(days=7)
    for col in ("coal_australia_usd_t", "iron_ore_cfr_usd_t"):
        panel[col] = _asof(pink[col], available, idx)
    return panel
