# MEDNEXUS Enhanced Enterprise Data Architecture Blueprint

## Purpose

This document converts requirements A01–A32 into an implementation-ready **prototype architecture**.

It is a design contract, not a claim that the expanded dataset already exists.

The current validated MEDNEXUS dataset remains authoritative until this design is prototyped, tested and promoted.

## Core rule

> **Maximum analytical richness per unit of data.**

No table or field is admitted without a traceable business question, KPI, method, model/forecast, risk/scenario, Power BI interaction, decision, or validation purpose.

---

## 1. Preservation strategy

Do not replace validated tables simply to rename them.

Use three change types:

1. **Enrich** — add defensible fields to an existing grain.
2. **Add** — create a new table only when a genuinely different grain/entity/event is required.
3. **Derive** — create analytical/BI marts from curated facts rather than duplicating source-like data.

Existing validated methods/gates remain intact:

- true single-stage FPY;
- RTY/DPMO/capability gates;
- predictive-maintenance leakage controls and uncalibrated-risk labeling;
- MORI/Data Trust project-defined disclosures;
- simulated-scenario labeling;
- optimization/experimentation/full-process-mining gates.

---

## 2. Temporal strategy

Target analytical history is **24–36 months where justified**, but the horizon is determined per domain.

Prototype rule:

- use enough history to validate joins, temporal behavior, YoY/MoM logic, seasonality where appropriate and local performance;
- do not force seasonality;
- use explicit event timestamps for event facts;
- use effective/start/end dates for slowly changing employment/assignment concepts only when required;
- distinguish source/synthetic history, derived outputs, forecasts and simulated scenarios.

Before full expansion, benchmark at least two candidate horizons if the additional history materially affects model quality or Power BI performance.

---

## 3. Candidate conformed dimensions

These are **candidate additions/enrichments**, not automatic final tables.

| Dimension | Proposed grain | Purpose / decision value |
|---|---|---|
| DimRegion | one region | Geographic rollup for plants/customers/suppliers/warehouses |
| DimPlant | one plant | Enrich with synthetic city/country/lat/long/type/capacity |
| DimLine | one production line | Preserve plant hierarchy; add line type/capacity where useful |
| DimMachine | one machine | Preserve; add machine type/commission date/component hierarchy keys where useful |
| DimProduct | one product | Enrich with product family and governed attributes |
| DimShift | one shift definition | Enables shift segmentation without embedding free-text shift repeatedly |
| DimDepartment | one department | Workforce/finance/recruitment conformance |
| DimJobRole | one job role | Workforce/recruitment role/criticality conformance |
| DimSkill | one skill | Skills shortages/training; use bridge for many-to-many employee-role skill associations |
| DimMaterial | one material | Supplier/PO/inventory/production linkage |
| DimWarehouse | one warehouse | Inventory/logistics; synthetic geography/capacity |
| DimSupplier | one supplier | Enrich geography/risk attributes |
| DimCarrier | one carrier | Logistics performance |
| DimRoute | one route | Origin/destination/carrier/logistics segmentation |
| DimCustomer | one healthcare customer | Enrich region/geography/type; no PII |
| DimSystem | one enterprise system | Technology operations |
| DimApplication | one application/service | System→application hierarchy |
| DimCostCenter | one cost center | Finance allocation/governed cost analysis |
| DimBusinessUnit | one business unit | Executive financial/operating segmentation where useful |

Do not add a dimension merely because it appears in this list. Prototype evidence must show it earns its place.

---

## 4. Candidate workforce / recruitment facts

| Fact | Proposed grain | Candidate keys | Primary purpose |
|---|---|---|---|
| FactWorkforceSnapshot | plant/department/role/shift/month | date, plant, department, role, shift | capacity, overtime, absence, utilization, labor cost |
| FactEmploymentEvent | one employee employment event | employee, event timestamp, department/role/plant | hire/transfer/leave/turnover history |
| FactTrainingEvent | one employee-training event | employee, skill/training, date | skill coverage, training completion |
| FactVacancy | one vacancy | role, department, plant, open date | vacancy pressure/criticality |
| FactCandidateEvent | one candidate-stage event | synthetic candidate, vacancy, stage, timestamp | bottlenecks/time in stage |
| FactOnboardingEvent | one accepted-hire onboarding milestone | vacancy/employee, milestone, timestamp | time-to-productivity/onboarding |

