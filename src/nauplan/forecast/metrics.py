from __future__ import annotations

import numpy as np
import pandas as pd


def pinball(y: np.ndarray, pred: np.ndarray, q: float) -> float:
    d = y - pred
    return float(np.mean(np.maximum(q * d, (q - 1) * d)))


DEV_END = pd.Timestamp("2023-12-31")  # model choice uses origins up to here; later origins are the holdout


def period(origin: pd.Series) -> pd.Series:
    return np.where(origin <= DEV_END, "dev", "holdout")


def summarise(preds: pd.DataFrame, by_period: bool = True) -> pd.DataFrame:
    """preds columns: origin, model, horizon, actual, q10, q50, q90 (log returns)."""
    preds = preds.assign(period=period(preds["origin"]) if by_period else "all")
    rows = []
    for (per, model, h), g in preds.groupby(["period", "model", "horizon"]):
        y = g["actual"].to_numpy()
        price_err = np.abs(np.exp(g["q50"].to_numpy() - y) - 1)  # |forecast price / actual price - 1|
        moving = g["q50"].abs() > 1e-12
        rows.append({
            "period": per, "model": model, "horizon": h, "n": len(g),
            "mae": float(np.mean(np.abs(g["q50"] - y))),
            "mape_price": float(np.mean(price_err)),
            "pinball": np.mean([pinball(y, g[c].to_numpy(), q) for c, q in (("q10", .1), ("q50", .5), ("q90", .9))]),
            "coverage_80": float(np.mean((y >= g["q10"]) & (y <= g["q90"]))),
            "direction_hit": float(np.mean(np.sign(g.loc[moving, "q50"]) == np.sign(g.loc[moving, "actual"])))
            if moving.any() else np.nan,
        })
    out = pd.DataFrame(rows)
    base = out[out["model"] == "random_walk"].set_index(["period", "horizon"])
    key = pd.MultiIndex.from_frame(out[["period", "horizon"]])
    out["mae_vs_rw"] = out["mae"].to_numpy() / base["mae"].reindex(key).to_numpy()
    out["pinball_vs_rw"] = out["pinball"].to_numpy() / base["pinball"].reindex(key).to_numpy()
    return out
