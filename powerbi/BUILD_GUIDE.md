# Power BI Build Guide

## Governance first

The final Power BI report is built by the user in Power BI Desktop. The repository does not pretend that a PBIX file has been created.

Before treating the report as final, review:

- `docs/specification/MEDNEXUS_MASTER_BUILD_SPECIFICATION.md`
- `docs/specification/REQUIREMENTS_TRACEABILITY_MATRIX.md`
- `powerbi/SEMANTIC_MODEL.md`
- `powerbi/DAX_MEASURES.md`
- `powerbi/PAGE_SPECIFICATIONS.md`

The existing report work is a **preserved shell** while unresolved predecessor analytical requirements are completed/gated. Final BI acceptance follows analytical reconciliation, not the other way around.

## Current gate before final PBIX

The September 2026 enhancement predecessor work is now closed through Phase 12G:

1. Phase 12E structural prototype — validated;
2. Phase 12F promotion/filter-behavior decision — validated;
3. Phase 12G canonical promotion — validated;
4. canonical contract — 58 exports, 45 active relationships, 2 inactive shipment date roles, 0 semantic issues;
5. Data Trust — 100/100.

The active repository-to-Power-BI transition is **Phase 12H — Power BI Desktop handoff and reconciliation preparation**.

Before building or refreshing the final PBIX, run:

```powershell
powershell -ExecutionPolicy Bypass -File ".\\scripts\\phase12h_powerbi_handoff_prep.ps1"
```

Then follow:

- `powerbi/PHASE_12H_DESKTOP_HANDOFF.md`
- `powerbi/handoff/import_plan.csv`
- `powerbi/handoff/relationship_build_order.csv`
- `powerbi/handoff/headline_reconciliation_checklist.csv`
- `powerbi/handoff/pbix_acceptance_checklist.csv`

The handoff files are build/control templates. They do **not** claim that a PBIX has been built, reconciled or validated.

## 1. Generate the Power BI handoff

