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

Latest FPY =
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

`FPY` is valid in the canonical synthetic process because defect_units represent first-pass failures before rework allocation. RTY remains unavailable because sequential process-stage yields are not modeled. DPMO remains unavailable because defect opportunities per unit are undefined.

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
Average Failure Risk Score = AVERAGE(PredictiveMaintenanceScores[failure_risk_score])
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


## Statistical quality and value-loss measures

```DAX
FPY = DIVIDE(SUM(ProductionKPI[total_count]) - SUM(ProductionKPI[defect_units]), SUM(ProductionKPI[total_count]))

P Chart Defect Rate = DIVIDE(SUM(QualityPChart[defect_units]), SUM(QualityPChart[total_count]))
P Chart Center Line = AVERAGE(QualityPChart[center_line])
P Chart LCL = AVERAGE(QualityPChart[lcl])
P Chart UCL = AVERAGE(QualityPChart[ucl])
P Chart Signals = SUM(QualityPChart[out_of_control])

Cost per Good Unit = AVERAGE(ValueLeakage[cost_per_good_unit])
Known Internal Quality Cost Proxy = SUM(ValueLeakage[known_internal_quality_cost_proxy])
```

Do not create RTY, DPMO, Cp, Cpk, Pp, Ppk, startup-reject loss, rework cost, or full COPQ measures unless the required evidence is added and the corresponding methodology gate changes from NOT_CALCULABLE.


## Predictive-maintenance validation measures

The validation tables are disconnected evidence marts. They should be used on the Prediction / Forecast / Risk page and model-validation tooltip surfaces, not joined into the operational fact model.

```DAX
PM Validation PR-AUC = MAX(PredictiveMaintenanceModelComparison[pr_auc])
PM Validation ROC-AUC = MAX(PredictiveMaintenanceModelComparison[roc_auc])
PM Holdout Average Risk Score = AVERAGE(PredictiveMaintenanceScores[failure_risk_score])
PM Holdout Predicted Flags = SUM(PredictiveMaintenanceScores[predicted_failure_flag])
PM Holdout Actual Failures = SUM(PredictiveMaintenanceScores[actual_failure_next_7d])
PM Calibration Gap = AVERAGE(PredictiveMaintenanceCalibration[absolute_calibration_gap])
```

Model-comparison visuals must state that candidate selection occurred on validation data and that the exported machine scores represent the strict temporal holdout test period. Permutation-importance visuals must include the non-causal interpretation label.


Predictive-maintenance score labeling is controlled by the generated `score_semantics` field. When calibration is inadequate, visuals must say **risk score** rather than **failure probability**. Do not convert an uncalibrated score into a percentage-probability label.


## Forecast validation measures

The forecast comparison and diagnostic tables are validation evidence marts. Keep them disconnected from the operational star schema.

```DAX
Selected Forecast MAE =
CALCULATE(
    MIN(DemandForecastModelComparison[mae]),
    DemandForecastModelComparison[selection_rank] = 1
)

Selected Forecast RMSE =
CALCULATE(
    MIN(DemandForecastModelComparison[rmse]),
    DemandForecastModelComparison[selection_rank] = 1
)

Selected Forecast sMAPE % =
CALCULATE(
    MIN(DemandForecastModelComparison[smape_pct]),
    DemandForecastModelComparison[selection_rank] = 1
)

Forecast MAE Improvement vs Naive % =
CALCULATE(
    MIN(DemandForecastModelComparison[mae_improvement_vs_naive_pct]),
    DemandForecastModelComparison[selection_rank] = 1
)

Forecast Bias =
MAX(DemandForecastDiagnostics[bias_forecast_minus_actual])
```

Forecast visuals must retain the **Model-derived** disclosure and show the generated adequacy status. If the status is limited, do not imply the selected model has proven forecasting superiority.


## MORI sensitivity measures

MORI sensitivity tables are disconnected evidence marts. MORI must remain visibly labeled **Project-defined index**.

```DAX
MORI Component Contribution Points =
SUM(MORIComponentContributions[weighted_contribution_points])

MORI Weight Sensitivity Max Abs Delta =
MAX(MORIWeightSensitivity[absolute_score_delta])

MORI Weight Sensitivity Band Changes =
CALCULATE(
    COUNTROWS(MORIWeightSensitivity),
    MORIWeightSensitivity[band_changed_vs_baseline] = TRUE()
)

MORI Threshold Sensitivity Band Changes =
CALCULATE(
    COUNTROWS(MORIThresholdSensitivity),
    MORIThresholdSensitivity[band_changed_vs_baseline] = TRUE()
)
```

Do not interpret MORI as an externally calibrated probability, regulatory risk score or causal estimate. If a MORI row is unavailable because a required component is missing, Power BI must preserve that unavailable state rather than substituting zero or recalculating a partial score.


## Scenario validation measures

`ScenarioOutputs`, `ScenarioAssumptions`, and `ScenarioMonitoringPlan` are disconnected simulated evidence tables.

```DAX
Scenario Opportunity Value =
SUM(ScenarioOutputs[simulated_opportunity_value])

Scenario Good-Unit Difference =
SUM(ScenarioOutputs[difference_good_units])

Scenario Downtime Difference =
SUM(ScenarioOutputs[difference_downtime_min])

Scenario Defect Difference =
SUM(ScenarioOutputs[difference_defect_units])

Scenario Capacity-Gap Difference =
SUM(ScenarioOutputs[difference_capacity_gap_pct])
```

Every scenario visual must retain a visible **Simulated** label. `simulated_opportunity_value` must never be relabeled as realized savings. Scenario ranking is a prioritization heuristic, not mathematical optimization.
