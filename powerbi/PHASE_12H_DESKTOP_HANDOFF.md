# Phase 12H — Power BI Desktop Model Handoff & Reconciliation

## Status

**REPOSITORY HANDOFF PREPARED — PBIX NOT YET BUILT OR VALIDATED**

Phase 12G closed the canonical data/model contract. Phase 12H is the transition from repository validation to actual Power BI Desktop construction.

Canonical contract:

- 58 Power BI exports;
- 35 connected tables;
- 23 disconnected evidence/presentation tables;
- 45 active relationships;
- 2 inactive shipment date roles;
- 0 repository semantic issues;
- Data Trust 100/100.

This phase must never mark PBIX checks as passed automatically. Every PBIX status begins as:

NOT_YET_VALIDATED_IN_PBIX

## Generated handoff files

Run the Phase 12H prep runner before opening or refreshing the final PBIX.

It creates:

- powerbi/handoff/import_plan.csv
- powerbi/handoff/relationship_build_order.csv
- powerbi/handoff/headline_reconciliation_checklist.csv
- powerbi/handoff/pbix_acceptance_checklist.csv
- powerbi/handoff/handoff_summary.json

These are build/control files, not proof that Power BI Desktop has already been validated.

## Working PBIX

Save the local report as:

MEDNEXUS_Enterprise_Operational_Intelligence.pbix

Do not commit the PBIX unless a later portfolio decision explicitly changes the repository policy.

## Build Wave 1 — connected canonical model only

Open Power BI Desktop.

Import the CSVs from:

powerbi/exports/

Start with all rows in import_plan.csv where:

model_status = CONNECTED

This is the controlled model-building wave.

Connected dimensions:

1. DimDate
2. DimPlant
3. DimLine
4. DimMachine
5. DimProduct
6. DimSupplier
7. DimCustomer
8. DimEmployee
9. DimWarehouse
10. DimShift
11. DimDepartment
12. DimJobRole

Connected operational/analytical tables:

- EnterpriseMonthly
- ProductionKPI
- Downtime
- QualityEvents
- Maintenance
- MORI
- QualityPChart
- SixBigLosses
- CapacityWaterfall
- ValueLeakage
- Reliability
- PredictiveMaintenanceScores
- DemandForecast
- Finance
- Workforce
- Recruitment
- Supply
- Orders
- Shipments
- CustomerService
- TechnologyIncidents
- SaaSUsage
- EmployeeAssignment

Do not create any relationship automatically that is absent from relationship_build_order.csv.

If Power BI auto-detect creates extra relationships, delete or deactivate them before proceeding.

## Data type gate

Before relationship construction:

- DimDate[date] = Date
- all date/month/month_date/order_date/ship_date/promised_date/actual_delivery_date fields = Date where they represent dates
- identifiers ending in _id = Text
- latitude/longitude = Decimal Number
- rates stored 0–1 = Decimal Number, formatted as Percentage only when semantically appropriate
- currency/cost/revenue fields = Decimal Number / Currency
- MORI = Decimal Number, not Percentage

Mark DimDate as the Date table using DimDate[date].

## Build Wave 2 — relationships

Use:

powerbi/handoff/relationship_build_order.csv

Create relationships in build_sequence order.

Every relationship must use:

- cardinality: One to many (1:*)
- cross-filter direction: Single
- active = value in the contract

Required hierarchy:

DimPlant → DimLine → DimMachine → machine-grain fact

Never add direct active:

- DimPlant → ProductionKPI
- DimLine → ProductionKPI
- DimLine → EmployeeAssignment
- DimDepartment → EmployeeAssignment
- any shared active DimRegion relationship

Approved workforce path:

DimDepartment → DimJobRole → EmployeeAssignment

Additional independent filters into EmployeeAssignment:

- DimPlant
- DimShift
- DimEmployee

Approved warehouse path:

DimPlant → DimWarehouse

Exactly two relationships must be inactive:

- DimDate[date] → Shipments[promised_date]
- DimDate[date] → Shipments[actual_delivery_date]

The active shipment date relationship remains:

DimDate[date] → Shipments[ship_date]

## Relationship acceptance checkpoint

Before adding DAX or visuals, confirm:

- 45 active relationships
- 2 inactive relationships
- no many-to-many
- no bidirectional filtering
- no fact-to-fact relationships
- no unexpected auto-detected relationship
- all one-side keys show 1 rather than *
- disconnected tables have not been loaded yet

If any count differs, do not continue to visual construction.

## Build Wave 3 — headline reconciliation

Create the executive measures from:

powerbi/DAX_MEASURES.md

