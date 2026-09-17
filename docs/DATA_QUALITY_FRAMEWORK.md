# MEDNEXUS Data Quality, Data Trust & Observability Framework

## Purpose

MEDNEXUS treats data quality as an executable control layer, not a dashboard decoration. The quality gate must answer whether the analytical evidence is structurally usable before KPI, statistical, model, scenario, or BI outputs are trusted.

The canonical synthetic build is expected to pass the controls below. A 100/100 score on the synthetic build means the implemented project checks found no failures; it does not mean the data is universally perfect or that the score is an external industry standard.

## Executable control layers

### 1. Table/schema controls

mednexus.quality.evaluate() records, per table:

- row count;
- column count;
- total cells;
- null cells and null rate;
- duplicate rows;
- duplicate primary keys where an explicit key exists;
- missing required contract fields;
- deterministic schema signature.

A table fails the structural gate when an explicit primary key is duplicated, an exact duplicate row is present, or a required contract field is missing.

### 2. Business validity controls

The current executable checks include:

- production counts nonnegative;
- good count not above total count;
- runtime positive;
- planned downtime not above planned production time;
- production-count identity reconciliation;
- shipment delay nonnegative;
- on-time flag binary and consistent with delay;
- shipment date ordering;
- revenue and operating cost nonnegative;
- finance operating-margin reconciliation;
- workforce headcount/rate validity;
- workforce vacancy reconciliation;
- recruitment-funnel monotonicity;
- supplier reliability range;
- supply quantity validity;
- SaaS adoption range;
- predictive-maintenance target binary.

The checks are deliberately business-rule based. They do not invent thresholds that the synthetic business logic does not support.

### 3. Referential integrity and hierarchy consistency

evaluate_referential_integrity() validates all documented foreign-key paths across plant, line, machine, product, supplier, customer, orders and downstream operational facts.

It additionally checks cross-key hierarchy consistency so that a fact row cannot independently contain valid machine_id, line_id, and plant_id values that refer to incompatible parents.

Artifact: artifacts/validation/referential_integrity.csv

### 4. Data observability

build_observability() creates one record per source table with:

- row count;
- column count;
- schema signature;
- date field and analytical cadence;
- minimum and maximum observed date;
- date-parse failure count;
- freshness lag;
- cadence-aware freshness tolerance;
- freshness status;
- timeliness status.

For this static portfolio build, freshness is measured relative to the canonical simulation cutoff derived from production data, not relative to the computer's current date. This prevents a deliberately frozen reproducible dataset from being mislabeled stale merely because the portfolio is viewed later.

Artifact: artifacts/validation/data_observability.csv

Production deployment would replace this portfolio-relative rule with source-specific SLAs and alerting.

### 5. Model-input quality profile

model_input_profile() records feature missingness, cardinality, zero-variance checks, and target positive rate for the predictive-maintenance input.

Artifact: artifacts/validation/model_input_profile.csv

This exposes class imbalance and feature sparsity before model evaluation.

## MEDNEXUS Data Trust Score v2

The Data Trust Score is explicitly project-defined and not an external standard.

Scale: 0-100.

The v2 score uses equal weights across eight dimensions:

1. completeness;
2. validity;
3. consistency;
4. uniqueness;
5. timeliness;
6. referential integrity;
7. schema consistency;
8. freshness.

For each dimension, the implementation produces a normalized 0-1 component. The composite is:

Data Trust Score = 100 x mean(component scores)

The score and all component values are written to artifacts/validation/data_trust.json.

Equal weighting is used because there is no observed business evidence supporting a more complex weighting scheme. A production implementation should review weights and thresholds with data owners.

## Data dictionary and table register

The pipeline generates:

- artifacts/validation/data_dictionary.csv — one row per source field with type, semantic role, description, FK target, observed nullability/cardinality, example and source classification;
- artifacts/validation/table_register.csv — one row per table with grain, PK, FK set, row count, analytical cadence/refresh logic and business meaning.

These are generated from the same code and source frames as the analytical pipeline, reducing documentation drift.

## Fail-closed behavior

The pipeline stops before analytical marts/models are trusted when any of these executable gates fail:

- structural table/schema gate;
- business validity/consistency gate;
- referential-integrity/hierarchy gate;
- observability freshness/timeliness gate.

A failed Data Trust component is evidence to investigate; the pipeline does not silently coerce the score back to 100.

## Drift and production extensions still open

The canonical specification also calls for production-style monitoring such as:

- cross-run unexpected row-count change;
- missingness spikes;
- category drift;
- source-schema evolution alerts;
- source-specific freshness SLA alerting;
- model-health drift monitoring;
- KPI anomaly monitoring.

The current observability artifacts provide the baseline evidence needed for those controls. Persistent cross-run baselines and alert routing remain a later production-style extension and must not be represented as already operating.

## Lineage

Governance evidence follows:

Synthetic source/generation -> validation -> integrity/observability -> transformation -> analytical marts/models -> Power BI -> management decision

See LINEAGE.md and the canonical traceability matrix for the broader output-level lineage requirement.
