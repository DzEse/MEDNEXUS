# Validation Framework

## Data
Automated quality gate in `mednexus/quality.py`.

## SQL
Validation queries in `sql/examples/03_validation.sql` reconcile facts and identify aggregation errors.

## Python
Pytest covers KPI formulas, risk-score bounds, data quality and seed reproducibility.

## ML
Temporal train/test separation, class weighting, recall-sensitive threshold and multiple classification metrics.

## Forecasting
Backtest against observed monthly demand using MAE, RMSE and bias.

## Business
Finance is built from observed synthetic operational components plus explicitly documented illustrative overhead/cost assumptions. OEE, OLI, MORI and scenarios are separately defined.
