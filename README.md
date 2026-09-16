# MEDNEXUS — Enterprise Operational Intelligence & Decision Analytics Platform

MEDNEXUS is a **fictional enterprise** and a **simulated analytics engagement**. It is designed to demonstrate how an analyst can move from interconnected enterprise data to evidence-backed management decisions without presenting synthetic results as real business outcomes.

## What this repository implements

The project integrates finance, workforce, recruitment, manufacturing, quality, maintenance, supply chain, logistics, healthcare-customer operations, and technology operations into one reproducible analytical pipeline.

The default build uses **compact synthetic data with documented business logic** so the project runs immediately on a personal computer. Public-data adapters and provenance notes are included for future extensions.

The pipeline produces:

- relational analytical database (`SQLite`)
- curated CSV datasets for SQL/Power BI consumption
- enterprise KPI marts
- OEE and Operational Loss Index (OLI)
- MEDNEXUS Operational Risk Index (MORI)
- Data Trust Score
- predictive-maintenance baseline model
- demand forecast baseline and validation metrics
- scenario-analysis outputs
- management decision queue
- automated data-quality checks
- Power BI semantic-model/DAX/build specifications
- reproducibility and validation artifacts

## Important disclosure

- MEDNEXUS is fictional.
- Synthetic datasets are labeled as synthetic.
- Scenario results are simulated.
- Model outputs are model-derived.
- Financial assumptions are illustrative unless directly calculated from generated observed data.
- This repository does not claim the author worked for MEDNEXUS.


## One-go build + GitHub publish (Windows / VS Code)

After extracting the repository, open the `MEDNEXUS` folder in VS Code and run this in the integrated PowerShell terminal:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/bootstrap_build_and_publish.ps1
```

The script creates `.venv`, installs dependencies, runs the full pipeline, runs the tests, creates a local Git commit, and—when GitHub CLI is installed and authenticated—creates/pushes the `MEDNEXUS` GitHub repository.

## Fast start in VS Code

### Windows PowerShell

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python setup_project.py
python run_pipeline.py
pytest -q
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python setup_project.py
python run_pipeline.py
pytest -q
```

## One-command build after environment setup

```bash
python run_pipeline.py --clean
```

Outputs are written to `artifacts/`, `data/curated/`, `powerbi/exports/`, and `mednexus.db`.

## Repository map

```text
MEDNEXUS/
├── README.md
├── run_pipeline.py
├── setup_project.py
├── requirements.txt
├── environment.yml
├── Makefile
├── mednexus/
│   ├── config.py
│   ├── synthetic.py
│   ├── database.py
│   ├── quality.py
│   ├── analytics.py
│   ├── models.py
│   ├── forecasting.py
│   ├── risk.py
│   ├── scenarios.py
│   ├── decision_queue.py
│   └── pipeline.py
├── sql/
├── tests/
├── docs/
├── powerbi/
├── data/
└── artifacts/
```

## Analytical story

**Business health → value leakage → operational drivers → emerging risk → forecast → intervention scenarios → prioritized actions → monitoring.**

The central executive question is:

> Where is MEDNEXUS losing operational value, why is it happening, what is likely to happen next, and which intervention should management prioritize?

## GitHub publishing

A helper script is included:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/publish_to_github.ps1
```

It uses the GitHub CLI (`gh`). If authenticated, it initializes Git, commits the repository, creates `MEDNEXUS` under your GitHub account if needed, and pushes `main`.

See `docs/REPRODUCIBILITY.md` and `docs/GITHUB_PUBLISHING.md` for details.
