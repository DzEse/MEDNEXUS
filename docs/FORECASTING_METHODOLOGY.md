# Forecasting Methodology

## Business question

What near-term customer demand should operations plan for?

## Grain

One row per month.

## Canonical baseline

The original three-month moving average is preserved as the canonical transparent baseline.

## Comparator hierarchy

The validated comparison set is intentionally compact and interpretable:

1. Naive last-value benchmark.
2. Three-month moving average baseline.
3. Twelve-month seasonal naive comparator.
4. Expanding linear trend comparator.

The project does not force ARIMA, Prophet, gradient boosting, or other higher-complexity forecasting methods without evidence that added complexity is justified by the data volume and decision need.

## Validation design

Forecast selection uses expanding-window rolling-origin, one-step-ahead backtesting. Every candidate is evaluated on the same common backtest months after at least 12 months of training history are available.

Metrics:

- MAE;
- RMSE;
- sMAPE;
- forecast bias;
- residual lag-1 autocorrelation;
- Ljung-Box residual autocorrelation diagnostic.

MAPE remains excluded because zero/near-zero denominators can make it unstable. sMAPE is retained with explicit zero-denominator handling.

## Selection rule

The selected model has the lowest rolling-origin MAE; RMSE and then sMAPE are tie-breakers.

The adequacy gate separately records whether:

- the common backtest sample is large enough;
- the selected model is not worse than naive on MAE;
- the selected model is not worse than naive on RMSE.

If no candidate beats the naive benchmark, MEDNEXUS does not claim forecasting improvement. The result is explicitly labeled limited and the benchmark can remain selected.

## Future forecast

The selected method generates a three-month model-derived demand forecast. Recursive predictions are used where the method requires prior forecast values.

## Interpretation

All forecast metrics and future values are model-derived from synthetic operating data. Backtest performance does not guarantee future or real-world accuracy.
