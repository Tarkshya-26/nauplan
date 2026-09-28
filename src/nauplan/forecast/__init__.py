"""Freight forecasting: weekly panel, features, models, walk-forward backtest."""

HORIZONS = (1, 4, 8, 13, 26)  # weeks ahead; 13 and 26 match 3 and 6 month period contracts
QUANTILES = (0.1, 0.5, 0.9)
