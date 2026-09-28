"""Walk-forward backtest: at each weekly origin, models see only data known at that date."""
from __future__ import annotations

import numpy as np
import pandas as pd

from nauplan.forecast import HORIZONS
from nauplan.forecast.features import features, targets
from nauplan.forecast.models import MODELS


def train_rows(index: pd.DatetimeIndex, origin_pos: int, h: int) -> np.ndarray:
    """Positions whose h-week target was already observed at the origin (s + h <= origin)."""
    return np.arange(0, max(0, origin_pos - h + 1))


def run(panel: pd.DataFrame, start: str = "2021-01-01", retrain_every: int = 13,
        horizons=HORIZONS, models=tuple(MODELS)) -> pd.DataFrame:
    X, Y = features(panel), targets(panel, horizons)
    valid = X.notna().all(axis=1)
    idx = panel.index
    first = int(np.searchsorted(idx, pd.Timestamp(start)))
    out = []
    for h in horizons:
        fitted, since = {}, retrain_every
        for t in range(first, len(idx) - h):
            if not valid.iloc[t]:
                continue
            if since >= retrain_every:
                tr = train_rows(idx, t, h)
                tr = tr[valid.iloc[tr].to_numpy()]
                history = panel.iloc[: t + 1]
                fitted = {m: MODELS[m]().fit(history, X.iloc[tr], Y[h].iloc[tr], h) for m in models}
                since = 0
            since += 1
            history = panel.iloc[: t + 1]
            for m, model in fitted.items():
                q = model.predict(history, X.iloc[[t]], h)
                out.append({"origin": idx[t], "horizon": h, "model": m, "actual": Y[h].iloc[t],
                            "q10": q[0.1], "q50": q[0.5], "q90": q[0.9]})
    return pd.DataFrame(out)
