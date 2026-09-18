import json

import numpy as np
import pytest

from mednexus.root_cause import (
    build_diagnostic_frame,
    categorical_group_tests,
    diagnostic_tree,
    numeric_associations,
    run_root_cause_analysis,
    segment_defect_rates,
)
from mednexus.synthetic import generate


@pytest.fixture(scope='module')
def frames():
    return generate(seed=42)


@pytest.fixture(scope='module')
def analysis(frames):
    return run_root_cause_analysis(frames)


def test_diagnostic_frame_has_unique_supported_grain(frames):
    frame = build_diagnostic_frame(frames)
    assert frame['production_order_id'].is_unique
    assert frame['defect_rate'].between(0, 1).all()
    assert not frame.isna().any().any()


def test_segment_intervals_and_lifts_are_valid(analysis):
    segments = analysis['segments']
    assert segments['defect_rate'].between(0, 1).all()
    assert segments['defect_rate_ci95_low'].between(0, 1).all()
    assert segments['defect_rate_ci95_high'].between(0, 1).all()
    assert (segments['defect_rate_ci95_low'] <= segments['defect_rate']).all()
    assert (segments['defect_rate'] <= segments['defect_rate_ci95_high']).all()
    assert segments['interpretation'].str.contains('not causation', case=False).all()


def test_known_synthetic_diagnostic_drivers_show_positive_association(analysis):
    associations = analysis['associations'].set_index('feature')
    for feature in ['unplanned_downtime_min', 'capacity_gap_pct']:
        assert associations.loc[feature, 'spearman_rho'] > 0
        assert associations.loc[feature, 'high_minus_low_defect_rate_pp'] > 0
        assert associations.loc[feature, 'p_value_fdr_bh'] < 0.05


def test_group_tests_report_effect_size_and_fdr(analysis):
    tests = analysis['group_tests']
    assert not tests.empty
    assert tests['epsilon_squared'].between(0, 1).all()
    assert tests['p_value'].between(0, 1).all()
    assert tests['p_value_fdr_bh'].between(0, 1).all()
    assert tests['interpretation'].str.contains('does not establish causation', case=False).all()


def test_regression_and_vif_are_finite_and_noncausal(analysis):
    regression = analysis['regression']
    vif = analysis['vif']
    diagnostics = analysis['methodology']['regression_diagnostics']

    assert np.isfinite(regression['coefficient_log_odds']).all()
    assert np.isfinite(regression['std_error_robust']).all()
    assert np.isfinite(regression['odds_ratio_per_1sd']).all()
    assert regression['interpretation'].str.contains('not a causal effect', case=False).all()
    assert np.isfinite(vif['vif']).all()
    assert diagnostics['converged'] is True
    assert diagnostics['max_vif'] >= 1


def test_diagnostic_tree_is_shallow_and_noncausal(analysis):
    importance = analysis['tree_importance']
    diagnostics = analysis['methodology']['tree_diagnostics']

    assert np.isclose(importance['tree_importance'].sum(), 1.0)
    assert diagnostics['max_depth'] == 3
    assert diagnostics['causal_status'] == 'NOT_CAUSAL'
    assert importance['interpretation'].str.contains('not causal evidence', case=False).all()


def test_investigation_priorities_do_not_claim_root_cause_causally(analysis):
    priorities = analysis['priorities']
    assert not priorities.empty
    assert priorities['causal_status'].isin(
        ['ASSOCIATION_ONLY', 'DESCRIPTIVE_ONLY', 'EXPLORATORY_ONLY']
    ).all()
    assert priorities['next_validation_step'].str.len().gt(20).all()


def test_methodology_records_complete_evidence_hierarchy(analysis):
    methodology = analysis['methodology']
    assert methodology['causal_claim'] is False
    hierarchy = methodology['evidence_hierarchy']
    assert 'segmentation with Wilson intervals' in hierarchy
    assert 'Spearman association with FDR correction and quartile contrast' in hierarchy
    assert 'grouped-binomial GLM with robust covariance and VIF' in hierarchy
    assert 'shallow diagnostic tree' in hierarchy
