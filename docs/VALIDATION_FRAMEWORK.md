# Validation Framework

## Data

Automated structural, business-rule, referential-integrity, freshness and schema checks run through mednexus/quality.py.

## SQL

SQL reconciliation views verify:

- production count identities;
- production fact vs quality-event totals;
- monthly finance revenue vs order revenue;
- operating cost vs the documented cost-component reconstruction.

Pytest executes these reconciliation views against the canonical generated data.

## Python

Pytest covers:

- KPI formulas;
- FPY semantics;
- OEE/OLI bounds;
- Data Trust dimensions;
- referential integrity;
- generated dictionary/table register;
- statistical quality method gates;
- p-chart limits;
- capacity-waterfall reconciliation;
- Six Big Losses gating;
- full-COPQ non-fabrication;
- risk-score bounds;
- cross-process reproducibility;
- master-spec traceability.

## Statistical quality

The p-chart implementation is validated for 0–1 rates, valid LCL/UCL ordering and explicit signal classification.

Capability indices are validated by exclusion: tests require Cp/Cpk/Pp/Ppk to remain NOT_CALCULABLE until legitimate specification limits exist.

RTY and DPMO are likewise fail-closed.

## ML

Temporal train/test separation, class weighting, recall-sensitive threshold and multiple classification metrics remain part of the predictive-maintenance validation layer.

## Forecasting

Backtest against observed monthly demand using MAE, RMSE and bias. Comparator expansion remains an open canonical requirement.

## Business

Finance is built from synthetic operational components plus explicitly documented illustrative overhead/cost assumptions. OEE, OLI, FPY, MORI, value leakage and scenarios are separately defined and reconciled where valid.
