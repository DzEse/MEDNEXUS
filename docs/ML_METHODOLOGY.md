# Machine-Learning Methodology

## Business question

Which machine observations have elevated near-term failure risk and therefore merit maintenance investigation?

## Grain and target

- Grain: one row per machine per day.
- Target: `failure_next_7d`.
- Features: temperature, torque, vibration and tool-wear index from the synthetic sensor fact.

The target and features are synthetic/modeling constructs and are not evidence of real medical-device manufacturing performance.

## Temporal validation design

The canonical model uses three strictly ordered date partitions:

1. **Train — first 60% of dates.**
2. **Validation — next 20% of dates.**
3. **Test — final 20% of dates.**

A calendar date cannot appear in more than one partition. Candidate models are trained only on the train period. Model selection and threshold selection use the validation period. The final test period is reserved for holdout evaluation.

This is stronger than tuning a threshold directly on the test set.

## Candidate model hierarchy

Two candidates are implemented:

- Logistic Regression with standardized numeric features and balanced class weights.
- Random Forest with balanced-subsample class weighting and controlled depth/minimum leaf size.

The primary comparison metric is validation **PR-AUC** because the failure target is imbalanced. Random Forest is selected only when its validation PR-AUC improves on Logistic Regression by at least 0.01; otherwise Logistic Regression is retained for simplicity and interpretability.

Gradient boosting remains gated. It is not added merely to increase model count.

## Threshold and operational error-cost analysis

Each candidate is evaluated across thresholds from 0.05 to 0.95.

The current decision weights are illustrative:

- false negative weight = 5;
- false positive weight = 1.

Weighted error cost:

`5 × false negatives + 1 × false positives`

The threshold-selection rule is recall-constrained: a candidate threshold must first achieve at least **70% validation recall**. Among those feasible thresholds, MEDNEXUS selects the threshold with the lowest validation weighted error cost. This prevents the strong class imbalance from making a near-never-alert threshold look artificially cheap. These values are decision weights, **not observed financial costs**.

## Holdout metrics

The selected model is evaluated once on the strict temporal holdout test period using:

- precision;
- recall;
- F1;
- ROC-AUC;
- PR-AUC;
- Brier score;
- confusion matrix;
- test positive rate.

## Calibration assessment

Calibration evidence uses probability bins on the holdout test set. Each bin reports:

- observations;
- mean predicted probability;
- observed failure rate;
- absolute calibration gap.

An expected calibration error is reported as the observation-weighted mean absolute calibration gap.

This is a calibration assessment, not a claim that the probabilities are perfectly calibrated. If holdout expected calibration error exceeds the project adequacy gate, the exported model output is labeled **uncalibrated failure-risk score** rather than estimated failure probability. Formal recalibration should only be added if the diagnostics and decision use justify it.

## Explainability

Permutation importance is calculated on the holdout test set using average precision as the scoring metric.

Permutation importance answers:

> How much does holdout predictive performance change when this feature is disrupted?

It does **not** prove that a feature causes failures.

SHAP and partial-dependence analysis remain conditional. They should be added only if they provide stable decision value beyond the validated permutation-importance layer.

## Leakage controls

- no future target values are used as features;
- no post-failure information is used as a predictor;
- dates are partitioned before evaluation;
- model selection uses validation data only;
- threshold tuning uses validation data only;
- the test period remains a strict holdout;
- the model does not infer causal effects.

## Selection and deployment interpretation

The serialized artifact is the selected candidate from the validation rule. Scores exported to Power BI are model-derived risk estimates for the test period.

The project does not claim production deployment, real-world generalization, realized maintenance savings or clinical/medical-device safety performance.

## Future model hierarchy

Potential extensions require additional evidence:

- probability recalibration if calibration quality is inadequate for the intended decision;
- gradient boosting only if it produces meaningful out-of-sample value;
- SHAP/PDP only if stable and decision-useful;
- model drift monitoring once a persistent multi-run history exists.
