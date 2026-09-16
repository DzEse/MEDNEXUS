# Analytical Requirements

Each major analysis must state its business question, grain, required data, method, validation, limitations, output and decision supported.

## Descriptive
Observed KPIs by month, plant, line, machine, product, supplier and customer where grain permits.

## Diagnostic
Pareto, segmentation, trend and SQL drill-down. Associations are not labeled causal.

## Predictive
Logistic Regression baseline for near-term equipment-failure risk. Temporal train/test split, class weighting and false-negative discussion are required.

## Forecasting
Three-month moving-average baseline with backtest MAE, RMSE and bias. More complex models must beat this baseline before adoption.

## Scenario
Baseline → assumption → simulated result → difference. Scenario outputs are explicitly simulated.

## Prescriptive
Management decision queue prioritizes issues using observed concentration, model-derived risk, scenario estimates, confidence and data limitations.
