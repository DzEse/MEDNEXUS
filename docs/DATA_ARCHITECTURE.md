# Data Architecture

## Canonical layers

MEDNEXUS uses:

**Raw → Synthetic/Source → Staging/Validation → Curated → Analytical SQL/Python → BI → Governance/Observability**

### 1. Raw

Reserved for externally acquired public data. Public data is not activated unless source, usage and provenance are verified.

### 2. Synthetic/source

`data/synthetic/` contains reproducible fictional enterprise source facts generated from documented relationships.

### 3. Staging / validation

Python quality, referential-integrity, schema, freshness and business-rule checks validate source facts before analytical use.

SQLite now also exposes explicit staging views such as `stg_production_validated`. These views are logical layers rather than duplicate persisted CSV copies.

### 4. Curated

`data/curated/` contains derived marts and model/scenario/process outputs at declared grains.

### 5. Analytical SQL / Python

SQLite `mednexus.db` contains source facts, analytical marts and views.

`sql/layered_architecture.sql` explicitly separates:

- staging validation;
- dimensional hierarchy;
- enriched fact views;
- KPI presentation;
- grain-validation views.

`sql/analytical_views.sql` retains executive, quality, reliability, supplier and reconciliation views.

### 6. BI

`powerbi/exports/` contains compact CSV handoffs only. Power BI remains a presentation/semantic layer and must not recreate unsupported business logic independently.

### 7. Governance / observability

`artifacts/validation/` contains machine-readable evidence for data quality, model/forecast/scenario gates, lineage, SQL contracts and architecture.

`artifacts/runtime/observability_baseline.csv` is a local persistent cross-run baseline intentionally excluded from Git and intentionally preserved by `--clean`.

## Why SQLite + CSV remain appropriate

SQLite is embedded, reproducible and personal-machine friendly. CSV keeps the Power BI handoff universal. A warehouse migration is not required to demonstrate the current business logic and would add complexity without decision value.

## Duplicate-minimization rule

MEDNEXUS does not persist a second full staging copy merely to imitate enterprise tooling. Staging is represented through validation logic and SQL views unless a genuine acquisition/cleaning requirement justifies persisted staging data.
