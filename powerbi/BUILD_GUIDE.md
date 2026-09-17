# Power BI Build Guide

## 1. Generate the Power BI handoff

From the repository root in VS Code PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File ".\scripts\phase2_powerbi_prep.ps1"
```

This regenerates the canonical datasets and verifies the required Power BI export files exist.

## 2. Start with Page 1, not the whole report

Build and validate **Enterprise Command Center** first using:

- `PAGE_01_ENTERPRISE_COMMAND_CENTER.md`
- `DAX_MEASURES.md`
- `SEMANTIC_MODEL.md`
- `MEDNEXUS_THEME.json`

Once Page 1 reconciles to the canonical management summary, continue with the remaining pages in `PAGE_SPECIFICATIONS.md`.

## 3. Import data

In Power BI Desktop choose **Get data → Text/CSV** and import the required files from `powerbi/exports/`.

For Page 1, start with only:

- DimDate
- EnterpriseMonthly
- MORI
- DecisionQueue

The full report can then add these domain tables:

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
- QualityPareto
- Reliability
- PredictiveMaintenanceScores
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
- ScenarioOutputs

## 4. Apply the report theme

Apply `powerbi/MEDNEXUS_THEME.json` as the custom report theme before detailed visual formatting. If the installed Power BI Desktop UI uses the newer Theme pane, use **View → Theme pane → Theme settings → Import theme**. On versions showing the classic Themes dropdown, use **View → Themes → Browse for themes**.

Power BI validates imported JSON themes, so stop and correct the file rather than ignoring an import error.

## 5. Data types

- Set `DimDate[date]` to Date.
- Set all `date`, `month`, `month_date`, `order_date`, `ship_date`, `promised_date`, and `actual_delivery_date` fields to Date where appropriate.
- Keep identifiers such as `machine_id`, `plant_id`, `customer_id`, and `order_id` as Text.
- Set rates and percentages to Decimal Number and format them as percentages only when the stored value is a 0–1 rate.
- Set financial fields to Decimal Number / Currency.

## 6. Build the model

Create the relationships in `SEMANTIC_MODEL.md`. Keep relationship filtering single-direction from dimensions to facts unless a documented requirement requires otherwise.

Use `DimDate[date]` as the model's controlled calendar field. Marking it as a Date table is appropriate for classic time-intelligence workflows; current Power BI versions also support calendar-based time intelligence, so use one documented approach consistently rather than mixing date-table behaviors.

## 7. Add measures

Create the measures in `DAX_MEASURES.md`.

For executive KPI cards, use the **Latest ...** measures so an unfiltered report defaults to the latest visible operating month. Use the non-latest measures for historical trend visuals.

Do not sum rate KPIs such as OEE, defect rate, on-time delivery, or capacity-gap percentage.

## 8. Build pages

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

Do not continue past Page 1 until its headline values reconcile to `artifacts/reports/management_summary.md`.

## 9. Required disclosure

Use visible disclosure text where applicable:

**Synthetic enterprise data / Simulated scenario / Model-derived prediction**

Do not describe MEDNEXUS as a real employer, client, or proprietary dataset.

## 10. Validation

Before screenshots or publication:

- Compare executive values to `artifacts/reports/management_summary.md`.
- Confirm no many-to-many relationships were introduced accidentally.
- Verify Date filtering works across monthly and daily facts.
- Check that slicers do not duplicate revenue, production, or shipment totals.
- Validate scenario visuals are clearly labeled **Simulated**.
- Validate prediction visuals are clearly labeled **Model-derived**.
- Confirm MORI is identified as a project-defined composite index.
- Confirm financial proxies are not represented as observed real-company financials.

## 11. Portfolio storage

Save the working local report as `MEDNEXUS_Enterprise_Operational_Intelligence.pbix`.

Do not commit a large `.pbix` file unless there is a specific reason. The repository is designed to retain the reproducible data pipeline, DAX/model specification, documentation, and selected screenshots while generated data and local Power BI binaries remain outside Git.
