# Methodology

## Analytical discipline
For each analysis: define business question → unit of analysis → grain → data → assumptions → method → validation → what it proves → what it does not prove → decision supported.

## Financial discipline
Downtime cost uses an **illustrative financial assumption** of `$12 per downtime minute`. Technology incident cost also contains an illustrative cost proxy. These are never presented as real MEDNEXUS savings.

## Quality
OEE components follow standard definitions. The default build does not invent process specification limits, so Cp/Cpk/Pp/Ppk are not calculated.

## Statistical quality
Control charts and capability metrics should only be added after a valid measurement characteristic, rational subgrouping and legitimate specification limits are available.

## Predictive maintenance
Baseline: Logistic Regression. Temporal 80/20 split. Features use current synthetic sensor-state variables only. The project explicitly distinguishes prediction from explanation and causation.

## Forecasting
Three-month moving average is the benchmark. Any advanced model must demonstrate improved out-of-sample value over the baseline.

## Scenario analysis
Scenario relationships are transparent sensitivity assumptions. They are not causal estimates.
