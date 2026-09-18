# Power BI Semantic Model

Use `EnterpriseMonthly` as the executive monthly mart and the detailed fact tables for domain pages and drill-through.

## Core dimensions

- `DimDate` — one row per calendar date; use as the primary date dimension.
- `DimPlant`
- `DimLine`
- `DimMachine`
- `DimProduct`
- `DimSupplier`
- `DimCustomer`
- `DimEmployee`

## Recommended active relationships

Use one-to-many (`1:*`) relationships with **single-direction filtering from dimension to fact** unless a documented analytical requirement proves otherwise.

### Date

- `DimDate[date]` 1:* `EnterpriseMonthly[month_date]`
- `DimDate[date]` 1:* `MORI[month_date]`
- `DimDate[date]` 1:* `ProductionKPI[date]`
- `DimDate[date]` 1:* `Downtime[date]`
- `DimDate[date]` 1:* `QualityEvents[date]`
- `DimDate[date]` 1:* `Maintenance[date]`
- `DimDate[date]` 1:* `PredictiveMaintenanceScores[date]`
- `DimDate[date]` 1:* `Workforce[month]`
- `DimDate[date]` 1:* `Recruitment[month]`
- `DimDate[date]` 1:* `Supply[month]`
- `DimDate[date]` 1:* `Finance[month]`
- `DimDate[date]` 1:* `DemandForecast[month]`
- `DimDate[date]` 1:* `Orders[order_date]`
- `DimDate[date]` 1:* `Shipments[ship_date]`
- `DimDate[date]` 1:* `CustomerService[date]`
- `DimDate[date]` 1:* `TechnologyIncidents[date]`
- `DimDate[date]` 1:* `QualityPChart[date]`
- `DimDate[date]` 1:* `SixBigLosses[month_date]`
- `DimDate[date]` 1:* `CapacityWaterfall[month_date]`
- `DimDate[date]` 1:* `ValueLeakage[month_date]`

For `Shipments[promised_date]` and `Shipments[actual_delivery_date]`, create inactive date relationships only if a measure explicitly needs them. Do not make multiple active date paths to the same fact.

### Operations hierarchy

- `DimPlant[plant_id]` 1:* `DimLine[plant_id]`
- `DimLine[line_id]` 1:* `DimMachine[line_id]`
- `DimPlant[plant_id]` 1:* `ProductionKPI[plant_id]`
- `DimPlant[plant_id]` 1:* `QualityPChart[plant_id]`
- `DimLine[line_id]` 1:* `ProductionKPI[line_id]`
- `DimMachine[machine_id]` 1:* `ProductionKPI[machine_id]`
- `DimMachine[machine_id]` 1:* `Downtime[machine_id]`
- `DimMachine[machine_id]` 1:* `QualityEvents[machine_id]`
- `DimMachine[machine_id]` 1:* `Maintenance[machine_id]`
- `DimMachine[machine_id]` 1:* `Reliability[machine_id]`
- `DimMachine[machine_id]` 1:* `PredictiveMaintenanceScores[machine_id]`

### Product / supplier / customer

- `DimProduct[product_id]` 1:* `ProductionKPI[product_id]`
- `DimProduct[product_id]` 1:* `QualityEvents[product_id]`
- `DimProduct[product_id]` 1:* `Orders[product_id]`
- `DimSupplier[supplier_id]` 1:* `Supply[supplier_id]`
- `DimCustomer[customer_id]` 1:* `Orders[customer_id]`
- `DimCustomer[customer_id]` 1:* `Shipments[customer_id]`
- `DimCustomer[customer_id]` 1:* `CustomerService[customer_id]`

### Workforce

- `DimPlant[plant_id]` 1:* `Workforce[plant_id]`
- `DimPlant[plant_id]` 1:* `Recruitment[plant_id]`

`DimEmployee` is available for portfolio extension, but the current workforce/recruitment facts are plant-month aggregates and should not be falsely joined to individual employees.

## Modeling rules

- Avoid fact-to-fact joins.
- Avoid many-to-many relationships unless a real bridge table is introduced and documented.
- Mark `DimDate` as the Date table using `DimDate[date]`.
- Hide surrogate/technical key columns from report view where they are not useful to report consumers.
- Keep scenario outputs disconnected unless using a deliberate scenario-selector pattern.
- `ScenarioAssumptions` and `ScenarioMonitoringPlan` are disconnected scenario-evidence marts. They must not filter operational facts or be interpreted as observed outcomes.
- `QualityPareto` and `DecisionQueue` are presentation marts and can remain disconnected.
- `PredictiveMaintenanceModelComparison`, `PredictiveMaintenanceCalibration`, and `PredictiveMaintenanceFeatureImportance` are validation/explainability marts and should remain disconnected from the operational star schema. Use them only on model-validation/reporting surfaces.
- `RootCauseSegments`, `RootCauseAssociations`, `RootCauseGroupTests`, `RootCauseRegression`, `RootCauseTreeImportance`, and `RootCausePriorities` are diagnostic evidence marts. Keep them disconnected; they summarize evidence at mixed grains and must not filter operational facts.
- `DemandForecastModelComparison` and `DemandForecastDiagnostics` are disconnected validation marts. `DemandForecastBacktest` may be used as a disconnected validation surface; do not join it to operational facts merely to drive filters. `DemandForecast` remains the future monthly model-derived forecast table.
- `MORIComponentContributions`, `MORIWeightSensitivity`, and `MORIThresholdSensitivity` are MORI evidence/sensitivity marts. Keep them disconnected from the operational star schema; use them to explain the project-defined index and its robustness rather than to filter operational facts.
- `SixBigLosses`, `CapacityWaterfall`, and `ValueLeakage` are monthly analytical marts; relate them to `DimDate[date]` through `month_date` only, not to detailed facts.
- Do not fabricate relationships for gated metrics such as RTY, DPMO, capability indices, startup rejects, or full COPQ.
- Validate totals after every relationship change to ensure filters do not duplicate fact rows.
