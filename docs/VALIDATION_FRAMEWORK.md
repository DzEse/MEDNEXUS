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

Predictive maintenance now uses a strict train/validation/test temporal design. Validation data is used for Logistic Regression vs Random Forest comparison and threshold/error-cost selection; the final test period remains untouched until holdout evaluation.

Validation evidence includes:

- validation PR-AUC/ROC-AUC and candidate comparison;
- explicit false-negative vs false-positive decision weights;
- threshold sweep and confusion-matrix evidence;
- holdout precision, recall, F1, ROC-AUC and PR-AUC;
- Brier score and binned calibration evidence;
- permutation feature importance on the holdout period;
- strict date ordering and non-overlap tests;
- anti-causal interpretation labels.

Gradient boosting, SHAP/PDP and probability recalibration remain conditional extensions rather than forced complexity.

## Root-cause diagnostics

Automated validation covers:

- unique diagnostic grain;
- bounded defect rates and Wilson confidence intervals;
- FDR-adjusted Spearman associations;
- practical high-vs-low quartile contrasts;
- Kruskal-Wallis effect sizes;
- grouped-binomial GLM convergence, finite robust standard errors and VIF;
- shallow-tree depth and feature-importance integrity;
- explicit non-causal labels on all investigation-priority outputs.

## Forecasting

Backtest against observed monthly demand using MAE, RMSE and bias. Comparator expansion remains an open canonical requirement.

## Business

Finance is built from synthetic operational components plus explicitly documented illustrative overhead/cost assumptions. OEE, OLI, FPY, MORI, value leakage and scenarios are separately defined and reconciled where valid.
