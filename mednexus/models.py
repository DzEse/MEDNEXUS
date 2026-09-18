from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from joblib import dump
from sklearn.ensemble import RandomForestClassifier
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


FEATURES = ['temperature_c', 'torque_nm', 'vibration_mm_s', 'tool_wear_index']
TARGET = 'failure_next_7d'
FALSE_NEGATIVE_COST = 5.0
FALSE_POSITIVE_COST = 1.0
MIN_VALIDATION_RECALL = 0.70
MAX_ECE_FOR_PROBABILITY_LABEL = 0.10
THRESHOLDS = np.round(np.arange(0.05, 0.96, 0.05), 2)


def _safe_auc(metric_fn, y_true, prob):
    return float(metric_fn(y_true, prob)) if pd.Series(y_true).nunique() > 1 else None


def _temporal_split(sensor: pd.DataFrame):
    df = sensor.copy()
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values(['date', 'machine_id']).reset_index(drop=True)

    unique_dates = pd.Index(sorted(df['date'].dt.normalize().unique()))
    if len(unique_dates) < 10:
        raise ValueError('Predictive-maintenance validation requires at least 10 unique dates.')

    train_end = max(1, int(len(unique_dates) * 0.60))
    validation_end = max(train_end + 1, int(len(unique_dates) * 0.80))
    validation_end = min(validation_end, len(unique_dates) - 1)

    train_dates = set(unique_dates[:train_end])
    validation_dates = set(unique_dates[train_end:validation_end])
    test_dates = set(unique_dates[validation_end:])

    normalized = df['date'].dt.normalize()
    train = df[normalized.isin(train_dates)].copy()
    validation = df[normalized.isin(validation_dates)].copy()
    test = df[normalized.isin(test_dates)].copy()

    if train.empty or validation.empty or test.empty:
        raise ValueError('Temporal split produced an empty partition.')

    return train, validation, test


def _candidate_models():
    return {
        'LogisticRegression': Pipeline(
            [
                ('scale', StandardScaler()),
                (
                    'model',
                    LogisticRegression(
                        max_iter=1000,
                        class_weight='balanced',
                        random_state=42,
                    ),
                ),
            ]
        ),
        'RandomForest': RandomForestClassifier(
            n_estimators=250,
            max_depth=8,
            min_samples_leaf=5,
            class_weight='balanced_subsample',
            random_state=42,
            n_jobs=-1,
        ),
    }


def _threshold_table(model_name, y_true, prob):
    rows = []
    for threshold in THRESHOLDS:
        pred = (prob >= threshold).astype(int)
        tn, fp, fn, tp = confusion_matrix(y_true, pred, labels=[0, 1]).ravel()
        total_cost = fn * FALSE_NEGATIVE_COST + fp * FALSE_POSITIVE_COST
        rows.append(
            {
                'model': model_name,
                'threshold': float(threshold),
                'tn': int(tn),
                'fp': int(fp),
                'fn': int(fn),
                'tp': int(tp),
                'precision': float(precision_score(y_true, pred, zero_division=0)),
                'recall': float(recall_score(y_true, pred, zero_division=0)),
                'f1': float(f1_score(y_true, pred, zero_division=0)),
                'false_negative_cost_weight': FALSE_NEGATIVE_COST,
                'false_positive_cost_weight': FALSE_POSITIVE_COST,
                'weighted_error_cost': float(total_cost),
                'weighted_error_cost_per_1000': float(total_cost / max(len(y_true), 1) * 1000),
                'meets_recall_floor': bool(recall_score(y_true, pred, zero_division=0) >= MIN_VALIDATION_RECALL),
            }
        )
    return pd.DataFrame(rows)


def _choose_threshold(table: pd.DataFrame):
    feasible = table[table['recall'] >= MIN_VALIDATION_RECALL].copy()
    if feasible.empty:
        raise RuntimeError(
            f'No validation threshold satisfies the minimum recall floor of {MIN_VALIDATION_RECALL:.2f}.'
        )
    ranked = feasible.sort_values(
        ['weighted_error_cost', 'recall', 'precision', 'threshold'],
        ascending=[True, False, False, True],
    )
    return float(ranked.iloc[0]['threshold'])


