# Core DAX Measures

These measures are designed for the MEDNEXUS semantic model documented in `SEMANTIC_MODEL.md`.

## Executive-period helpers

The Enterprise Command Center should default to the latest visible operating month rather than summing all monthly periods into a single KPI card.

```DAX
Latest Visible Month =
MAX(EnterpriseMonthly[month_date])

Latest Revenue =
VAR _period = [Latest Visible Month]
RETURN
    CALCULATE(
        SUM(EnterpriseMonthly[revenue]),
        KEEPFILTERS(EnterpriseMonthly[month_date] = _period)
    )

Latest Operating Cost =
VAR _period = [Latest Visible Month]
RETURN
    CALCULATE(
        SUM(EnterpriseMonthly[operating_cost]),
        KEEPFILTERS(EnterpriseMonthly[month_date] = _period)
    )

Latest Operating Margin Proxy =
[Latest Revenue] - [Latest Operating Cost]

Latest Operating Margin % Proxy =
DIVIDE([Latest Operating Margin Proxy], [Latest Revenue])

Latest Gross Margin Proxy =
VAR _period = [Latest Visible Month]
RETURN
    CALCULATE(
        SUM(EnterpriseMonthly[gross_margin_proxy]),
        KEEPFILTERS(EnterpriseMonthly[month_date] = _period)
    )

Latest OEE =
VAR _period = [Latest Visible Month]
RETURN
    CALCULATE(
        AVERAGE(EnterpriseMonthly[oee]),
        KEEPFILTERS(EnterpriseMonthly[month_date] = _period)
    )

Latest OLI =
VAR _period = [Latest Visible Month]
RETURN
    CALCULATE(
        AVERAGE(EnterpriseMonthly[oli]),
        KEEPFILTERS(EnterpriseMonthly[month_date] = _period)
    )

Latest FPY Proxy =
VAR _period = [Latest Visible Month]
RETURN
    CALCULATE(
        AVERAGE(EnterpriseMonthly[fpy]),
        KEEPFILTERS(EnterpriseMonthly[month_date] = _period)
    )

Latest Total Units =
VAR _period = [Latest Visible Month]
RETURN
    CALCULATE(
        SUM(EnterpriseMonthly[total_units]),
        KEEPFILTERS(EnterpriseMonthly[month_date] = _period)
    )

Latest Good Units =
VAR _period = [Latest Visible Month]
RETURN
    CALCULATE(
        SUM(EnterpriseMonthly[good_units]),
        KEEPFILTERS(EnterpriseMonthly[month_date] = _period)
    )

Latest Defect Units =
VAR _period = [Latest Visible Month]
RETURN
    CALCULATE(
        SUM(EnterpriseMonthly[defect_units]),
        KEEPFILTERS(EnterpriseMonthly[month_date] = _period)
    )

Latest Defect Rate =
DIVIDE([Latest Defect Units], [Latest Total Units])

Latest On-Time Delivery =
VAR _period = [Latest Visible Month]
RETURN
    CALCULATE(
        AVERAGE(EnterpriseMonthly[on_time_delivery]),
        KEEPFILTERS(EnterpriseMonthly[month_date] = _period)
    )

Latest Capacity Gap % =
VAR _period = [Latest Visible Month]
RETURN
    CALCULATE(
        AVERAGE(EnterpriseMonthly[capacity_gap_pct]),
        KEEPFILTERS(EnterpriseMonthly[month_date] = _period)
    )

Latest Vacancies =
VAR _period = [Latest Visible Month]
RETURN
    CALCULATE(
        SUM(EnterpriseMonthly[vacancies]),
        KEEPFILTERS(EnterpriseMonthly[month_date] = _period)
    )

Latest Supplier Reliability =
VAR _period = [Latest Visible Month]
RETURN
    CALCULATE(
        AVERAGE(EnterpriseMonthly[supplier_reliability]),
        KEEPFILTERS(EnterpriseMonthly[month_date] = _period)
    )

Latest Shortage Hours =
VAR _period = [Latest Visible Month]
RETURN
    CALCULATE(
        SUM(EnterpriseMonthly[shortage_hours]),
        KEEPFILTERS(EnterpriseMonthly[month_date] = _period)
    )

Latest Technology Downtime Minutes =
VAR _period = [Latest Visible Month]
RETURN
    CALCULATE(
        SUM(EnterpriseMonthly[technology_downtime_min]),
        KEEPFILTERS(EnterpriseMonthly[month_date] = _period)
    )

Latest Major Technology Incidents =
VAR _period = [Latest Visible Month]
RETURN
    CALCULATE(
        SUM(EnterpriseMonthly[major_incidents]),
        KEEPFILTERS(EnterpriseMonthly[month_date] = _period)
    )

Latest MORI =
VAR _period = [Latest Visible Month]
RETURN
    CALCULATE(
        MAX(MORI[mori_score]),
        KEEPFILTERS(MORI[month_date] = _period)
    )

Latest MORI Band =
VAR _period = [Latest Visible Month]
RETURN
    CALCULATE(
        SELECTEDVALUE(MORI[mori_band]),
        KEEPFILTERS(MORI[month_date] = _period)
    )
```

## Trend measures

