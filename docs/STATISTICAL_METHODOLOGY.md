# Statistical Methodology

## Purpose
Separate operational signal from random variation without overstating what the synthetic evidence proves.

## Default methods
- descriptive distributions and robust summaries
- trend analysis at compatible time grains
- Pareto concentration
- segmentation by plant, line, machine, product, supplier and customer when sample size permits
- confidence intervals/effect sizes for future intervention studies
- correlation/regression only as association evidence

## Process control and capability
The default build does **not** calculate Cp, Cpk, Pp or Ppk because valid specification limits are not present. It also does not fabricate control limits. Future control-chart work must choose X-bar/R, I-MR, p or np charts according to measurement type and rational subgrouping.

## Causality
Correlation, regression coefficients, feature importance and SHAP values must not be described as causal effects. Causal language requires an appropriate identification strategy, experiment or defensible quasi-experimental design.
