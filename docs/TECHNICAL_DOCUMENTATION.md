# Technical Documentation

## Runtime
Python 3.11+; SQLite via the Python standard library; pandas/numpy for data processing; scikit-learn for predictive modeling; pytest for validation.

## Entry points
- `setup_project.py` creates runtime directories.
- `run_pipeline.py --clean` executes the complete build.
- `pytest -q` validates formulas, quality gates, risk bounds and reproducibility.

## Pipeline order
1. Generate deterministic synthetic source tables.
2. Run data-quality gate.
3. Build KPI/enterprise marts.
4. Train predictive-maintenance baseline.
5. Backtest demand forecast.
6. Construct MORI, scenarios and decision queue.
7. Load SQLite facts/marts and create SQL views.
8. Export Power BI-ready CSVs and management summary.
9. Write file-hash manifest.

## Failure behavior
The pipeline fails closed when core table/business data-quality checks fail. It does not silently continue past a failed quality gate.
