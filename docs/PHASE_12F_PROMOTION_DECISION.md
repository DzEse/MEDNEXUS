# Phase 12F — Prototype Promotion & Power BI Filter-Behavior Decision

## Status

**VALIDATED — APPROVED PROMOTION PLAN, NOT YET APPLIED**

Phase 12F evaluates every Phase 12E.1 structural prototype against MEDNEXUS business value, grain integrity, semantic-model safety and Power BI filter behavior.

It does **not** mutate the current canonical 53-export Power BI contract. The purpose is to decide what is safe to implement next and what must remain gated.

## Full validation result

- Prototype structures reviewed: **20**
- Approved for canonical implementation: **8**
- New export candidates: **5**
- Existing-dimension geography merges: **3**
- Rework required before promotion: **8**
- Deferred: **3**
- Redundant / deliberately not promoted: **1**
- Proposed post-promotion exports: **58**
- Proposed active relationships: **45**
- Proposed inactive relationships: **2**
- Filter-behavior checks: **29**
- Filter-behavior failures: **0**
- Semantic issues: **0**
- Actual PBIX validated: **No**
- Power BI validation scope: **contract simulation, not actual PBIX inspection**

## Approved structures

### Geography — merge, do not duplicate dimensions

The following are approved as attribute merges into existing dimensions:

- dim_plant_geo → DimPlant
- dim_supplier_geo → DimSupplier
- dim_customer_geo → DimCustomer

Approved fields are role-specific geography attributes such as country, region, city, latitude, longitude and the explicit label:

SIMULATED_ENTERPRISE_FOOTPRINT

No shared active DimRegion relationship is admitted. A single Region dimension spanning plant, supplier and customer geography would mix different geographic business roles and could create misleading global-filter semantics.

### New canonical export candidates

- DimWarehouse
- DimShift
- DimDepartment
- DimJobRole
- EmployeeAssignment

DimEmployee is already exported but is proposed to move from disconnected to connected because the approved current employee-assignment snapshot provides a defensible employee-grain relationship.

## Proposed new relationship paths

Only the following additions are approved:

- DimPlant → DimWarehouse
- DimPlant → EmployeeAssignment
- DimShift → EmployeeAssignment
- DimEmployee → EmployeeAssignment
- DimDepartment → DimJobRole
- DimJobRole → EmployeeAssignment

All remain:

- 1:*;
- single direction;
- dimension/hierarchy → fact/reference.

Important exclusions:

- no DimLine → EmployeeAssignment active relationship;
- no direct DimDepartment → EmployeeAssignment relationship;
- no global connected DimRegion;
- no new fact-to-fact relationship;
- no bidirectional relationship;
- no many-to-many relationship.

The Department workforce filter path is deliberately:

DimDepartment → DimJobRole → EmployeeAssignment

This creates one active route only.

## Rework required before promotion

The following passed structural prototype checks but are **not decision-ready canonical facts**:

- fact_vacancy
- fact_candidate_event
- fact_production_event
- fact_inspection_event
- fact_purchase_order
- fact_receipt
- fact_inventory_movement
- fact_inventory_snapshot

Why they remain gated:

- vacancy/candidate events are currently disaggregated from monthly recruitment aggregates;
- production events are a deliberate 50/50 split used to prove event-grain mechanics, not genuine shift variation;
- inspection events prove linkage but do not yet represent independent sampling/process-stage behavior;
- PO and receipt records are reverse-disaggregated from monthly supplier facts;
- inventory balances reconcile, but consumption uses an explicit scaled production-demand proxy.

The next canonical version must generate these event facts directly and derive aggregates upward, not infer pseudo-detail downward from aggregates.

## Deferred structures

- dim_region — defer as a connected dimension because geography has distinct plant/supplier/customer roles.
- dim_material — defer until direct canonical purchasing/receipt/inventory generation exists.
- bridge_product_material — defer until material flow is canonical and a bridge is genuinely required.

## Deliberately not promoted

fact_order_fulfillment_event is not promoted because MEDNEXUS already has a validated source-backed order-fulfillment process event log. Duplicating it would add storage/model complexity without additional decision value.

## Power BI filter-behavior result

The Phase 12F contract simulation proves:

- no ambiguous active paths in the proposed model;
- Plant filters EmployeeAssignment through one direct path;
- Shift filters EmployeeAssignment without falsely filtering production;
- Employee filters one current assignment;
- Department filters EmployeeAssignment through JobRole only;
- Plant filters Warehouse safely;
- geography merges preserve dimension grain and coordinate validity;
- unready prototype facts remain outside the proposed canonical export target.

This is **not** evidence that a PBIX file has been built or inspected.

## Next gate

Phase 12G should physically implement only the approved structures, then:

1. regenerate canonical synthetic exports;
2. expand the table/data dictionary;
3. regenerate the Power BI semantic contract;
4. validate the new 58-export package;
5. rerun ambiguity/orphan/date-role checks;
6. regenerate headline reconciliation targets;
7. run the full regression suite;
8. only then hand the enhanced model to Power BI Desktop for actual relationship and measure reconciliation.
