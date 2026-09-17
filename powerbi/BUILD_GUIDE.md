# Power BI Build Guide

## 1. Generate the Power BI handoff

From the repository root in VS Code PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File ".\scripts\phase2_powerbi_prep.ps1"
```

This regenerates the canonical datasets and verifies the required Power BI export files exist.

## 2. Import data

In Power BI Desktop choose **Get data → Text/CSV** and import the required files from `powerbi/exports/`.

Start with these core tables:

- DimDate
- DimPlant
- DimLine
- DimMachine
- DimProduct
- DimSupplier
- DimCustomer
- EnterpriseMonthly
- ProductionKPI
- MORI
- DecisionQueue
- Finance
- Workforce
- Recruitment
- Supply
- Orders
- Shipments
- CustomerService
- TechnologyIncidents
- ScenarioOutputs

Then add the specialist drill-through tables as needed:

- Downtime
- QualityEvents
- Maintenance
- QualityPareto
- Reliability
- PredictiveMaintenanceScores
- DemandForecast
- SaaSUsage

## 3. Data types

- Set `DimDate[date]` to Date.
- Set all `date`, `month`, `month_date`, `order_date`, `ship_date`, `promised_date`, and `actual_delivery_date` fields to Date where appropriate.
- Keep identifiers such as `machine_id`, `plant_id`, `customer_id`, and `order_id` as Text.
- Set rates and percentages to Decimal Number and format them as percentages only when the stored value is a 0–1 rate.
- Set financial fields to Decimal Number / Currency.

## 4. Build the model

Create the relationships in `SEMANTIC_MODEL.md`. Keep relationship filtering single-direction from dimensions to facts unless a documented requirement requires otherwise.

Mark `DimDate` as the model Date table using `DimDate[date]`.

## 5. Add measures

Create the measures in `DAX_MEASURES.md`. Do not sum rate KPIs such as OEE, defect rate, on-time delivery, or capacity-gap percentage.

## 6. Build pages

Build pages in the sequence defined in `PAGE_SPECIFICATIONS.md`:

1. Enterprise Command Center
2. Finance & Business Health
3. People & Recruitment
4. Manufacturing & Quality
5. Equipment & Reliability
6. Supply Chain & Logistics
7. Healthcare Customer Service
8. Technology & Data Trust
9. Prediction / Forecast / Risk
10. Scenario & Decision Intelligence

Build **Enterprise Command Center first** and validate it before continuing.

## 7. Required disclosure

Use visible disclosure text where applicable:

**Synthetic enterprise data / Simulated scenario / Model-derived prediction**

Do not describe MEDNEXUS as a real employer, client, or proprietary dataset.

## 8. Validation

Before screenshots or publication:

- Compare executive totals to `artifacts/reports/management_summary.md`.
- Confirm no many-to-many relationships were introduced accidentally.
- Verify Date filtering works across monthly and daily facts.
- Check that slicers do not duplicate revenue, production, or shipment totals.
- Validate scenario visuals are clearly labeled **Simulated**.
- Validate prediction visuals are clearly labeled **Model-derived**.

## 9. Portfolio storage

Do not commit a large `.pbix` file unless there is a specific reason. The repository is designed to retain the reproducible data pipeline, DAX/model specification, documentation, and selected screenshots while generated data and local Power BI binaries remain outside Git.
