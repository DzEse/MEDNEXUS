# MEDNEXUS — Enterprise Operational Intelligence & Decision Analytics Platform

MEDNEXUS is a **fictional medical-technology enterprise** and a **simulated enterprise analytics engagement**. It is designed to demonstrate how an analyst can move from fragmented enterprise data to validated evidence, diagnostic insight, prediction/forecasting, risk/scenario analysis and management decisions without presenting synthetic or simulated results as real business outcomes.

This is not a school assignment, a collection of disconnected dashboards, or a Kaggle-style notebook project. The repository is governed by professional standards for business logic, data integrity, analytical validity, reproducibility, traceability and decision usefulness.

## Central executive question

> **Where is MEDNEXUS losing operational value, why is it happening, what is likely to happen next, and which intervention should management prioritize?**

## Canonical specification and governance

The full project specification is preserved verbatim in the repository:

- [`docs/specification/MEDNEXUS_MASTER_BUILD_SPECIFICATION.md`](docs/specification/MEDNEXUS_MASTER_BUILD_SPECIFICATION.md) — canonical 57-section production-grade specification.
- [`docs/MASTER_IMPLEMENTATION_BLUEPRINT.md`](docs/MASTER_IMPLEMENTATION_BLUEPRINT.md) — preserves all 60 original implementation areas and adds binding A01–A32/B01–B28 enhancement annexes.
- [`docs/specification/REQUIREMENTS_TRACEABILITY_MATRIX.md`](docs/specification/REQUIREMENTS_TRACEABILITY_MATRIX.md) — section-by-section implementation status and remaining work.
- [`docs/specification/MEDNEXUS_ENTERPRISE_DATASET_DIGITAL_TWIN_ENHANCEMENT.md`](docs/specification/MEDNEXUS_ENTERPRISE_DATASET_DIGITAL_TWIN_ENHANCEMENT.md) — binding A01–A32 enterprise data/digital-twin enhancement.
- [`docs/specification/MEDNEXUS_EXECUTIVE_COMMAND_CENTER_ENHANCEMENT.md`](docs/specification/MEDNEXUS_EXECUTIVE_COMMAND_CENTER_ENHANCEMENT.md) — binding B01–B28 flagship Command Center enhancement.
- [`docs/specification/ENHANCEMENT_TRACEABILITY_MATRIX.md`](docs/specification/ENHANCEMENT_TRACEABILITY_MATRIX.md) — per-requirement status for all 60 enhancement requirements.
- [`docs/specification/SCOPE_PRESERVATION_POLICY.md`](docs/specification/SCOPE_PRESERVATION_POLICY.md) — additive/no-silent-dropping change-control policy.
- [`docs/DEFINITION_OF_DONE.md`](docs/DEFINITION_OF_DONE.md) — final evidence-based completion gate.

The governing priority hierarchy is:

**Accuracy → Business Logic → Data Integrity → Analytical Validity → Reproducibility → Decision Value → Technical Depth → Visual Polish**

## Current implementation status

The repository contains a validated **core baseline**, not a claim that every canonical requirement is complete.

Implemented or substantially implemented today:

- deterministic, cross-process-reproducible synthetic enterprise generator;
- finance, workforce, recruitment, manufacturing, quality, maintenance, supply, logistics, healthcare-customer and technology/SaaS facts;
- SQLite analytical database and SQL analytical views;
- OEE and Operational Loss Index (OLI) baseline;
- MEDNEXUS Operational Risk Index (MORI) baseline;
- Data Trust Score baseline;
- Logistic Regression predictive-maintenance baseline with temporal validation;
- demand moving-average forecast baseline with backtest metrics;
- simulated scenario engine baseline;
- evidence/confidence/limitations management decision queue;
- automated data-quality/business checks;
- reproducibility manifest and cross-process determinism guard;
- Phase 12G 58-file Power BI export contract with ambiguity-safe relationship/table-role audit and headline reconciliation targets;
- Power BI semantic-model/DAX/build specifications, preserved Page 1 shell, and flagship Executive Command Center implementation blueprint;
- CI-compatible automated tests;
- explicit fictional/synthetic/model-derived/simulated disclosures.

Earlier analytical predecessor work is now substantially implemented or explicitly gated. **Phase 12E.1 validated the structural prototype, Phase 12F validated the promotion/filter-behavior decision gate, and Phase 12G physically applies only the approved structures.** The canonical Power BI contract is now 58 exports with 45 active and 2 inactive relationships, Data Trust remains 100/100, and the full CI regression passes 120 tests. High-risk reverse-disaggregated prototype facts remain gated and are not exported.

Nothing is silently treated as complete simply because a baseline exists.

## Important disclosure

- MEDNEXUS is fictional.
- The default enterprise operating data is synthetic.
- Public benchmark datasets, if used, retain their own provenance/license and are not represented as MEDNEXUS proprietary data.
- Scenario results are **Simulated**.
- Predictive/forecast outputs are **Model-derived**.
- Project-defined financial parameters are **Illustrative assumptions** unless calculated directly from generated facts.
- MORI, OLI and Data Trust are project-defined analytical constructs and are not presented as external industry standards.
- This repository does not claim the author worked for MEDNEXUS.
- No patient-identifiable information is used.

