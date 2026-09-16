# Forecasting Methodology

## Business question
What near-term customer demand should operations plan for?

## Grain
One row per month.

## Baseline
Three-month moving average.

## Validation
Historical one-step-ahead backtesting with MAE, RMSE and forecast bias. MAPE is intentionally not required because its suitability depends on the scale and presence of near-zero values.

## Adoption rule
More complex forecasting models should not replace the baseline unless they improve out-of-sample performance and remain operationally interpretable.