def _classification_metrics(model_name, split_name, y_true, prob, threshold):
    pred = (prob >= threshold).astype(int)
    cm = confusion_matrix(y_true, pred, labels=[0, 1])
    return {
        'model': model_name,
        'split': split_name,
        'threshold': float(threshold),
        'precision': float(precision_score(y_true, pred, zero_division=0)),
        'recall': float(recall_score(y_true, pred, zero_division=0)),
        'f1': float(f1_score(y_true, pred, zero_division=0)),
        'roc_auc': _safe_auc(roc_auc_score, y_true, prob),
        'pr_auc': _safe_auc(average_precision_score, y_true, prob),
        'brier_score': float(brier_score_loss(y_true, prob)),
        'confusion_matrix': cm.tolist(),
        'rows': int(len(y_true)),
        'positive_rate': float(pd.Series(y_true).mean()),
    }


def _calibration_table(model_name, y_true, prob, bins=10):
    frame = pd.DataFrame({'actual': np.asarray(y_true, dtype=int), 'probability': prob})
    frame['bin'] = pd.cut(
        frame['probability'],
        bins=np.linspace(0, 1, bins + 1),
        include_lowest=True,
        duplicates='drop',
    )
    rows = []
    for interval, group in frame.groupby('bin', observed=True):
        rows.append(
            {
                'model': model_name,
                'probability_bin': str(interval),
                'observations': int(len(group)),
                'mean_predicted_probability': float(group['probability'].mean()),
                'observed_failure_rate': float(group['actual'].mean()),
                'absolute_calibration_gap': float(
                    abs(group['probability'].mean() - group['actual'].mean())
                ),
            }
        )
    return pd.DataFrame(rows)


def _expected_calibration_error(calibration: pd.DataFrame):
    if calibration.empty:
        return None
    weights = calibration['observations'] / calibration['observations'].sum()
    return float((weights * calibration['absolute_calibration_gap']).sum())


