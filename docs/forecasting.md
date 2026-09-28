# Freight forecasting

## What is forecast

The h-week log change of the weekly freight proxy (BDRY closing price, Friday), for h = 1, 4, 8, 13 and 26 weeks. 13 and 26 weeks match 3 and 6 month period contracts. Every forecast is a range: P10, P50, P90.

BDRY is an ETF of dry bulk freight futures, not a spot rate for one vessel class or route. Its price already contains the market's expectation, so large predictable moves are not expected. Per-class spot and period rates (Baltic Exchange or SAIL fixtures) are needed for a real deployment; the same pipeline will run on them.

## No look-ahead

- Features at week t use only data up to t; targets are log(P[t+h] / P[t]).
- FRED series (Brent, USD/INR) are used 7 days after their date; World Bank monthly prices from the 8th of the following month (assumed release lags).
- At each forecast origin, training rows are only those whose target was already observed (s + h <= origin). Models retrain every 13 weeks.
- Tests in `tests/test_forecast.py` check each of these rules.

## Models

| Model | Centre | Range |
|---|---|---|
| random_walk | no change | past h-week moves |
| vol_random_walk | no change | scales with current volatility (EWMA, lambda 0.9, fixed in advance) |
| seasonal_naive | last year's move over the same weeks | its past errors |
| arima | ARIMA(1,1,1) on log price | model variance |
| lgbm_quantile | LightGBM quantile models on 15 features | same |
| lgbm_vol | regularised LightGBM median | volatility band |

## Protocol and results

Forecast origins weekly from Jan 2021. Model choice used only the dev period (origins to Dec 2023), with a rule fixed before scoring the holdout (2024 onward): keep the simplest model unless another beats it by at least 2% pinball loss on dev. Note: a first run of the four original models was inspected over the full period before this split was introduced.

Full tables: [reports/backtest.md](../reports/backtest.md). Summary:

- **Direction is not reliably forecastable** from these public inputs. No model beat the random walk on dev by the 2% rule; the LightGBM models lost clearly on dev (overfitting, ranges far too narrow). Selected model: random walk, all horizons.
- **Ranges depend on the market regime.** In the calm 2024-26 holdout, the random walk's ranges were too wide (94-100% coverage against the 80% target). The volatility-scaled ranges stayed close to target (84-91%) and scored 5-7% better on pinball loss. This is a holdout finding, not a selection, so it is reported as the alternative (`vol_random_walk`) to confirm on more data.
- **Volatility early warning is weak so far.** EWMA volatility tracks next-month volatility better than the long-run average (holdout MAE 0.023 vs 0.034), but the 80th-percentile alert had 36% precision against a 21% base rate on dev and only 3 (false) alerts in the calm holdout.

Overlapping targets mean the effective sample at h = 26 is only about 10 independent periods per split, so small differences are noise.

## What this means for NauPlan

The forecast's job in the decision layer is honest uncertainty, not a confident price call: the optimiser plans against the P10-P90 range and scenarios drawn from it. With real data, the market's own forward curve (FFA) becomes the centre forecast, and the model's value is calibrated ranges, regime and volatility warnings, and the link to vessel, port and contract decisions.

## Commands

```bash
uv run nauplan fetch      # refresh public data
uv run nauplan backtest   # about 90 s; writes reports/backtest.md
uv run nauplan forecast   # writes data/processed/forecast_latest.json
```
