# Data Lineage

MEDNEXUS maintains both human-readable lineage and a machine-readable output registry.

Machine-readable artifact:

`artifacts/validation/output_lineage_registry.csv`

Canonical lineage chain:

**Source → Generation/Ingestion → Validation → Transformation → Analytical Table/Artifact → Method/KPI/Model → Power BI Surface → Decision**

## Headline examples

### Production / OEE

`fact_production`
→ data-quality / RI gates
→ `production_kpis()`
→ `mart_production_kpi`
→ `ProductionKPI.csv`
→ Manufacturing Performance page
→ capacity-loss investigation.

### Statistical quality

`fact_production`
→ `p_chart_by_plant()`
→ `mart_quality_p_chart`
→ `QualityPChart.csv`
→ Quality & Process Intelligence page
→ process-stability investigation.

### Root-cause diagnostics

Production + machine + workforce evidence
→ `run_root_cause_analysis()`
→ diagnostic evidence marts
→ `RootCausePriorities.csv`
→ Quality page
→ investigation prioritization.

Outputs remain association/investigation evidence, not causal attribution.

### Predictive maintenance

`fact_sensor`
→ temporal train/validation/test split
→ model comparison + threshold selection + calibration assessment
→ scored holdout observations
→ `PredictiveMaintenanceScores.csv`
→ Equipment & Reliability page
→ maintenance investigation.

### Forecasting

`fact_orders`
→ monthly demand
→ rolling-origin comparator validation
→ selected forecast method
→ `DemandForecast.csv`
→ Prediction, Forecast & Risk page
→ short-term capacity planning.

### MORI

Cross-domain facts
→ `enterprise_monthly_mart()`
→ normalized risk components
→ `run_mori_validation()`
→ `MORI.csv` + sensitivity evidence
→ Executive / Prediction pages
→ cross-domain risk review.

MORI remains project-defined.

### Scenarios

Enterprise monthly mart
→ explicit scenario assumptions
→ `run_scenarios()`
→ simulated results / differences / monitoring plan
→ Scenario & Decision Intelligence page
→ intervention comparison.

Scenario opportunity value is simulated and is not realized savings.

### Process analytics

Orders + shipments + optional service events
→ linked order-level event log
→ case cycle times / transition durations
→ `ProcessTransitions.csv`
→ Logistics page
→ fulfillment investigation.

This is order-fulfillment analytics only, not full manufacturing process mining.

### Decision queue

Historical KPIs + Pareto + reliability + MORI + forecast/scenario evidence
→ `build_decision_queue()`
→ `DecisionQueue.csv`
→ Executive / Scenario pages
→ management action review.

### Data Trust

Table quality + referential integrity + freshness/timeliness + observability
→ `data_trust_score()`
→ `data_trust.json`
→ Technology / Executive pages
→ data-reliability review.