Use these on time-series visuals where `DimDate[month_start]`, `DimDate[year_month]`, or the relevant monthly date is already on the axis.

```DAX
Revenue = SUM(EnterpriseMonthly[revenue])
Operating Cost = SUM(EnterpriseMonthly[operating_cost])
Operating Margin Proxy = [Revenue] - [Operating Cost]
Operating Margin % Proxy = DIVIDE([Operating Margin Proxy], [Revenue])
Gross Margin Proxy = SUM(EnterpriseMonthly[gross_margin_proxy])
Total Enterprise Units = SUM(EnterpriseMonthly[total_units])
Enterprise Defect Units = SUM(EnterpriseMonthly[defect_units])
Enterprise Defect Rate = DIVIDE([Enterprise Defect Units], [Total Enterprise Units])
Average OLI = AVERAGE(EnterpriseMonthly[oli])
On-Time Delivery = AVERAGE(EnterpriseMonthly[on_time_delivery])
Capacity Gap % = AVERAGE(EnterpriseMonthly[capacity_gap_pct])
Supplier Reliability = AVERAGE(EnterpriseMonthly[supplier_reliability])
Technology Downtime Minutes = SUM(EnterpriseMonthly[technology_downtime_min])
Major Technology Incidents = SUM(EnterpriseMonthly[major_incidents])
MORI Score = MAX(MORI[mori_score])
```

## Detailed manufacturing measures

Use these for manufacturing and drill-through pages. They are calculated from the detailed `ProductionKPI` grain rather than copied from the executive monthly mart.

```DAX
Total Units = SUM(ProductionKPI[total_count])
Good Units = SUM(ProductionKPI[good_count])
Defect Units = SUM(ProductionKPI[defect_units])
Scrap Units = SUM(ProductionKPI[scrap_units])
Rework Units = SUM(ProductionKPI[rework_units])

Availability =
DIVIDE(
    SUM(ProductionKPI[run_time_min]),
    SUM(ProductionKPI[planned_production_min]) - SUM(ProductionKPI[planned_downtime_min])
)

Performance =
DIVIDE(
    SUMX(
        ProductionKPI,
        ProductionKPI[ideal_cycle_min] * ProductionKPI[total_count]
    ),
    SUM(ProductionKPI[run_time_min])
)

Quality Rate = DIVIDE([Good Units], [Total Units])
OEE = [Availability] * [Performance] * [Quality Rate]
Defect Rate = DIVIDE([Defect Units], [Total Units])
Scrap Rate = DIVIDE([Scrap Units], [Total Units])
Rework Rate = DIVIDE([Rework Units], [Total Units])
```

`FPY`, `RTY` and `DPMO` require their canonical data semantics. Do not substitute the current `fpy` proxy for a final true FPY measure without validating rework/pass definitions. RTY requires sequential process-stage yields. DPMO requires a defensible number of defect opportunities per unit.

## Logistics, people, and reliability measures

```DAX
Shipment Count = COUNTROWS(Shipments)
On-Time Shipments = SUM(Shipments[on_time_flag])
Detailed On-Time Delivery = DIVIDE([On-Time Shipments], [Shipment Count])
Average Delivery Delay Days = AVERAGE(Shipments[delay_days])

Required Headcount = SUM(Workforce[required_headcount])
Actual Headcount = SUM(Workforce[actual_headcount])
Vacancies = SUM(Workforce[vacancies])
Average Absence Rate = AVERAGE(Workforce[absence_rate])
Average Overtime Hours = AVERAGE(Workforce[overtime_hours_per_employee])

Unplanned Downtime Minutes = SUM(Downtime[duration_min])
Maintenance Events = COUNTROWS(Maintenance)
Average Maintenance Duration Minutes = AVERAGE(Maintenance[duration_min])
Average Failure Risk = AVERAGE(PredictiveMaintenanceScores[failure_risk])
Predicted Failure Flags = SUM(PredictiveMaintenanceScores[predicted_failure_flag])
```

## Scenario measures

`ScenarioOutputs` is intentionally disconnected. These measures report the selected simulated scenario without implying causal certainty.

```DAX
Selected Scenario =
SELECTEDVALUE(ScenarioOutputs[scenario], "Baseline")

Scenario Opportunity Value =
SUM(ScenarioOutputs[simulated_opportunity_value])

Scenario Good Units =
SUM(ScenarioOutputs[simulated_good_units])

Scenario Downtime Minutes =
SUM(ScenarioOutputs[simulated_downtime_min])
```

The scenario layer will be expanded to the canonical Baseline → Assumption → Expected Change → Result → Difference design before final report acceptance.

## Formatting guidance

- Currency: `$#,0;($#,0)` or the report's chosen local currency convention.
- OEE / OLI / FPY / delivery / capacity / reliability / rates: percentage with 1 decimal place.
- MORI: decimal number with 1 decimal place, not a percentage.
- Counts and minutes: whole number unless decimal precision materially helps interpretation.
- Do not sum percentage KPIs that are defined as rates; use weighted or context-appropriate aggregation.
- Executive cards should use the `Latest ...` measures; trend visuals should use the non-latest measures.
- Measures based on illustrative financial assumptions must remain visibly labeled as such in the report documentation/tooltips.
