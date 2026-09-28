"""Freight-rate scenarios for the optimiser.

Hire multipliers relative to today, one per month, built by resampling real 4-week moves of
the freight proxy (BDRY). Each month's multipliers are rescaled to average exactly 1, so the
expected future hire equals today's (no directional view, as the backtest supports); the
spread and fat tails come from history.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from nauplan.config import RAW

WEEKS_PER_MONTH = 4


def monthly_moves(weekly_close: pd.Series) -> np.ndarray:
    """All overlapping 4-week log moves, de-meaned."""
    lp = np.log(weekly_close.dropna())
    moves = (lp.shift(-WEEKS_PER_MONTH) - lp).dropna().to_numpy()
    return moves - moves.mean()


def hire_multipliers(months: int, n: int, seed: int = 7, weekly_close: pd.Series | None = None,
                     vol_scale: float = 1.0) -> np.ndarray:
    """Array (n, months). Month 0 is fixed at today's market (multiplier 1)."""
    if weekly_close is None:
        daily = pd.read_parquet(RAW / "bdry.parquet").set_index("date")["bdry_close"]
        weekly_close = daily.resample("W-FRI").last()
    moves = monthly_moves(weekly_close) * vol_scale
    rng = np.random.default_rng(seed)
    draws = rng.choice(moves, size=(n, months - 1), replace=True)
    paths = np.exp(np.cumsum(draws, axis=1))
    paths /= paths.mean(axis=0, keepdims=True)  # expected hire = today's hire in every month
    return np.hstack([np.ones((n, 1)), paths])