Synthetic employee/candidate IDs only. No real identities or unnecessary sensitive fields.

---

## 5. Candidate manufacturing / quality facts

| Fact | Proposed grain | Candidate keys | Primary purpose |
|---|---|---|---|
| FactProductionOrder | one production order | production_order_id, product, plant, line, planned dates | demand/schedule/attainment linkage |
| FactProductionEvent | one order-line-product-shift production event | production_order, line, machine, product, shift, timestamp/date | throughput/OEE/cycle time/loss |
| FactDowntimeEvent | one downtime event | machine, line, start/end, reason | failure/loss/MTTR |
| FactInspectionEvent | one inspection event | inspection_id, production_order, product, stage, machine/line, timestamp | FPY/rework/scrap/defect analysis |
| FactQualityMeasurement | one characteristic measurement | inspection/production order, characteristic, timestamp | SPC/capability only where valid |
| FactMaintenanceEvent | one maintenance event | machine/component, type, start/end | preventive/corrective/backlog/cost |
| FactFailureEvent | one failure occurrence | machine/component/failure mode, timestamp | MTBF/failure Pareto/reliability |

Specification limits live in governed characteristic/specification metadata only when valid. Never generate hidden limits solely to unlock Cp/Cpk.

---

## 6. Candidate supply / inventory facts

| Fact | Proposed grain | Candidate keys | Primary purpose |
|---|---|---|---|
| FactPurchaseOrder | one PO line | PO, supplier, material, order/promised dates | lead time/reliability |
| FactReceipt | one received PO/material lot event | receipt, PO line, lot, warehouse, date | actual receipt/material availability |
| FactMaterialLot | one material lot | lot, material, supplier, receipt | lot traceability/supplier quality |
| FactMaterialConsumption | one production-order material-consumption event | production order, material/lot, date | supplier/material→production linkage |
| FactInventoryMovement | one stock movement | warehouse, item, movement type, timestamp | inventory ledger |
| FactInventorySnapshot | warehouse/item/day or month snapshot | warehouse, item, period | stock, safety stock, excess/stockout |

Inventory ledger validation:

**opening + receipts − consumption ± adjustments = closing**

within documented tolerance.

Do not create impossible negative inventory unless explicitly modeled as a backorder/exception state.

---

## 7. Candidate logistics / customer facts

| Fact | Proposed grain | Candidate keys | Primary purpose |
|---|---|---|---|
| FactOrder | one customer order line | order, customer, product, order date | demand/order volume |
| FactShipment | one shipment | shipment, order/customer, warehouse, carrier, route | fulfillment/logistics |
| FactDeliveryEvent | one shipment lifecycle event | shipment, event type, timestamp | delays/OTIF/process log |
| FactCustomerService | one service issue/request | customer, order/shipment/product where applicable | downstream service risk |

Retain order/shipment as separate facts in BI. Use shared dimensions and event/bridge logic rather than casual fact-to-fact relationships.

---

## 8. Candidate technology facts

| Fact | Proposed grain | Candidate keys | Primary purpose |
|---|---|---|---|
| FactTechnologyIncident | one incident | system/application, severity, start/end | downtime/MTTR/visibility risk |
| FactDeployment | one deployment | application, timestamp, status | failed deployment/reliability |
| FactSupportTicket | one support ticket | application/system, open/resolve dates | workload/response/resolution |
| FactSystemUsage | application/entity/time period | application, date/time | adoption/usage |
| FactDataQualityIncident | one data-quality incident | system/dataset, timestamp, severity | reporting uncertainty/Data Trust |

Technology→operations links are represented only where a documented system/data dependency exists.

---

## 9. Cross-domain link strategy

Key cross-domain identifiers should be introduced only when the business process logically creates them.

Priority links:

- `production_order_id`: production schedule/event ↔ inspection/rework/release ↔ material consumption;
- `material_lot_id`: supplier/receipt ↔ inventory ↔ production consumption ↔ quality where inspected;
- `shipment_id` / `order_id`: fulfillment ↔ delivery events ↔ service issues;
- `vacancy_id`: recruitment events ↔ role/department/plant capacity need;
- `machine_id`: production/downtime/maintenance/failure/sensor/quality;
- `shift_id`: workforce capacity ↔ production/quality where staffing design supports the link;
- `cost_center_id`: finance allocation to governed operating domains where the cost is actually attributable.

