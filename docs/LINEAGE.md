# Data Lineage

## Example: OEE
`fact_production` → `production_kpis()` → `data/curated/production_kpis.csv` → `powerbi/exports/ProductionKPI.csv` → OEE DAX/visual → capacity-loss investigation.

## Example: MORI
Cross-domain facts → `enterprise_monthly_mart` → normalized risk components → `mori.csv` → executive command center → risk-prioritization decision.

## Example: predictive maintenance
`fact_sensor` → temporal split → Logistic Regression → model metrics + scored observations → equipment-risk page → maintenance investigation.

## Example: decision queue
Historical KPIs + Pareto + reliability concentration + MORI + forecast/scenario context → decision queue → management action review.
