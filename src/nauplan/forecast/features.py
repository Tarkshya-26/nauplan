"""Features at week t use only panel rows up to t. Targets are log(P[t+h] / P[t])."""
from __future__ import annotations

import numpy as np
import pandas as pd

from nauplan.forecast import HORIZONS


def features(panel: pd.DataFrame) -> pd.DataFrame:
    lp = np.log(panel["bdry"])
    r = lp.diff()
    f = pd.DataFrame(index=panel.index)
    for k in (1, 4, 13, 26, 52):
        f[f"ret_{k}"] = lp.diff(k)
    f["vol_4"] = r.rolling(4).std()
    f["vol_13"] = r.rolling(13).std()
    f["z_52"] = (lp - lp.rolling(52).mean()) / lp.rolling(52).std()
    f["brent_ret_4"] = np.log(panel["brent_usd_bbl"]).diff(4)
    f["brent_ret_13"] = np.log(panel["brent_usd_bbl"]).diff(13)
    f["inr_ret_13"] = np.log(panel["usd_inr"]).diff(13)
    f["coal_ret_13"] = np.log(panel["coal_australia_usd_t"]).diff(13)
    f["iron_ret_13"] = np.log(panel["iron_ore_cfr_usd_t"]).diff(13)
    week = panel.index.isocalendar().week.astype(float).values
    f["woy_sin"] = np.sin(2 * np.pi * week / 52.18)
    f["woy_cos"] = np.cos(2 * np.pi * week / 52.18)
    return f


def targets(panel: pd.DataFrame, horizons=HORIZONS) -> pd.DataFrame:
    lp = np.log(panel["bdry"])
    return pd.DataFrame({h: lp.shift(-h) - lp for h in horizons}, index=panel.index)