Do not manufacture direct fact-to-fact joins in the Power BI model.

---

## 10. Event-log target

A full process case may be admitted only after the necessary link keys/timestamps exist.

Target lifecycle:

**Order Created → Production Scheduled → Production Started → Inspection → Rework (optional) → Release → Shipment → Delivery**

Requirements:

- stable case identifier;
- unique event IDs;
- valid timestamps;
- monotonic process logic or documented exceptions;
- no fabricated missing events;
- explicit optionality for rework;
- process variants derived from real generated event sequences.

Until then, the currently validated order-fulfillment process log remains authoritative.

---

## 11. Geospatial strategy

Use synthetic coordinates only for fictional MEDNEXUS entities.

Required metadata where admitted:

- country;
- region;
- city;
- latitude;
- longitude;
- entity type;
- capacity/risk/status fields where valid.

Coordinates must be plausible and documented as simulated.

Geography must support map analysis, drill/filter context and logistics/supply decisions rather than decorative plotting.

---

## 12. Financial linkage

Prefer a governed cost-event/allocation model rather than embedding duplicated financial fields into every fact.

Candidate approach:

- FactFinanceActual / FactFinanceBudget at financial-period × cost-center × plant/business-unit/product-family grain;
- analytical allocation views for labor, downtime, quality, maintenance, inventory, logistics and technology costs where allocation logic is defensible;
- explicit `Illustrative assumption` labels where a cost rate is project-defined.

No simulated opportunity is presented as realized savings.

---

## 13. Synthetic dependency graph

The generator should encode explicit business-rule dependencies, for example:

- demand pressure → production requirement;
- workforce shortage → available capacity/overtime pressure;
- machine age/operating exposure → simulated failure pressure;
- maintenance intervention → simulated reduction in subsequent failure pressure;
- downtime → available run time/output pressure;
- process variation → quality/rework pressure;
- supplier delay/reliability → receipt/material shortage pressure;
- inventory shortage → production availability pressure;
- production/quality/availability → shipment/backlog pressure;
- delivery performance → service-issue pressure;
- technology/data incidents → reporting/freshness uncertainty.

These are **synthetic generation assumptions**, never empirical causal findings.

Document the dependency graph and parameter assumptions.

---

## 14. Prototype-before-scale gate

Before full expansion:

1. freeze required business questions;
2. define candidate grains;
3. define PK/FK/cardinality;
4. define KPI dependencies;
5. define analytical methods;
6. define minimum fields;
7. generate a small deterministic prototype;
8. validate PK/FK/orphans;
9. validate temporal/event chronology;
10. validate inventory balance;
11. validate KPI calculations;
12. validate SQL/Python reconciliation;
13. validate Power BI filter paths on the prototype;
14. benchmark runtime/storage;
15. reject fields/tables that do not add decision value;
16. promote the accepted design and only then scale entity/history counts.

---

## 15. Promotion criteria

A new table or field can enter the canonical build only when:

- its purpose is documented;
- grain is unambiguous;
- keys/cardinality are validated;
- source/generation rule is documented;
- transformation is traceable;
- quality checks exist;
- at least one business/analytical/decision use exists;
- storage/runtime cost is acceptable;
- Power BI relationship impact is understood;
- disclosures are correct.

---

## 16. Semantic-model consequence

The Phase-12 semantic contract is a preserved baseline, not the final enhanced model.

After prototype promotion:

1. regenerate exports;
2. rebuild table-role contract;
3. reassess conformed dimensions/bridges;
4. prove no ambiguous active paths;
5. validate date roles;
6. update disconnected-evidence marts;
7. regenerate headline reconciliation targets;
8. rerun the full test suite;
9. only then start final flagship PBIX construction.

---

## 17. Data-product metadata

For every promoted table, record:

- table name;
- business purpose;
- grain;
- PK;
- FK(s);
- dimensions;
- measures;
- cardinality;
- source;
- refresh strategy;
- transformation logic;
- owner concept;
- version;
- limitations;
- quality rules;
- lineage;
- Power BI role.

This metadata becomes part of the MEDNEXUS data product rather than informal implementation notes.
