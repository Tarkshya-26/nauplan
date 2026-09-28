"""Volatility forecasting for early warnings: is a turbulent month ahead?

At each origin t we forecast realised volatility over the next `h` weeks
(RMS of weekly log returns t+1..t+h) and flag 'high volatility' when the forecast is
above the 80th percentile of volatility seen in the training history.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from nauplan.forecast.models import ewma_vol


def realised_vol(panel: pd.DataFrame, h: int = 4) -> pd.Series:
    r = np.log(panel["bdry"]).diff()
    fwd = (r ** 2).rolling(h).mean().shift(-h)  # mean of r[t+1..t+h]^2
    return np.sqrt(fwd)


def backtest(panel: pd.DataFrame, h: int = 4, start: str = "2021-01-01", pct: float = 0.8) -> pd.DataFrame:
    r = np.log(panel["bdry"]).diff()
    ewma = ewma_vol(panel)
    real = realised_vol(panel, h)
    rows = []
    idx = panel.index
    for t in range(int(np.searchsorted(idx, pd.Timestamp(start))), len(idx) - h):
        past_r = r.iloc[1: t + 1]
        past_real = real.iloc[: max(0, t - h + 1)].dropna()  # realised vols fully observed by t
        threshold = float(np.quantile(past_real, pct))
        rows.append({
            "origin": idx[t], "actual": float(real.iloc[t]),
            "historical": float(np.sqrt((past_r ** 2).mean())),
            "ewma": float(ewma.iloc[t]),
            "alert": bool(ewma.iloc[t] > threshold),
            "actual_high": bool(real.iloc[t] > threshold),
        })
    return pd.DataFrame(rows)


def summarise(bt: pd.DataFrame) -> dict:
    out = {"n": len(bt)}
    for m in ("historical", "ewma"):
        out[f"mae_{m}"] = float(np.mean(np.abs(bt[m] - bt["actual"])))
        out[f"corr_{m}"] = float(np.corrcoef(bt[m], bt["actual"])[0, 1])
    alerts = bt[bt["alert"]]
    out["alerts"] = len(alerts)
    out["alert_precision"] = float(alerts["actual_high"].mean()) if len(alerts) else float("nan")
    out["high_vol_recall"] = float(bt.loc[bt["actual_high"], "alert"].mean()) if bt["actual_high"].any() else float("nan")
    out["base_rate_high"] = float(bt["actual_high"].mean())
    return out
