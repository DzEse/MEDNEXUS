# Statistical Methodology

## Purpose

Separate operational signal from random variation without overstating what the synthetic evidence proves.

## Implemented methods

- descriptive distributions and robust summaries;
- trend analysis at compatible time grains;
- Pareto concentration;
- segmentation at valid grains;
- plant-level p charts for daily defective-unit proportions with varying subgroup sizes;
- explicit method gates for unsupported capability/yield metrics.

## First Pass Yield

The canonical synthetic production generator records defect_units before rework allocation. Therefore:

FPY = (Total Count - Defect Units) / Total Count

is a valid single-stage first-pass yield for the simulated process.

RTY is not calculated because sequential process-stage yields are absent. DPMO is not calculated because opportunities per unit are undefined.

## Statistical process control

The implemented control chart is a p chart at daily plant grain. This is appropriate because:

- the outcome is defective/not-defective at unit level;
- subgroup sizes vary;
- daily plant aggregates provide a documented rational subgroup for the simulated portfolio.

For each plant:

p-bar = total defects / total units

LCL/UCL = p-bar ± 3 * sqrt(p-bar(1-p-bar)/n)

Limits are clipped to 0 and 1.

A point outside the limits is a statistical signal requiring investigation. It is not automatically proof of an assignable cause.

## Capability gate

Cp, Cpk, Pp and Ppk remain NOT CALCULABLE because the canonical data contains no valid engineering specification limits for a continuous quality characteristic.

No specification limits are invented.

This also preserves the distinction between process control and process capability: calculated control limits describe process behavior; engineering specification limits describe requirements.

## Six Big Losses

The current dataset supports:

- Equipment Failure from observed downtime events;
- Setup & Adjustment from observed downtime events;
- Idling & Minor Stops from observed downtime events;
- Reduced Speed from runtime theoretical output minus actual total output;
- Process Defects as a time-equivalent first-pass defect proxy.

Startup Rejects remain NOT CALCULABLE because startup-period rejects are not separately identified.

## Value leakage / COPQ

Scrap cost, downtime cost, logistics cost, technology cost and cost per good unit are available as synthetic/illustrative value-leakage measures.

Full COPQ is intentionally not calculated because rework resource cost and external failure cost are not separately observed.

## Causality

Correlation, regression coefficients, control-chart signals, feature importance and SHAP values must not be described as causal effects. Causal language requires an appropriate identification strategy, experiment or defensible quasi-experimental design.


## Root-cause diagnostic hierarchy

MEDNEXUS now implements a non-causal diagnostic hierarchy for first-pass defect rate:

1. segment defect-rate summaries with Wilson 95% confidence intervals;
2. Spearman rank associations at production-order/machine-day grain;
3. high-vs-low quartile practical contrasts;
4. Benjamini-Hochberg false-discovery-rate correction;
5. Kruskal-Wallis group tests with epsilon-squared effect size;
6. grouped-binomial GLM with standardized predictors, HC0 robust covariance and VIF diagnostics;
7. shallow diagnostic decision tree for exploratory segmentation;
8. investigation-priority output with explicit next-validation steps.

The implemented numeric drivers are supported by the canonical source grain: unplanned downtime, machine age, workforce capacity gap, absence rate and overtime.

Statistical detection is not treated as business materiality. Correlation magnitude, quartile defect-rate difference, effect size, confidence interval and adjusted regression association are all retained so practical significance can be considered separately from p-values.

No output from this layer is labeled a proven root cause. The required interpretation is **association / investigation priority** until controlled, prospective or otherwise defensible causal evidence exists.