Start with the 19 rows in:

powerbi/handoff/headline_reconciliation_checklist.csv

With no date filter applied, the latest operating month is August 2026.

Expected anchor values include:

- Latest Revenue: 79,962,618.61
- Latest Operating Cost: 31,046,396.29345631
- Latest Operating Margin Proxy: 48,916,222.31654369
- Latest OEE: 0.7871550824396587
- Latest OLI: 0.23273266727511877
- Latest FPY: 0.9715715820254223
- Latest Defect Rate: 0.028428417974577787
- Latest On-Time Delivery: 0.579175704989154
- Latest Capacity Gap %: 0.07548076923076924
- Latest Supplier Reliability: 0.9021237982840995
- Latest MORI: 70.05450716728754
- Latest MORI Band: Elevated

Use the exact generated checklist as the authority if regenerated values ever change.

For every target record:

1. create/use the documented DAX measure;
2. display the actual PBIX value;
3. compare to expected value;
4. calculate variance;
5. apply the generated tolerance;
6. record PASS only after the actual value matches within tolerance;
7. add a real evidence reference.

Do not mark blank checks PASS.

## Build Wave 4 — filter behavior

Test the following before Page 1:

### Operations

Select one Plant.

Confirm:

- Lines reduce correctly;
- Machines reduce correctly;
- ProductionKPI/Downtime/Quality/Maintenance follow through Plant→Line→Machine;
- enterprise-only marts such as EnterpriseMonthly and MORI do not falsely become plant-specific.

### Workforce

Select one Department.

Confirm EmployeeAssignment filters through:

DimDepartment → DimJobRole → EmployeeAssignment

Select one Shift.

Confirm EmployeeAssignment filters, while ProductionKPI does not falsely change because true shift production is still gated.

### Geography

Use geography only from the entity being analyzed:

- plant geography from DimPlant;
- supplier geography from DimSupplier;
- customer geography from DimCustomer;
- warehouse geography from DimWarehouse.

Visible map label:

SIMULATED ENTERPRISE FOOTPRINT

Do not create one universal Region relationship.

### Date roles

Confirm Shipments responds to DimDate using ship_date by default.

Promised-date or actual-delivery-date analysis must use an explicit USERELATIONSHIP measure.

## Build Wave 5 — disconnected evidence tables

Only after the connected model and headline reconciliation pass, import the rows in import_plan.csv where:

model_status = DISCONNECTED

These tables must remain disconnected.

They include model validation, MORI sensitivity, root-cause evidence, scenarios, process evidence, forecast validation, DecisionQueue and presentation marts.

They may be used in dedicated visuals, tooltips and evidence pages but must not filter operational facts.

## Build Wave 6 — PBIX acceptance checklist

Use:

powerbi/handoff/pbix_acceptance_checklist.csv

All 30 checks begin as:

NOT_YET_VALIDATED_IN_PBIX

Change a check to PASS only after inspecting the actual PBIX.

Evidence must come from the actual model/report.

Valid evidence examples:

- Model view screenshot showing the required relationship;
- relationship properties screenshot;
- reconciliation card/table screenshot;
- filter-behavior before/after screenshot;
- date-table configuration screenshot;
- page screenshot showing required disclosure.

Store accepted reconciliation evidence under:

evidence/powerbi_reconciliation/

Do not fabricate or pre-populate screenshots.

## Command Center build boundary

Do not style/build the flagship Command Center until the model/reconciliation checklist is technically clean.

After model acceptance, build Page 1 according to:

- powerbi/PAGE_01_ENTERPRISE_COMMAND_CENTER.md
- powerbi/EXECUTIVE_COMMAND_CENTER_BLUEPRINT.md
- powerbi/PAGE_SPECIFICATIONS.md
- powerbi/DAX_MEASURES.md

Required lifecycle:

OBSERVE → DIAGNOSE → QUANTIFY → PREDICT → PRIORITIZE → SIMULATE → DECIDE → MONITOR → LEARN

Required visible disclosures where applicable:

- Synthetic enterprise data
- Illustrative assumption
- Model-derived
- Simulated
- Project-defined index/metric
- SIMULATED ENTERPRISE FOOTPRINT

## Phase 12H closure rule

Repository preparation may be marked PASS.

PBIX validation may not be marked PASS until:

- the actual PBIX exists;
- relationship counts and properties match;
- all headline targets reconcile;
- filter behavior is tested;
- all required disclosures are present;
- real evidence is captured.

Until then:

PBIX_BUILD_STATUS = IN_PROGRESS
PBIX_MODEL_VALIDATED = False
