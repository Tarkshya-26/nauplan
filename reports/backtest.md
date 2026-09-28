# Freight forecast backtest

Generated 2026-09-28 by `uv run nauplan backtest`. Data: BDRY weekly closes 2018-03-23 to 2026-09-25. Forecast origins from 2021-01-01; dev = origins to 2023-12-31, holdout = later origins. Models retrained every 13 weeks, using only data public at each origin.

Metrics on h-week log returns. `mae_vs_rw` and `pinball_vs_rw` below 1 beat the random walk. `coverage_80` should be near 0.80. `direction_hit` is the share of correct up/down calls. Targets overlap for h > 1, so the effective sample is much smaller than n (about n / h).

## Price models, dev

| model | horizon | n | mae_vs_rw | pinball_vs_rw | coverage_80 | direction_hit | mape_price |
|---|---|---|---|---|---|---|---|
| vol_random_walk | 1 | 157 | 1.000 | 0.994 | 0.790 | nan | 0.079 |
| random_walk | 1 | 157 | 1.000 | 1.000 | 0.771 | nan | 0.079 |
| arima | 1 | 157 | 1.018 | 1.011 | 0.745 | 0.471 | 0.081 |
| lgbm_vol | 1 | 157 | 1.035 | 1.019 | 0.771 | 0.471 | 0.082 |
| lgbm_quantile | 1 | 157 | 1.116 | 1.144 | 0.586 | 0.446 | 0.089 |
| seasonal_naive | 1 | 157 | 1.406 | 1.420 | 0.694 | 0.497 | 0.113 |
| random_walk | 4 | 157 | 1.000 | 1.000 | 0.815 | nan | 0.167 |
| arima | 4 | 157 | 1.017 | 1.010 | 0.764 | 0.490 | 0.169 |
| vol_random_walk | 4 | 157 | 1.000 | 1.028 | 0.834 | nan | 0.167 |
| lgbm_vol | 4 | 157 | 1.081 | 1.094 | 0.790 | 0.471 | 0.184 |
| lgbm_quantile | 4 | 157 | 1.347 | 1.445 | 0.465 | 0.369 | 0.229 |
| seasonal_naive | 4 | 157 | 1.451 | 1.496 | 0.752 | 0.561 | 0.246 |
| random_walk | 8 | 157 | 1.000 | 1.000 | 0.834 | nan | 0.254 |
| arima | 8 | 157 | 1.011 | 1.001 | 0.777 | 0.522 | 0.257 |
| vol_random_walk | 8 | 157 | 1.000 | 1.064 | 0.847 | nan | 0.254 |
| lgbm_vol | 8 | 157 | 1.154 | 1.225 | 0.777 | 0.433 | 0.298 |
| lgbm_quantile | 8 | 157 | 1.406 | 1.557 | 0.490 | 0.312 | 0.369 |
| seasonal_naive | 8 | 157 | 1.637 | 1.738 | 0.662 | 0.471 | 0.432 |
| random_walk | 13 | 157 | 1.000 | 1.000 | 0.809 | nan | 0.340 |
| arima | 13 | 157 | 1.008 | 1.021 | 0.739 | 0.541 | 0.345 |
| vol_random_walk | 13 | 157 | 1.000 | 1.117 | 0.847 | nan | 0.340 |
| lgbm_vol | 13 | 157 | 1.199 | 1.318 | 0.790 | 0.357 | 0.447 |
| lgbm_quantile | 13 | 157 | 1.652 | 1.830 | 0.427 | 0.312 | 0.567 |
| seasonal_naive | 13 | 157 | 1.707 | 1.883 | 0.618 | 0.427 | 0.623 |
| arima | 26 | 157 | 1.016 | 0.990 | 0.694 | 0.516 | 0.584 |
| random_walk | 26 | 157 | 1.000 | 1.000 | 0.847 | nan | 0.571 |
| vol_random_walk | 26 | 157 | 1.000 | 1.116 | 0.822 | nan | 0.571 |
| lgbm_vol | 26 | 157 | 1.262 | 1.288 | 0.809 | 0.261 | 0.772 |
| lgbm_quantile | 26 | 157 | 1.612 | 1.863 | 0.293 | 0.401 | 1.000 |
| seasonal_naive | 26 | 157 | 1.793 | 1.954 | 0.643 | 0.376 | 1.361 |

