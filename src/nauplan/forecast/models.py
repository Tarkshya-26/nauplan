"""Forecast models. Each predicts quantiles of the h-week log return of the freight proxy.

fit(history, X, y, h) receives only rows whose target was observed by the forecast origin.
predict(history, X_row, h) returns {quantile: log return}.
"""
from __future__ import annotations

import warnings
from typing import ClassVar

import numpy as np
import pandas as pd

from nauplan.forecast import QUANTILES


class RandomWalk:
    """No change expected; the range comes from past h-week moves."""
    name = "random_walk"

    def fit(self, history, X, y, h):
        self.q = {q: float(np.quantile(y, q)) - float(np.median(y)) for q in QUANTILES}
        self.q[0.5] = 0.0
        return self

    def predict(self, history, X_row, h):
        return dict(self.q)


class SeasonalNaive:
    """Repeats last year's move over the same weeks; range from its past errors."""
    name = "seasonal_naive"

    @staticmethod
    def _point(lp: pd.Series, t_pos: int, h: int) -> float:
        a, b = t_pos - 52, t_pos - 52 + h
        return float(lp.iloc[b] - lp.iloc[a]) if a >= 0 else np.nan

    def fit(self, history, X, y, h):
        lp = np.log(history["bdry"])
        pos = {t: i for i, t in enumerate(lp.index)}
        pts = np.array([self._point(lp, pos[t], h) for t in y.index])
        err = (y.values - pts)[~np.isnan(pts)]
        self.err_q = {q: float(np.quantile(err, q)) for q in QUANTILES}
        return self

    def predict(self, history, X_row, h):
        lp = np.log(history["bdry"])
        p = self._point(lp, len(lp) - 1, h)
        return {q: p + self.err_q[q] for q in QUANTILES}


class Arima:
    """ARIMA(1,1,1) on weekly log price; parameters refit at each retrain, state updated every week."""
    name = "arima"
    Z: ClassVar[dict] = {0.1: -1.2816, 0.5: 0.0, 0.9: 1.2816}

    def fit(self, history, X, y, h):
        from statsmodels.tsa.statespace.sarimax import SARIMAX
        lp = np.log(history["bdry"]).reset_index(drop=True)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self.params = SARIMAX(lp, order=(1, 1, 1)).fit(disp=False).params
        return self

    def predict(self, history, X_row, h):
        from statsmodels.tsa.statespace.sarimax import SARIMAX
        lp = np.log(history["bdry"]).reset_index(drop=True)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            fc = SARIMAX(lp, order=(1, 1, 1)).filter(self.params).get_forecast(h)
        mean, sd = float(fc.predicted_mean.iloc[-1]) - float(lp.iloc[-1]), float(np.sqrt(fc.var_pred_mean.iloc[-1]))
        return {q: mean + z * sd for q, z in self.Z.items()}


class LgbmQuantile:
    """One LightGBM model per quantile, trained on the engineered features."""
    name = "lgbm_quantile"
    PARAMS: ClassVar[dict] = {"n_estimators": 300, "learning_rate": 0.03, "num_leaves": 7, "min_child_samples": 20,
                              "subsample": 0.8, "subsample_freq": 1, "colsample_bytree": 0.8, "verbose": -1}

    def fit(self, history, X, y, h):
        import lightgbm as lgb
        self.models = {q: lgb.LGBMRegressor(objective="quantile", alpha=q, **self.PARAMS).fit(X, y)
                       for q in QUANTILES}
        return self

    def predict(self, history, X_row, h):
        vals = sorted(float(m.predict(X_row)[0]) for m in self.models.values())  # no quantile crossing
        return dict(zip(QUANTILES, vals))


def ewma_vol(history: pd.DataFrame, lam: float = 0.9) -> pd.Series:
    """Weekly volatility estimate: exponentially weighted RMS of weekly log returns (known at each week)."""
    r = np.log(history["bdry"]).diff()
    return np.sqrt((r ** 2).ewm(alpha=1 - lam, adjust=False).mean())


class VolRandomWalk:
    """No change expected; the range scales with current volatility (EWMA, lambda 0.9, fixed a priori).

    Quantiles of standardised past moves y / (vol * sqrt(h)) keep the fat tails of freight returns.
    """
    name = "vol_random_walk"

    def fit(self, history, X, y, h):
        vol = ewma_vol(history).reindex(y.index)
        z = (y / (vol * np.sqrt(h))).dropna()
        self.zq = {q: float(np.quantile(z, q)) - float(np.median(z)) for q in QUANTILES}
        return self

    def predict(self, history, X_row, h):
        scale = float(ewma_vol(history).iloc[-1]) * np.sqrt(h)
        return {q: (0.0 if q == 0.5 else self.zq[q] * scale) for q in QUANTILES}


class LgbmVol(VolRandomWalk):
    """Heavily regularised LightGBM for the median move; range from the volatility model around it."""
    name = "lgbm_vol"
    PARAMS: ClassVar[dict] = {"objective": "l1", "n_estimators": 150, "learning_rate": 0.02, "num_leaves": 4,
                              "min_child_samples": 40, "subsample": 0.7, "subsample_freq": 1,
                              "colsample_bytree": 0.6, "reg_lambda": 5.0, "verbose": -1}

    def fit(self, history, X, y, h):
        import lightgbm as lgb
        super().fit(history, X, y, h)
        self.model = lgb.LGBMRegressor(**self.PARAMS).fit(X, y)
        return self

    def predict(self, history, X_row, h):
        mid = float(self.model.predict(X_row)[0])
        band = super().predict(history, X_row, h)
        return {q: mid + band[q] for q in QUANTILES}


MODELS = {m.name: m for m in (RandomWalk, SeasonalNaive, Arima, LgbmQuantile, VolRandomWalk, LgbmVol)}
