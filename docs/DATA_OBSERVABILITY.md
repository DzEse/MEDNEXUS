# MEDNEXUS Data Observability

## Objective

Provide lightweight, reproducible evidence that the source-to-analytics pipeline can detect structural and temporal data problems before management outputs are trusted.

## Current executable evidence

The pipeline emits:

- data_quality_tables.csv;
- data_quality_business_checks.csv;
- referential_integrity.csv;
- data_observability.csv;
- model_input_profile.csv;
- data_trust.json;
- manifest.json.

The observability table records schema signatures, row counts, temporal coverage, parsing failures, freshness lag and timeliness status.

## Portfolio freshness semantics

MEDNEXUS is a reproducible simulated engagement with a deliberately fixed synthetic historical period. Therefore, current portfolio freshness is evaluated relative to the canonical simulation cutoff, not today's wall-clock date.

This is a portfolio-specific rule. A production deployment would use source-specific freshness SLAs and current ingestion timestamps.

## Current limits

The repository does not yet claim live alert routing, persistent run-to-run baselines, automated category-drift alarms, automated model-drift alarms, or production incident escalation.

Those remain later implementation requirements. The current artifacts establish the measurable baseline needed to build those controls without fabricating a live production environment.
