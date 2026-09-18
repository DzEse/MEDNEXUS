# Assumptions and Limitations

## Assumptions

- Default enterprise data is synthetic and reproducible.
- Unit prices and cost parameters are synthetic.
- $12/min downtime cost is an illustrative financial assumption.
- Technology incident cost mapping is illustrative.
- Scenario response relationships are simplified and explicitly simulated.
- Each shipment fulfills the modeled order quantity; therefore on-time delivery is used as an OTIF proxy.
- In the canonical generator, defect_units are units failing the first pass; rework_units are the recovered subset and scrap_units are unrecovered units.

## Limitations

- Synthetic data cannot demonstrate real-world generalization.
- The predictive-maintenance target is generated from simulated relationships.
- Causal effects are not identified.
- No patient-level data is present.
- No valid engineering specification limits are available, so Cp/Cpk/Pp/Ppk are intentionally omitted.
- No sequential process-stage yield data exists, so RTY is intentionally omitted.
- Opportunities per unit are undefined, so DPMO is intentionally omitted.
- Startup-period rejects are not separately identified, so the sixth Big Loss category cannot be quantified directly.
- Rework resource cost and external failure cost are not separately observed, so full COPQ is intentionally omitted.
- p-chart signals indicate statistical behavior requiring investigation, not causal explanations.
- Power BI is specified but the PBIX file must be built by the user.


## Predictive-maintenance-specific limitations

- Candidate selection is based on synthetic validation data and cannot establish real-world model superiority.
- False-negative and false-positive weights are illustrative decision weights, not measured financial or safety costs.
- The holdout test set measures performance only under the simulated data-generating process.
- Calibration diagnostics do not establish that probabilities are suitable for safety-critical decision-making.
- Permutation importance measures predictive contribution, not causal effect.
- No clinical, patient-safety or regulated medical-device inference should be drawn from the model.


## Root-cause diagnostic limitations

- The diagnostic layer identifies associations and investigation priorities, not proven causal root causes.
- Statistical significance can be amplified by the large synthetic sample; practical effect sizes and confidence intervals must also be considered.
- The grouped-binomial regression can adjust only for measured predictors included in the model; omitted-variable bias remains possible.
- Kruskal-Wallis results identify distribution differences but do not identify which operational mechanism created the difference.
- Diagnostic-tree split importance is exploratory and in-sample; it is not causal attribution.
- Synthetic generator relationships are known by construction and do not establish real-world generalization.


## Forecasting-specific limitations

- The canonical demand history contains only 24 synthetic monthly periods, so forecasting complexity is intentionally constrained.
- Rolling-origin backtesting measures synthetic historical generalization only.
- A model can be statistically best among the tested candidates without being operationally adequate in a real enterprise.
- Residual autocorrelation diagnostics have limited power with the available backtest length.
- Seasonal-naive comparison is supported because at least 12 months of history exist, but two years of data is still weak evidence for stable annual seasonality.
- Linear-trend extrapolation is descriptive and may become unreliable if structural demand conditions change.
- Future demand values remain model-derived and must not be presented as guaranteed outcomes.


## MORI-specific limitations

- MORI is a project-defined composite index and is not an industry-standard or externally validated risk scale.
- Component weights are analytical governance choices rather than estimated causal coefficients.
- Full-history min-max normalization makes the index relative to the current canonical history and can change when new history is added.
- Correlated components can represent overlapping operational pressure and may partially double-count risk.
- Stable/Watch/Elevated/Critical thresholds are project-defined governance bands, not validated real-world risk cutoffs.
- The index fails closed when any required component is missing; MEDNEXUS does not renormalize remaining components into a partial score.
- Weight and threshold sensitivity assess robustness to design choices but do not prove predictive validity or causation.


## Scenario/optimization-specific limitations

- Scenario response relationships are illustrative assumptions, not estimated causal intervention effects.
- Simulated opportunity value is not realized savings.
- The scenario ranking is a prioritization heuristic rather than mathematical optimization.
- Formal optimization is not admitted because defensible intervention costs, resource/budget constraints, response functions and objective trade-off weights are not all available.
- Monitoring plans are prospective only; no intervention has been executed or experimentally evaluated.


## Process analytics / experimentation limitations

- Current process analytics cover linked order fulfillment only; they are not full manufacturing process mining.
- Production, inspection, rework and release events are not linked to customer order cases and are therefore not synthesized into the event log.
- Transition duration concentration is descriptive process evidence, not causal proof of a bottleneck mechanism.
- No intervention has been executed, randomized or observed prospectively, so no treatment effect is estimated.
- The experimentation framework is prospective and does not represent an actual experiment.
