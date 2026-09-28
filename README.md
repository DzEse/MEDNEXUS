# MEDNEXUS — Enterprise Operational Intelligence & Decision Analytics

**Portfolio focus:** Data Analytics • Operations Analytics • Manufacturing Analytics • SQL • Python • Forecasting • Predictive Analytics • Power BI

MEDNEXUS is a **fictional medical-technology enterprise analytics project** built to demonstrate how an analyst can move from fragmented operational data to validated KPIs, diagnostic analysis, forecasting, predictive modelling, scenario analysis, and management decision support.

> **Recruiter summary:** This project demonstrates end-to-end analytical thinking across manufacturing, quality, maintenance, supply, finance, workforce, and technology data. It includes Python pipelines, a SQLite analytical database, SQL views, automated data-quality checks, forecasting and predictive-maintenance baselines, Power BI-ready exports, reproducibility controls, and automated tests.

## Business Question

> **Where is the business losing operational value, why is it happening, what is likely to happen next, and which actions should management investigate?**

## What I Built

- Deterministic synthetic enterprise-data generator covering multiple business domains.
- SQLite analytical database with reusable SQL analytical views.
- Manufacturing and operations KPIs including OEE-oriented analysis.
- Data-quality and business-rule validation checks.
- Predictive-maintenance baseline using Logistic Regression with temporal validation.
- Demand-forecasting baseline with backtesting.
- Scenario-analysis framework for comparing simulated interventions.
- Management decision queue that records evidence, confidence, and limitations.
- Power BI export layer and documented semantic-model/DAX design.
- Reproducibility manifest and automated regression testing.

## Skills Demonstrated

| Area | Evidence in this project |
|---|---|
| Data engineering | Reproducible Python data-generation and transformation pipeline |
| SQL | SQLite database and analytical views |
| Data quality | Automated validation and business-rule checks |
| Operations analytics | Manufacturing, quality, maintenance, supply and logistics analysis |
| Forecasting | Demand baseline with backtest metrics |
| Predictive analytics | Predictive-maintenance baseline with temporal validation |
| BI modelling | Power BI export contract, semantic-model and DAX specifications |
| Governance | Traceability matrices, scope controls, reproducibility and explicit limitations |
| Testing | CI-compatible automated test suite |

## Current Validated Baseline

The repository contains a validated **core baseline**, not a claim that every planned feature is complete.

Current implementation includes:

- finance, workforce, recruitment, manufacturing, quality, maintenance, supply, logistics, healthcare-customer, and technology/SaaS facts;
- SQLite analytical database and SQL analytical views;
- OEE and Operational Loss Index (OLI) baseline;
- MEDNEXUS Operational Risk Index (MORI) baseline;
- Data Trust Score baseline;
- Logistic Regression predictive-maintenance baseline with temporal validation;
- demand moving-average forecast baseline with backtest metrics;
- simulated scenario engine;
- evidence/confidence/limitations management decision queue;
- automated data-quality and business checks;
- reproducibility manifest and cross-process determinism guard;
- Power BI export and semantic-model contract;
- CI-compatible automated tests.

The current repository documentation records a **58-file Power BI export contract**, **45 active and 2 inactive relationships**, a **Data Trust Score of 100/100**, and a full CI regression of **120 tests** for the documented baseline.

## Analytical Story

**Business Health → Value Leakage → Operational Drivers → Emerging Risk → Forecast → Management Levers → Simulated Interventions → Prioritized Decisions → Monitoring**

Example relationships explored in the project include:

- workforce demand → capacity pressure → operational strain;
- machine deterioration → downtime → production/shipment pressure;
- process and quality loss → rework/scrap → cost and throughput pressure;
- supplier variability → shortages → capacity pressure;
- technology reliability → data availability/trust → decision reliability.

Where the evidence does not support a causal conclusion, the relationship is labelled as an association, simulated result, scenario, hypothesis, or conceptual link.

## Important Disclosure

- MEDNEXUS is fictional.
- The default enterprise operating data is synthetic.
- This repository does **not** claim that I worked for a real company called MEDNEXUS.
- Predictive and forecast outputs are model-derived.
- Scenario outputs are simulated.
- Project-defined financial parameters are illustrative unless directly calculated from generated facts.
- MORI, OLI, and Data Trust are project-defined analytical constructs, not external industry standards.
- No patient-identifiable information is used.

## Technology

- Python
- Pandas / NumPy
- SQLite / SQL
- scikit-learn
- Pytest
- Power BI design specifications
- DAX / Power Query design
- Git / GitHub
- PowerShell automation

## Repository Structure

```text
MEDNEXUS/
├── mednexus/          # analytical pipeline modules
├── sql/               # SQL logic and views
├── tests/             # automated validation and regression tests
├── docs/              # architecture, methods, governance and specifications
├── data/              # generated/curated data areas
├── artifacts/         # analytical outputs
├── scripts/           # build, validation and handoff automation
├── powerbi/           # BI exports and Power BI specifications
├── setup_project.py
├── run_pipeline.py
└── README.md
```

## Run the Project

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

Outputs are written to `artifacts/`, `data/curated/`, `powerbi/exports/`, and the local `mednexus.db`.

## Power BI Status

The repository contains the analytical exports, semantic-model specifications, DAX/build guidance, validation contracts, and handoff material required for Power BI development.

It does **not** claim that the final PBIX report has been fully built and reconciled. Final Power BI Desktop construction remains a separate user-side step.

## Governance and Technical Documentation

The detailed implementation is preserved in the repository documentation:

- [Master Build Specification](docs/specification/MEDNEXUS_MASTER_BUILD_SPECIFICATION.md)
- [Master Implementation Blueprint](docs/MASTER_IMPLEMENTATION_BLUEPRINT.md)
- [Requirements Traceability Matrix](docs/specification/REQUIREMENTS_TRACEABILITY_MATRIX.md)
- [Scope Preservation Policy](docs/specification/SCOPE_PRESERVATION_POLICY.md)
- [Definition of Done](docs/DEFINITION_OF_DONE.md)
- [Reproducibility Documentation](docs/REPRODUCIBILITY.md)

The project uses the following priority hierarchy:

**Accuracy → Business Logic → Data Integrity → Analytical Validity → Reproducibility → Decision Value → Technical Depth → Visual Polish**

## Career Relevance

This project is intended to demonstrate skills relevant to roles such as:

**Technical Data Analyst • Manufacturing Data Analyst • Operations Data Analyst • BI Analyst • Reporting Analyst • Engineering Data Analyst • Predictive Analytics Analyst • Junior Data Scientist**
