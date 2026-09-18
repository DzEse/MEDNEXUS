import numpy as np
import pytest

from mednexus.models import FEATURES, train_predictive_maintenance
from mednexus.synthetic import generate


@pytest.fixture(scope='module')
def result():
    sensor = generate(seed=42)['fact_sensor']
    return train_predictive_maintenance(sensor)


def test_candidate_comparison_contains_logistic_and_random_forest(result):
    metrics, scored, comparison, thresholds, calibration, importance = result
    assert set(comparison['model']) == {'LogisticRegression', 'RandomForest'}
    assert comparison['split'].eq('validation').all()
    assert comparison['pr_auc'].between(0, 1).all()
    assert comparison['roc_auc'].between(0, 1).all()


def test_temporal_partitions_are_strictly_ordered(result):
    metrics = result[0]
    assert metrics['train_end'] < metrics['validation_start']
    assert metrics['validation_end'] < metrics['test_start']


def test_threshold_is_selected_from_validation_cost_table(result):
    metrics, scored, comparison, thresholds, calibration, importance = result
    selected = thresholds[thresholds['model'] == metrics['model']].copy()
    best_cost = selected['weighted_error_cost'].min()
    chosen = selected[np.isclose(selected['threshold'], metrics['threshold'])].iloc[0]

    assert np.isclose(chosen['weighted_error_cost'], best_cost)
    assert metrics['false_negative_cost_weight'] > metrics['false_positive_cost_weight']


def test_holdout_scores_and_metrics_are_valid(result):
    metrics, scored, comparison, thresholds, calibration, importance = result
    assert scored['failure_risk'].between(0, 1).all()
    assert scored['predicted_failure_flag'].isin([0, 1]).all()
    assert scored['actual_failure_next_7d'].isin([0, 1]).all()
    assert scored['selected_model'].nunique() == 1
    assert scored['selected_model'].iloc[0] == metrics['model']

    for key in ['precision', 'recall', 'f1', 'roc_auc', 'pr_auc', 'brier_score']:
        assert metrics[key] is not None
        assert 0 <= metrics[key] <= 1


def test_calibration_evidence_is_explicit(result):
    metrics, scored, comparison, thresholds, calibration, importance = result
    assert not calibration.empty
    assert calibration['mean_predicted_probability'].between(0, 1).all()
    assert calibration['observed_failure_rate'].between(0, 1).all()
    assert calibration['absolute_calibration_gap'].ge(0).all()
    assert 0 <= metrics['expected_calibration_error'] <= 1


def test_permutation_importance_covers_all_features_and_warns_against_causality(result):
    metrics, scored, comparison, thresholds, calibration, importance = result
    assert set(importance['feature']) == set(FEATURES)
    assert importance['permutation_importance_mean'].notna().all()
    assert importance['permutation_importance_std'].notna().all()
    assert importance['interpretation'].str.contains('not evidence of causation', case=False).all()
    assert 'not causal' in metrics['note'].lower() or 'not causal conclusions' in metrics['note'].lower()
