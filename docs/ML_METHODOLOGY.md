# Machine-Learning Methodology

## Business question
Which machine observations have elevated near-term failure risk and therefore merit maintenance investigation?

## Grain
One row per machine per day.

## Baseline
Logistic Regression with standardized numeric features and class weighting.

## Validation
The data is sorted chronologically and split 80/20, preserving time order. Metrics include precision, recall, F1, ROC-AUC, PR-AUC and confusion matrix. The decision threshold is intentionally recall-sensitive because false negatives represent missed risk in this simulated setting.

## Leakage controls
No future target values are used as features. The model does not use post-failure information. Rows are time-ordered before train/test separation.

## Interpretation
Scores are model-derived risk estimates. Associations between features and predictions do not establish failure causation.

## Future model hierarchy
Random Forest and gradient boosting may be tested only if they produce credible out-of-sample improvement while retaining explainability and leakage controls.
