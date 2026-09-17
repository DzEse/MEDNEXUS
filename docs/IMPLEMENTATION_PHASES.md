# MEDNEXUS Implementation Phases and Dependencies

This plan follows the canonical master specification. Phase status reflects **evidence closure**, not simply whether a file exists. Cross-phase baseline work already completed is preserved, but a later phase is not considered final if predecessor requirements remain unresolved.

| Phase | Deliverable | Depends on | Current state |
|---|---|---|---|
| 0 | Enterprise definition and project charter | — | Substantially implemented |
| 1 | Business requirements and analytical questions | 0 | Substantially implemented; expanded canonical traceability active |
| 2 | Source-data research and provenance | 1 | Partial — public sources registered; actual-use acquisition/license verification still gated |
| 3 | Data architecture and dimensional modeling | 1–2 | Partial — core model works; full grain/key/cardinality/refresh dictionary still required |
| 4 | Synthetic enterprise data generation | 3 | Implemented baseline; expand only for unresolved business requirements |
| 5 | Data ingestion and staging | 2–4 | Partial — reproducible synthetic generation exists; explicit public ingestion/staging architecture needs expansion if public sources are activated |
| 6 | Data quality and validation | 5 | Partial — core gates pass; RI/observability/drift/freshness/model-data checks require expansion |
| 7 | SQL analytical layer | 6 | Partial — SQLite views/examples exist; staged quality/dimension/fact/KPI/reconciliation SQL architecture requires expansion |
| 8 | Python exploratory/statistical/diagnostic layer | 6–7 | Partial — core KPI analytics exist; statistical quality/root-cause/evidence hierarchy still required |
| 9 | Predictive analytics | 6–8 | Partial — Logistic Regression baseline exists; Random Forest/calibration/threshold/explainability comparison remains |
| 10 | Forecasting | 6–8 | Partial — moving-average baseline exists; comparator/backtest/adequacy expansion remains |
| 11 | Risk intelligence | 8–10 | Partial — MORI works; sensitivity/missing-data/expanded component evidence remains |
| 12 | Scenario / decision / optimization gate | 8–11 | Partial — scenario/decision queue works; expanded scenario schema and optimization/process-analysis gates remain |
| 13 | Power BI semantic model | 7–12 | Strong baseline/report shell exists; final acceptance waits for predecessor analytical closure |
| 14 | Power BI report development | 13 | Page 1 shell/specification prepared; final report build intentionally not treated as complete yet |
| 15 | Validation and reconciliation | 7–14 | Partial — reproducibility/data/model/forecast checks exist; cross-domain/SQL/statistical/BI reconciliation needs expansion |
| 16 | Documentation | continuous; final after 15 | Strong baseline; Data Dictionary, observability/lineage depth and final closeout remain |
| 17 | Portfolio / GitHub presentation | 15–16 | Not final — README/governance improved; screenshots/final evidence package wait for analytical/BI closure |

## Current execution order

The next work should close/gate predecessor analytical requirements before treating Power BI as final:

1. expand Data Quality + referential integrity + observability;
2. formalize table-level grain/PK/FK/cardinality/refresh dictionary;
3. expand SQL staging/quality/dimension/fact/KPI/reconciliation layer;
4. build statistical/quality and root-cause evidence layer;
5. implement Six Big Losses / COPQ / value-leakage decomposition;
6. strengthen predictive maintenance hierarchy, threshold/calibration and explainability;
7. strengthen forecasting comparison/backtesting;
8. expand MORI sensitivity/missing-data behavior;
9. expand scenario schema and run optimization/process-mining suitability gates;
10. regenerate/reconcile Power BI exports and continue report pages.

## Phase dependency rule

A phase can use preliminary outputs from a later phase for design exploration, but final acceptance cannot bypass unresolved predecessor validity requirements. Existing Page 1 work remains preserved and will be refreshed rather than discarded.
