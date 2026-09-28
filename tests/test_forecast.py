import numpy as np
import pandas as pd
import pytest

from nauplan.forecast import QUANTILES
from nauplan.forecast.backtest import run, train_rows
from nauplan.forecast.features import features, targets
from nauplan.forecast.metrics import pinball
from nauplan.forecast.models import MODELS
from nauplan.forecast.panel import weekly_panel


def synthetic_panel(n=260, seed=0):
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2019-01-04", periods=n, freq="W-FRI")
    walk = lambda s0, sd: s0 * np.exp(np.cumsum(rng.normal(0, sd, n)))
    return pd.DataFrame({"bdry": walk(10, 0.08), "brent_usd_bbl": walk(70, 0.04), "usd_inr": walk(75, 0.005),
                         "coal_australia_usd_t": walk(120, 0.05), "iron_ore_cfr_usd_t": walk(100, 0.05)}, index=idx)


def test_training_rows_only_have_targets_observed_by_origin():
    idx = pd.date_range("2020-01-03", periods=100, freq="W-FRI")
    for h in (1, 4, 13):
        for t in (20, 50, 99):
            rows = train_rows(idx, t, h)
            assert rows.max() + h <= t


def test_features_do_not_look_ahead():
    p = synthetic_panel()
    k = 150
    changed = p.copy()
    changed.iloc[k + 1:] *= 3.0
    pd.testing.assert_frame_equal(features(p).iloc[: k + 1], features(changed).iloc[: k + 1])


def test_targets_are_forward_log_returns():
    p = synthetic_panel()
    y = targets(p, horizons=(4,))
    assert y[4].iloc[10] == pytest.approx(np.log(p["bdry"].iloc[14] / p["bdry"].iloc[10]))
    assert y[4].iloc[-4:].isna().all()


def test_monthly_prices_hidden_until_release(tmp_path):
    days = pd.date_range("2024-01-01", "2024-06-30", freq="D")
    pd.DataFrame({"date": days, "bdry_close": 10.0}).to_parquet(tmp_path / "bdry.parquet")
    for name in ("brent_usd_bbl", "usd_inr"):
        pd.DataFrame({"date": days, name: 1.0}).to_parquet(tmp_path / f"{name}.parquet")
    months = pd.date_range("2024-01-01", periods=6, freq="MS")
    pd.DataFrame({"date": months, "coal_australia_usd_t": np.arange(6.0),
                  "iron_ore_cfr_usd_t": np.arange(6.0)}).to_parquet(tmp_path / "pink_sheet.parquet")
    panel = weekly_panel(tmp_path)
    # January's value (0.0) is released from 8 Feb: absent on Fri 2 Feb, present on Fri 9 Feb
    assert pd.isna(panel.loc["2024-02-02", "coal_australia_usd_t"])
    assert panel.loc["2024-02-09", "coal_australia_usd_t"] == 0.0


def test_pinball_loss():
    y = np.array([1.0, 2.0])
    assert pinball(y, np.array([1.0, 2.0]), 0.9) == 0.0
    assert pinball(np.array([1.0]), np.array([0.0]), 0.9) == pytest.approx(0.9)
    assert pinball(np.array([0.0]), np.array([1.0]), 0.9) == pytest.approx(0.1)


@pytest.mark.parametrize("name", list(MODELS))
def test_models_return_ordered_quantiles(name):
    p = synthetic_panel()
    X, Y = features(p), targets(p, horizons=(4,))
    ok = X.notna().all(axis=1) & Y[4].notna()
    t = len(p) - 1
    q = MODELS[name]().fit(p, X[ok], Y[4][ok], 4).predict(p, X.iloc[[t]], 4)
    assert set(q) == set(QUANTILES)
    assert q[0.1] <= q[0.5] <= q[0.9]


def test_backtest_runs_on_synthetic_data():
    out = run(synthetic_panel(), start="2021-06-01", horizons=(1, 4), models=("random_walk", "vol_random_walk"))
    assert {"origin", "horizon", "model", "actual", "q10", "q50", "q90"} <= set(out.columns)
    assert out[["q10", "q50", "q90", "actual"]].notna().all().all()
