# Data Observability Framework

MEDNEXUS uses lightweight observability across:

**Source → Validation → Transformation → Model → KPI → BI handoff**

## Single-run controls

Current-build evidence includes:

- row counts;
- column counts;
- schema fingerprints;
- required-column checks;
- null rates;
- duplicate rows/keys;
- referential integrity;
- date parsing;
- freshness;
- timeliness;
- model feature sparsity;
- model target positive rate;
- Data Trust components.

## Cross-run drift

The runtime baseline is:

`artifacts/runtime/observability_baseline.csv`

It survives `run_pipeline.py --clean`.

Each run compares the current profile to the previous profile for:

- row-count drift;
- missingness drift;
- schema changes;
- categorical-domain changes;
- predictive-maintenance target-rate drift;
- headline KPI drift.

Machine-readable evidence:

- `artifacts/validation/observability_current_profile.csv`
- `artifacts/validation/cross_run_drift.csv`
- `artifacts/validation/cross_run_drift_summary.json`

## Thresholds

Current project-defined warning thresholds are intentionally simple:

- row-count relative change: 10%;
- null-rate absolute change: 2 percentage points;
- model target positive-rate change: 5 percentage points;
- headline KPI relative change: 20%;
- schema/category-set change: exact-match alert.

These are portfolio governance thresholds, not universal production standards.

A fresh environment initializes the baseline. Later runs perform actual cross-run comparison.