From the repository root in VS Code PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File ".\scripts\phase12h_powerbi_handoff_prep.ps1"
```

This validates the current 58-export canonical package and generates the Desktop import, relationship, reconciliation and acceptance control files. Run `phase2_powerbi_prep.ps1` only when you intentionally need to regenerate the underlying canonical exports.

## 2. Preserve Page 1 as the baseline report shell

Preserve/review the existing **Enterprise Command Center** semantic/visual shell using:

- `PAGE_01_ENTERPRISE_COMMAND_CENTER.md`
- `DAX_MEASURES.md`
- `SEMANTIC_MODEL.md`
- `MEDNEXUS_THEME.json`

Do not treat the page as final. The flagship target now also requires the enhanced dataset/twin prototype, regenerated semantic contract, global navigation, map/twin/value-loss/risk/forecast/scenario/decision interactions and real PBIX reconciliation.

## 3. Import data

In Power BI Desktop choose **Get data → Text/CSV** and import the required files from `powerbi/exports/`.

Build the final model from `powerbi/handoff/import_plan.csv`. Load connected tables first, validate the semantic model and headline measures, then load disconnected evidence tables. The current canonical exports include:

- DimPlant
- DimLine
- DimMachine
- DimProduct
- DimSupplier
- DimCustomer
- DimEmployee
- ProductionKPI
- Downtime
- QualityEvents
- Maintenance
- MORIComponentContributions
- MORIWeightSensitivity
- MORIThresholdSensitivity
- QualityPareto
- QualityPChart
- SixBigLosses
- CapacityWaterfall
- ValueLeakage
- Reliability
- PredictiveMaintenanceScores
- PredictiveMaintenanceModelComparison
- PredictiveMaintenanceCalibration
- PredictiveMaintenanceFeatureImportance
- RootCauseSegments
- RootCauseAssociations
- RootCauseGroupTests
- RootCauseRegression
- RootCauseTreeImportance
- RootCausePriorities
- Finance
- Workforce
- Recruitment
- Supply
- Orders
- Shipments
- CustomerService
- TechnologyIncidents
- SaaSUsage
- DemandForecast
- DemandForecastBacktest
- DemandForecastModelComparison
- DemandForecastDiagnostics
- ScenarioOutputs
- ScenarioAssumptions
- ScenarioMonitoringPlan
- ProcessEventLog
- ProcessCases
- ProcessTransitions

The current accepted canonical contract is fixed at 58 exports for the Phase 12H PBIX build. Rework-required/deferred prototype structures remain excluded. Never add them manually in Power BI.

## 4. Apply the report theme

Apply `powerbi/MEDNEXUS_THEME.json` as the custom report theme before detailed visual formatting.

Power BI validates imported JSON themes, so correct any import error rather than ignoring it.

## 5. Data types

- Set `DimDate[date]` to Date.
- Set all `date`, `month`, `month_date`, `order_date`, `ship_date`, `promised_date`, and `actual_delivery_date` fields to Date where appropriate.
- Keep identifiers such as `machine_id`, `plant_id`, `customer_id`, and `order_id` as Text.
- Set rates and percentages to Decimal Number and format them as percentages only when the stored value is a 0–1 rate.
- Set financial fields to Decimal Number / Currency.
- Do not format MORI as a percentage.

## 6. Build the model

Create the relationships in `SEMANTIC_MODEL.md`.

Rules:

- use only the machine-readable canonical relationship contract;
- one-to-many for every canonical relationship;
- single-direction filtering from dimensions/hierarchy to facts;
- for machine-grain facts, filter Plant → Line → Machine → Fact; do not add direct parallel Plant/Line paths;
- no fact-to-fact relationships merely for convenience;
- no many-to-many relationship without a documented bridge/grain rationale;
- only one active date path per fact unless a deliberate inactive date role is activated by a measure;
- use `DimDate[date]` as the controlled model date;
- keep disconnected scenario/presentation tables disconnected where documented.

Validate totals after every relationship change.

## 7. Add measures

Create measures from `DAX_MEASURES.md`.

Key rules:

- executive cards use `Latest ...` measures;
- historical charts use trend/context measures;
- do not sum OEE, OLI, defect rates, delivery rates, capacity rates or other percentage KPIs;
- true FPY/RTY/DPMO measures are added only after their canonical data semantics are validated;
- simulated/illustrative/model-derived measures retain their labels and tooltips.

## 8. Build the canonical 13-question report story

1. **Enterprise Command Center** — Where is MEDNEXUS losing operational value?
2. **Finance & Business Health** — Where is financial performance being pressured?
3. **People, HR & Workforce** — Do we have the people and capacity required to operate the business?
4. **Recruitment & Capacity** — Where are talent gaps becoming operational constraints?
5. **Manufacturing Performance** — Where is productive capacity being lost?
6. **Quality & Process Intelligence** — Where are defects and process instability originating?
7. **Equipment & Reliability** — Which assets represent the greatest operational risk?
8. **Supply Chain & Inventory** — Are materials and suppliers constraining operations?
9. **Logistics & Customer Service** — Where are delivery and service failures occurring?
10. **Healthcare Customer Operations** — How does enterprise performance translate into downstream customer service?
11. **Technology / Data Operations** — Can MEDNEXUS trust the systems and data supporting its decisions?
12. **Prediction, Forecast & Risk** — What is likely to happen next?
13. **Scenario & Decision Intelligence** — What should management do?

Detailed requirements are in `PAGE_SPECIFICATIONS.md`.

A future consolidation is acceptable only if no business question, evidence layer, interaction or disclosure is lost.

## 9. Page 1 requirements

The executive page must visibly cover:

- revenue/cost/margin;
- workforce/capacity;
- production;
- quality;
- supply risk;
- logistics/service;
- technology health;
- OEE/OLI;
- MORI;
- value-loss drivers;
- management decision queue.

Use a compact enterprise-health strip rather than creating an excessive number of large KPI cards.

## 10. Advanced Power BI features

Use only when they improve analysis:

- drill-through for plant/line/machine/product/customer/supplier detail;
- tooltip pages for definitions, provenance, assumptions and limitations;
- bookmarks for executive/detail navigation;
- field parameters for legitimate measure/dimension switching;
- what-if parameters for scenario assumptions;
- dynamic titles for selected period/entity/scenario;
- conditional formatting based on documented thresholds;
- decomposition tree for diagnostic association;
- Key Influencers only when input data and interpretation are defensible;
- executive commentary distinguishing evidence, hypothesis and simulated recommendation.

Avoid decorative use of advanced features.

## 11. Required disclosures

Use visible wording where applicable:

- **Synthetic enterprise data**
- **Illustrative assumption**
- **Model-derived**
- **Simulated**
- **Project-defined index/metric**

Do not describe MEDNEXUS as a real employer, client or proprietary dataset.

## 12. Validation

Before screenshots/publication:

- compare executive totals to the latest generated management summary;
- reconcile Power BI to curated/SQLite outputs;
- verify no accidental many-to-many or ambiguous relationship exists;
- verify Date filtering works across the intended facts;
- verify slicers do not multiply revenue, production or shipment totals;
- verify Page 1 includes every required enterprise-health domain;
- verify scenario visuals are clearly **Simulated**;
- verify prediction/forecast visuals are **Model-derived**;
- verify MORI/Data Trust/OLI are described as project-defined where applicable;
- verify FPY/RTY/DPMO/capability/control visuals only exist after upstream validity gates pass;
- verify all displayed assumptions/limitations are traceable.

## 13. Portfolio storage

Save the local working report as:

`MEDNEXUS_Enterprise_Operational_Intelligence.pbix`

Do not commit a large `.pbix` file unless a specific portfolio reason outweighs the storage cost. Retain the reproducible pipeline, model/DAX/page documentation and selected **validated** screenshots.

Export final screenshots to `powerbi/screenshots/` only after reconciliation and analytical closure.
