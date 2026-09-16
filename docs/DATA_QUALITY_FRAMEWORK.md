# Data Quality and Observability Framework

Checks implemented in the default build:
- row counts
- null counts
- duplicate rows
- duplicate primary keys
- nonnegative production counts
- good count ≤ total count
- positive runtime
- nonnegative shipment delay
- nonnegative finance revenue

Observability artifacts are written to `artifacts/validation/` and include table checks, business checks, data-trust score, model metrics, forecast metrics and file hashes.

Recommended future production additions: freshness SLA, schema drift, category drift, unexpected row-count change, referential-integrity queries and alerting.
