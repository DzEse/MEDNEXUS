# Repository Guide

- `mednexus/` — reusable production-style Python modules.
- `sql/` — reusable analytical views and demonstration queries.
- `tests/` — automated validation.
- `config/` — project configuration and source registry.
- `data/synthetic/` — generated synthetic facts/dimensions; ignored by Git.
- `data/curated/` — generated analytical marts; ignored by Git.
- `artifacts/validation/` — metrics, quality results and manifest.
- `artifacts/reports/` — generated management summary.
- `powerbi/` — semantic model, DAX and page/build guidance.
- `scripts/` — GitHub publishing helper.
- `docs/` — charter, requirements, architecture, methodology, lineage, limitations and validation documentation.

Do not commit secrets, PBIX binaries, regenerated model artifacts, local databases or large raw public datasets.
