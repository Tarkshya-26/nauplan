"""Entry points: full backtest report and the latest forecast."""
from __future__ import annotations

import json
from datetime import UTC, datetime

import numpy as np
import pandas as pd

from nauplan.config import PROCESSED, ROOT
from nauplan.forecast import HORIZONS, QUANTILES
from nauplan.forecast import volatility as vol
from nauplan.forecast.backtest import run as run_backtest
from nauplan.forecast.features import features, targets
from nauplan.forecast.metrics import DEV_END, summarise
from nauplan.forecast.models import MODELS, ewma_vol
from nauplan.forecast.panel import weekly_panel

# Chosen on the dev period only, by a rule fixed before the holdout was scored:
# use the simplest model unless another beats it by >= 2% pinball loss on dev. None did.
SELECTED = {h: "random_walk" for h in HORIZONS}
ALTERNATIVE = "vol_random_walk"  # better calibrated in the 2024-26 holdout; to confirm on more data


def _md(df: pd.DataFrame) -> str:
    cols = list(df.columns)
    lines = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for _, r in df.iterrows():
        lines.append("| " + " | ".join(f"{v:.3f}" if isinstance(v, float) else str(v) for v in r) + " |")
    return "\n".join(lines)


def backtest_report() -> str:
    panel = weekly_panel()
    preds = run_backtest(panel)
    PROCESSED.mkdir(parents=True, exist_ok=True)
    preds.to_parquet(PROCESSED / "backtest_predictions.parquet", index=False)
    s = summarise(preds)
    cols = ["model", "horizon", "n", "mae_vs_rw", "pinball_vs_rw", "coverage_80", "direction_hit", "mape_price"]
    vbt = vol.backtest(panel)
    vs = {p: vol.summarise(g) for p, g in (("dev", vbt[vbt.origin <= DEV_END]), ("holdout", vbt[vbt.origin > DEV_END]))}

    parts = [
        "# Freight forecast backtest",
        (f"Generated {datetime.now(UTC).date()} by `uv run nauplan backtest`. Data: BDRY weekly closes "
         f"{panel.index.min().date()} to {panel.index.max().date()}. Forecast origins from 2021-01-01; "
         f"dev = origins to {DEV_END.date()}, holdout = later origins. Models retrained every 13 weeks, "
         "using only data public at each origin."),
        ("Metrics on h-week log returns. `mae_vs_rw` and `pinball_vs_rw` below 1 beat the random walk. "
         "`coverage_80` should be near 0.80. `direction_hit` is the share of correct up/down calls. "
         "Targets overlap for h > 1, so the effective sample is much smaller than n (about n / h)."),
    ]
    for per in ("dev", "holdout"):
        t = s[s.period == per][cols].sort_values(["horizon", "pinball_vs_rw"])
        parts += [f"## Price models, {per}", _md(t.round(3))]
    parts += ["## Volatility early warning (next 4 weeks)",
              _md(pd.DataFrame([{"period": p, **{k: (round(v, 3) if isinstance(v, float) else v)
                                                   for k, v in d.items()}} for p, d in vs.items()]))]
    path = ROOT / "reports" / "backtest.md"
    path.parent.mkdir(exist_ok=True)
    path.write_text("\n\n".join(parts) + "\n")
    return str(path)


def latest_forecast() -> str:
    panel = weekly_panel()
    X, Y = features(panel), targets(panel)
    valid = X.notna().all(axis=1)
    last = panel.index[-1]
    price = float(panel["bdry"].iloc[-1])
    out = {"as_of": str(last.date()), "series": "BDRY (dry bulk freight futures ETF, proxy)",
           "last_price": round(price, 2), "horizons": {}}
    for h in HORIZONS:
        tr = np.arange(0, len(panel) - h)
        tr = tr[valid.iloc[tr].to_numpy() & Y[h].iloc[tr].notna().to_numpy()]
        entry = {}
        for name in (SELECTED[h], ALTERNATIVE):
            q = MODELS[name]().fit(panel, X.iloc[tr], Y[h].iloc[tr], h).predict(panel, X.iloc[[-1]], h)
            entry[name] = {f"p{int(k * 100)}": round(price * float(np.exp(q[k])), 2) for k in QUANTILES}
        entry["selected"] = SELECTED[h]
        out["horizons"][str(h)] = entry
    v = ewma_vol(panel)
    out["weekly_volatility"] = round(float(v.iloc[-1]), 4)
    out["weekly_volatility_pct_rank"] = round(float((v.dropna() <= v.iloc[-1]).mean()), 3)
    PROCESSED.mkdir(parents=True, exist_ok=True)
    path = PROCESSED / "forecast_latest.json"
    path.write_text(json.dumps(out, indent=2))
    return str(path)