## Enterprise analytical story

**Business Health → Value Leakage → Operational Drivers → Emerging Risk → Forecast → Management Levers → Simulated Interventions → Prioritized Decisions → Monitoring/Learning**

Domains connect through explicit relationships such as:

- workforce demand → capacity pressure → operational strain;
- machine deterioration → downtime → production/shipment pressure;
- process/quality loss → rework/scrap → cost/throughput pressure;
- supplier variability → shortages → capacity pressure;
- technology reliability → data availability/trust → decision reliability.

Where evidence does not support a causal claim, the relationship is labeled association, simulated, scenario-based, conceptual or hypothesis requiring validation.

## One-go build + GitHub publish (Windows / VS Code)

After cloning/extracting the repository, open the `MEDNEXUS` folder in VS Code and run:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/bootstrap_build_and_publish.ps1
```

The hardened Windows script creates/uses `.venv`, installs dependencies, runs the pipeline/tests, commits changes when needed and pushes when GitHub CLI is authenticated. Native command failures stop the script rather than reporting false success.

## Current validated setup flow

### Windows PowerShell

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python setup_project.py
python run_pipeline.py --clean
pytest -q
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python setup_project.py
python run_pipeline.py --clean
pytest -q
```

Outputs are written to `artifacts/`, `data/curated/`, `powerbi/exports/` and local `mednexus.db`.

## Current enhancement execution boundary

Phase 12 is closed as a **validated baseline**, not discarded.

Before final PBIX construction, MEDNEXUS now requires:

1. enhanced-grain/business-question design — **completed for Phase 12E.1**;
2. a small deterministic prototype — **completed**;
3. key/relationship/event/inventory/calculation validation — **completed in CI (62/62 checks)**;
4. Phase 12E structural evidence — **completed**;
5. Phase 12F promotion/filter-behavior contract validation — **completed locally and in CI**;
6. physical implementation of only the 8 approved structures — **completed in Phase 12G**;
7. canonical semantic-model audit and reconciliation-target regeneration — **completed in Phase 12G**;
8. Phase 12H Power BI Desktop handoff pack — **repository implementation in progress / PBIX remains user-side**;
9. actual Power BI Desktop relationship/measure reconciliation;
10. flagship Executive Command Center build after model reconciliation passes.

See `docs/ENHANCED_ENTERPRISE_DATA_ARCHITECTURE_BLUEPRINT.md` and `powerbi/EXECUTIVE_COMMAND_CENTER_BLUEPRINT.md`.

The active Phase 12G local evidence runner is:

```powershell
powershell -ExecutionPolicy Bypass -File ".\scripts\phase12g_canonical_promotion.ps1"
```

Phase 12E and Phase 12F evidence remains preserved as historical predecessor evidence.

The Phase 12H Desktop handoff prep command is:

```powershell
powershell -ExecutionPolicy Bypass -File ".\\scripts\\phase12h_powerbi_handoff_prep.ps1"
```

## Power BI handoff

The repository does **not** pretend a PBIX file exists. The user builds the final report in Power BI Desktop using the generated BI exports and documented semantic model/DAX/page specifications.

The current preparation command is:

```powershell
powershell -ExecutionPolicy Bypass -File ".\scripts\phase2_powerbi_prep.ps1"
```

Phase 12G validates the canonical 58-file export/semantic-model contract. The existing Page 1 Enterprise Command Center design remains a report shell. The repository still does not claim that a PBIX has been built or reconciled; that requires Power BI Desktop.

## Repository map

```text
MEDNEXUS/
├── README.md
├── LICENSE
├── requirements.txt
├── environment.yml
├── setup_project.py
├── run_pipeline.py
├── config/
├── mednexus/
├── sql/
├── tests/
├── docs/
│   ├── specification/
│   │   ├── MEDNEXUS_MASTER_BUILD_SPECIFICATION.md
│   │   ├── REQUIREMENTS_TRACEABILITY_MATRIX.md
│   │   └── SCOPE_PRESERVATION_POLICY.md
│   ├── MASTER_IMPLEMENTATION_BLUEPRINT.md
│   └── ... methodology / architecture / validation documentation
├── notebooks/
├── data/
├── artifacts/
├── scripts/
└── powerbi/
```

The repository intentionally remains compact. New folders are added only when real implementation artifacts require them; empty folder trees are not created merely for appearance.

## Validation and reproducibility

The build currently includes:

- deterministic project seed;
- stable product assignment independent of Python hash randomization;
- cross-process reproducibility verification;
- data-quality/business-rule checks;
- generated-output SHA-256 manifest;
- model/forecast validation metrics;
- pytest suite;
- canonical specification preservation tests that require all 57 specification sections, all 60 original master-blueprint areas, all A01–A32/B01–B28 enhancement requirements and their traceability rows to remain present.

## GitHub publishing

The connected repository is `DzEse/MEDNEXUS`. A helper remains available:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/publish_to_github.ps1
```

See `docs/REPRODUCIBILITY.md`, `docs/GITHUB_PUBLISHING.md`, the canonical master specification and the requirements traceability matrix before treating the portfolio as final.