def train_predictive_maintenance(sensor: pd.DataFrame, model_path=None):
    train, validation, test = _temporal_split(sensor)

    X_train = train[FEATURES]
    y_train = train[TARGET].astype(int)
    X_validation = validation[FEATURES]
    y_validation = validation[TARGET].astype(int)
    X_test = test[FEATURES]
    y_test = test[TARGET].astype(int)

    fitted = {}
    comparison_rows = []
    threshold_frames = []
    validation_probabilities = {}

    for model_name, model in _candidate_models().items():
        model.fit(X_train, y_train)
        fitted[model_name] = model

        validation_prob = model.predict_proba(X_validation)[:, 1]
        validation_probabilities[model_name] = validation_prob
        threshold_table = _threshold_table(model_name, y_validation, validation_prob)
        threshold_frames.append(threshold_table)
        chosen_threshold = _choose_threshold(threshold_table)

        validation_metrics = _classification_metrics(
            model_name,
            'validation',
            y_validation,
            validation_prob,
            chosen_threshold,
        )
        comparison_rows.append(validation_metrics)

    comparison = pd.DataFrame(comparison_rows)
    comparison['selection_metric'] = 'validation PR-AUC'
    comparison['selection_rule'] = (
        'Highest validation PR-AUC; if models differ by <0.01, prefer LogisticRegression for simplicity.'
    )

    log_pr = float(comparison.loc[comparison['model'] == 'LogisticRegression', 'pr_auc'].iloc[0])
    rf_pr = float(comparison.loc[comparison['model'] == 'RandomForest', 'pr_auc'].iloc[0])
    selected_model_name = 'RandomForest' if rf_pr >= log_pr + 0.01 else 'LogisticRegression'

    threshold_analysis = pd.concat(threshold_frames, ignore_index=True)
    selected_validation_thresholds = threshold_analysis[
        threshold_analysis['model'] == selected_model_name
    ]
    selected_threshold = _choose_threshold(selected_validation_thresholds)

    selected_model = fitted[selected_model_name]
    test_prob = selected_model.predict_proba(X_test)[:, 1]
    test_metrics = _classification_metrics(
        selected_model_name,
        'strict temporal holdout test',
        y_test,
        test_prob,
        selected_threshold,
    )

    calibration = _calibration_table(selected_model_name, y_test, test_prob)
    ece = _expected_calibration_error(calibration)
    calibration_status = (
        'ACCEPTABLE_FOR_PROJECT_PROBABILITY_INTERPRETATION'
        if ece is not None and ece <= MAX_ECE_FOR_PROBABILITY_LABEL
        else 'INADEQUATE_FOR_PROBABILITY_INTERPRETATION'
    )
    score_semantics = (
        'estimated_failure_probability'
        if calibration_status == 'ACCEPTABLE_FOR_PROJECT_PROBABILITY_INTERPRETATION'
        else 'uncalibrated_failure_risk_score'
    )

    importance_result = permutation_importance(
        selected_model,
        X_test,
        y_test,
        scoring='average_precision',
        n_repeats=8,
        random_state=42,
        n_jobs=-1,
    )
    feature_importance = pd.DataFrame(
        {
            'model': selected_model_name,
            'feature': FEATURES,
            'permutation_importance_mean': importance_result.importances_mean,
            'permutation_importance_std': importance_result.importances_std,
        }
    ).sort_values('permutation_importance_mean', ascending=False)
    feature_importance['interpretation'] = (
        'Predictive contribution on the holdout set; not evidence of causation.'
    )

    pred = (test_prob >= selected_threshold).astype(int)
    scored = test[['date', 'machine_id', 'plant_id', 'line_id']].copy()
    scored['failure_risk'] = test_prob
    scored['failure_risk_score'] = test_prob
    scored['predicted_failure_flag'] = pred
    scored['actual_failure_next_7d'] = y_test.to_numpy()
    scored['selected_model'] = selected_model_name
    scored['decision_threshold'] = selected_threshold
    scored['score_semantics'] = score_semantics

    metrics = {
        **test_metrics,
        'model': selected_model_name,
        'model_role': 'selected predictive-maintenance model',
        'selection_basis': comparison.loc[
            comparison['model'] == selected_model_name, 'selection_rule'
        ].iloc[0],
        'logistic_validation_pr_auc': log_pr,
        'random_forest_validation_pr_auc': rf_pr,
        'expected_calibration_error': ece,
        'calibration_status': calibration_status,
        'score_semantics': score_semantics,
        'minimum_validation_recall': MIN_VALIDATION_RECALL,
        'threshold_policy': (
            'Minimize validation weighted error cost only among thresholds meeting the minimum validation recall floor.'
        ),
        'false_negative_cost_weight': FALSE_NEGATIVE_COST,
        'false_positive_cost_weight': FALSE_POSITIVE_COST,
        'train_start': str(train['date'].min().date()),
        'train_end': str(train['date'].max().date()),
        'validation_start': str(validation['date'].min().date()),
        'validation_end': str(validation['date'].max().date()),
        'test_start': str(test['date'].min().date()),
        'test_end': str(test['date'].max().date()),
        'features': FEATURES,
        'note': (
            'Model-derived predictive evidence on synthetic data. Cost weights are illustrative decision weights, '
            'not observed financial costs. Raw scores are labeled as uncalibrated unless holdout calibration is adequate. '
            'Feature importance and model associations are not causal conclusions.'
        ),
    }

    if model_path:
        Path(model_path).parent.mkdir(parents=True, exist_ok=True)
        dump(selected_model, model_path)

    return (
        metrics,
        scored,
        comparison,
        threshold_analysis,
        calibration,
        feature_importance,
    )