## Price models, holdout

| model | horizon | n | mae_vs_rw | pinball_vs_rw | coverage_80 | direction_hit | mape_price |
|---|---|---|---|---|---|---|---|
| vol_random_walk | 1 | 142 | 1.000 | 0.934 | 0.852 | nan | 0.047 |
| lgbm_vol | 1 | 142 | 1.036 | 0.963 | 0.824 | 0.521 | 0.049 |
| lgbm_quantile | 1 | 142 | 1.076 | 0.981 | 0.775 | 0.479 | 0.051 |
| arima | 1 | 142 | 0.990 | 0.991 | 0.930 | 0.521 | 0.047 |
| random_walk | 1 | 142 | 1.000 | 1.000 | 0.937 | nan | 0.047 |
| seasonal_naive | 1 | 142 | 1.541 | 1.515 | 0.915 | 0.500 | 0.074 |
| vol_random_walk | 4 | 139 | 1.000 | 0.949 | 0.856 | nan | 0.103 |
| lgbm_quantile | 4 | 139 | 1.053 | 0.963 | 0.719 | 0.597 | 0.105 |
| arima | 4 | 139 | 0.985 | 0.975 | 0.935 | 0.576 | 0.103 |
| lgbm_vol | 4 | 139 | 1.003 | 0.975 | 0.820 | 0.554 | 0.102 |
| random_walk | 4 | 139 | 1.000 | 1.000 | 0.957 | nan | 0.103 |
| seasonal_naive | 4 | 139 | 1.645 | 1.549 | 0.878 | 0.496 | 0.180 |
| lgbm_vol | 8 | 135 | 0.917 | 0.919 | 0.874 | 0.644 | 0.132 |
| lgbm_quantile | 8 | 135 | 0.923 | 0.953 | 0.659 | 0.719 | 0.134 |
| vol_random_walk | 8 | 135 | 1.000 | 0.977 | 0.844 | nan | 0.150 |
| arima | 8 | 135 | 0.991 | 0.981 | 0.963 | 0.556 | 0.150 |
| random_walk | 8 | 135 | 1.000 | 1.000 | 0.970 | nan | 0.150 |
| seasonal_naive | 8 | 135 | 1.807 | 1.714 | 0.904 | 0.452 | 0.309 |
| lgbm_quantile | 13 | 130 | 1.040 | 0.875 | 0.654 | 0.623 | 0.198 |
| arima | 13 | 130 | 0.995 | 0.931 | 0.938 | 0.577 | 0.209 |
| vol_random_walk | 13 | 130 | 1.000 | 0.952 | 0.908 | nan | 0.209 |
| lgbm_vol | 13 | 130 | 1.051 | 0.997 | 0.885 | 0.562 | 0.201 |
| random_walk | 13 | 130 | 1.000 | 1.000 | 1.000 | nan | 0.209 |
| seasonal_naive | 13 | 130 | 1.914 | 1.768 | 0.877 | 0.438 | 0.484 |
| arima | 26 | 117 | 1.006 | 0.906 | 0.983 | 0.624 | 0.387 |
| vol_random_walk | 26 | 117 | 1.000 | 0.927 | 0.880 | nan | 0.382 |
| lgbm_vol | 26 | 117 | 0.971 | 0.977 | 0.803 | 0.581 | 0.303 |
| random_walk | 26 | 117 | 1.000 | 1.000 | 1.000 | nan | 0.382 |
| lgbm_quantile | 26 | 117 | 1.143 | 1.041 | 0.581 | 0.513 | 0.333 |
| seasonal_naive | 26 | 117 | 2.028 | 1.822 | 0.863 | 0.282 | 1.030 |

## Volatility early warning (next 4 weeks)

| period | n | mae_historical | corr_historical | mae_ewma | corr_ewma | alerts | alert_precision | high_vol_recall | base_rate_high |
|---|---|---|---|---|---|---|---|---|---|
| dev | 157 | 0.028 | -0.409 | 0.028 | 0.128 | 22 | 0.364 | 0.242 | 0.210 |
| holdout | 139 | 0.034 | 0.181 | 0.023 | 0.220 | 3 | 0.000 | 0.000 | 0.014 |
