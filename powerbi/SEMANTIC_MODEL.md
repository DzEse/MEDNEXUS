# Power BI Semantic Model

## Enhancement status

This document is the **validated Phase-12 baseline semantic contract**.

The September 2026 enterprise dataset/twin enhancement introduced candidate inventory, warehouse, material, shift, workforce, geospatial and process-event structures. Phase 12E validated the structural prototype. Phase 12F then reviewed every prototype table and approved a limited promotion plan, but **the approved structures are not yet admitted to this canonical contract**.

The current 53-export relationships remain authoritative until Phase 12G physically implements the approved structures and this contract is regenerated. Do not manually add Phase 12F proposed relationships to the PBIX before that regeneration.

The final model uses a **controlled star/snowflake design**. The repository validates the relationship contract before the user builds it in Power BI Desktop.

Machine-readable contract:

- `artifacts/validation/powerbi_semantic_relationships.csv`
- `artifacts/validation/powerbi_table_roles.csv`
- `artifacts/validation/powerbi_semantic_audit.json`

## Phase 12F approved target — not canonical yet

Phase 12F contract simulation proposes a post-promotion target of **58 exports, 45 active relationships and 2 inactive relationships** with **0 semantic issues**.

Approved geography treatment:

- merge simulated Plant geography into DimPlant;
- merge simulated Supplier geography into DimSupplier;
- merge simulated Customer geography into DimCustomer;
- add DimWarehouse as a Plant child;
- do **not** add one shared active DimRegion relationship.

Approved workforce/reference additions:

- DimShift;
- DimDepartment;
- DimJobRole;
- EmployeeAssignment;
- connect the existing DimEmployee to EmployeeAssignment.

Approved proposed paths:

- DimPlant → DimWarehouse;
- DimPlant → EmployeeAssignment;
- DimShift → EmployeeAssignment;
- DimEmployee → EmployeeAssignment;
- DimDepartment → DimJobRole;
- DimJobRole → EmployeeAssignment.

The proposed model deliberately excludes direct DimLine→EmployeeAssignment and DimDepartment→EmployeeAssignment relationships to preserve a single active filter route. High-risk reverse-disaggregated production, recruitment, supply and inventory prototype facts remain outside the canonical model until direct generation replaces pseudo-detail.

This is a **contract simulation**, not actual PBIX validation.

## Core dimensions

- `DimDate` — one row per calendar date; mark as the Date table.
- `DimPlant`
- `DimLine`
- `DimMachine`
- `DimProduct`
- `DimSupplier`
- `DimCustomer`

`DimEmployee` remains disconnected because the current workforce/recruitment facts are plant-month aggregates rather than employee-grain facts.

## Cardinality and filtering rules

Every canonical active relationship is:

- **1:***;
- **single-direction**;
- dimension/hierarchy → fact or mart.

Prohibited unless a future documented bridge requires otherwise:

- many-to-many;
- bidirectional filtering;
- fact-to-fact relationships;
- parallel active paths from the same dimension into the same fact.

## Operations hierarchy — important

Use exactly:

- `DimPlant[plant_id]` 1:* `DimLine[plant_id]`
- `DimLine[line_id]` 1:* `DimMachine[line_id]`

Machine-grain facts then relate through **DimMachine only**:

- `DimMachine[machine_id]` 1:* `ProductionKPI[machine_id]`
- `DimMachine[machine_id]` 1:* `Downtime[machine_id]`
- `DimMachine[machine_id]` 1:* `QualityEvents[machine_id]`
- `DimMachine[machine_id]` 1:* `Maintenance[machine_id]`
- `DimMachine[machine_id]` 1:* `Reliability[machine_id]`
- `DimMachine[machine_id]` 1:* `PredictiveMaintenanceScores[machine_id]`

**Do not create direct active DimPlant→ProductionKPI or DimLine→ProductionKPI relationships.**

Plant and line filtering reaches machine-grain facts through:

`DimPlant → DimLine → DimMachine → Fact`

This removes the prior multiple-active-path risk.

Plant-grain facts/marts connect directly to `DimPlant`:

- Workforce;
- Recruitment;
- QualityPChart.

## Date relationships

Use `DimDate[date]` as the one side.

Canonical active date relationships:

- EnterpriseMonthly → `month_date`
- MORI → `month_date`
- ProductionKPI → `date`
- Downtime → `date`
- QualityEvents → `date`
- Maintenance → `date`
- PredictiveMaintenanceScores → `date`
- Workforce → `month`
- Recruitment → `month`
- Supply → `month`
- Finance → `month`
- DemandForecast → `month`
- Orders → `order_date`
- Shipments → `ship_date`
- CustomerService → `date`
- TechnologyIncidents → `date`
- SaaSUsage → `date`
- QualityPChart → `date`
- SixBigLosses → `month_date`
- CapacityWaterfall → `month_date`
- ValueLeakage → `month_date`

Optional inactive shipment date roles:

- `Shipments[promised_date]`
- `Shipments[actual_delivery_date]`

Use them only with an explicit `USERELATIONSHIP` measure when a business question requires that date role.

## Product / supplier / customer

Product:

- DimProduct → ProductionKPI
- DimProduct → QualityEvents
- DimProduct → Orders

Supplier:

- DimSupplier → Supply

Customer:

- DimCustomer → Orders
- DimCustomer → Shipments
- DimCustomer → CustomerService

Orders and Shipments remain separate facts. Do not create a fact-to-fact relationship merely because both contain `order_id`.

## Enterprise-level marts

`EnterpriseMonthly` and `MORI` relate to `DimDate` only. They are enterprise-wide monthly marts and must not be falsely filtered by plant/product dimensions that do not exist at their grain.

## Explicitly disconnected tables

Keep the following disconnected:

- DimEmployee
- MORIComponentContributions
- MORIWeightSensitivity
- MORIThresholdSensitivity
- ScenarioOutputs
- ScenarioAssumptions
- ScenarioMonitoringPlan
- ProcessEventLog
- ProcessCases
- ProcessTransitions
- DecisionQueue
- QualityPareto
- PredictiveMaintenanceModelComparison
- PredictiveMaintenanceCalibration
- PredictiveMaintenanceFeatureImportance
- RootCauseSegments
- RootCauseAssociations
- RootCauseGroupTests
- RootCauseRegression
- RootCauseTreeImportance
- RootCausePriorities
- DemandForecastBacktest
- DemandForecastModelComparison
- DemandForecastDiagnostics

These tables are evidence, validation, simulated, diagnostic, case-analysis or presentation marts. They must not filter operational facts.

## Validation rule

Before a PBIX is accepted:

1. Build only the relationships in `powerbi_semantic_relationships.csv`.
2. Confirm all active relationships are 1:* and single direction.
3. Confirm exactly one active date relationship per fact.
4. Confirm all disconnected tables remain disconnected.
5. Compare Page 1 headline measures to `powerbi_headline_reconciliation_targets.csv`.
6. Recheck totals after every relationship change.

The repository validates the **contract**. The final PBIX still requires user-side construction and reconciliation in Power BI Desktop.
