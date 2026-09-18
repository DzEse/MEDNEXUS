import numpy as np
import pandas as pd
import pytest

from mednexus.analytics import monthly_enterprise_mart
from mednexus.scenarios import run_scenarios
from mednexus.synthetic import generate


@pytest.fixture(scope='module')
def result():
    frames = generate(seed=42)
    mart = monthly_enterprise_mart(frames)
    return run_scenarios(mart)


def test_scenario_flow_and_labels_are_explicit(result):
    scenarios = result['scenarios']
    methodology = result['methodology']

    assert len(scenarios) == 5
    assert scenarios['scenario_status'].eq('SIMULATED').all()
    assert scenarios['value_semantics'].eq(
        'SIMULATED_OPPORTUNITY_NOT_REALIZED_SAVINGS'
    ).all()
    assert scenarios['response_function_status'].eq(
        'ILLUSTRATIVE_ASSUMPTION_NOT_CAUSAL'
    ).all()
    assert methodology['canonical_flow'] == [
        'Baseline',
        'Assumption',
        'Expected Change',
        'Result',
        'Difference',
        'Monitoring',
    ]
    assert methodology['causal_claim'] is False


def test_baseline_reconciles_to_zero_difference(result):
    baseline = result['scenarios'].set_index('scenario').loc['Baseline']

    assert np.isclose(baseline['difference_downtime_min'], 0.0)
    assert np.isclose(baseline['difference_defect_units'], 0.0)
    assert np.isclose(baseline['difference_capacity_gap_pct'], 0.0)
    assert np.isclose(baseline['difference_good_units'], 0.0)
    assert np.isclose(baseline['simulated_opportunity_value'], 0.0)
    assert int(baseline['decision_priority_rank']) == 0


def test_combined_scenario_applies_all_declared_levers(result):
    combined = result['scenarios'].set_index('scenario').loc['Combined intervention']

    assert np.isclose(combined['downtime_reduction_pct'], 15.0)
    assert np.isclose(combined['defect_reduction_pct'], 12.0)
    assert np.isclose(combined['workforce_capacity_change_pct'], 5.0)
    assert combined['simulated_downtime_min'] < combined['baseline_downtime_min']
    assert combined['simulated_defect_units'] < combined['baseline_defect_units']
    assert combined['simulated_capacity_gap_pct'] <= combined['baseline_capacity_gap_pct']
    assert combined['simulated_good_units'] > combined['baseline_good_units']


def test_simulated_opportunity_value_reconciles_only_to_supported_cost_proxies(result):
    scenarios = result['scenarios']
    expected = (
        scenarios['simulated_downtime_value_proxy']
        + scenarios['simulated_scrap_value_proxy']
    )
    assert np.allclose(scenarios['simulated_opportunity_value'], expected)
    assert scenarios['simulated_opportunity_value'].ge(0).all()


def test_scenario_priority_is_a_heuristic_not_optimization(result):
    scenarios = result['scenarios']
    candidates = scenarios[scenarios['scenario'] != 'Baseline'].copy()

    rank_one = candidates.loc[candidates['decision_priority_rank'] == 1]
    assert len(rank_one) == 1
    assert np.isclose(
        rank_one.iloc[0]['simulated_opportunity_value'],
        candidates['simulated_opportunity_value'].max(),
    )
    assert scenarios['ranking_semantics'].str.contains(
        'not mathematical optimization', case=False
    ).all()


def test_monitoring_plan_requires_future_observed_validation(result):
    monitoring = result['monitoring_plan']

    assert len(monitoring) == 16
    assert monitoring['status'].eq('MONITORING_PLAN_ONLY_NOT_EXECUTED').all()
    assert monitoring['validation_design'].eq(
        'PRE_POST_OR_CONTROLLED_COMPARISON_IF_IMPLEMENTED'
    ).all()
    assert monitoring['minimum_evidence_before_causal_claim'].str.contains(
        'Observed post-intervention data', case=False
    ).all()


def test_optimization_is_fail_closed(result):
    gate = result['optimization_gate']

    assert gate['optimization_status'] == (
        'NOT_ADMITTED_INSUFFICIENT_DECISION_MODEL_EVIDENCE'
    )
    assert gate['solver_executed'] is False
    assert gate['recommendation_type'] == 'SCENARIO_PRIORITIZATION_ONLY'
    assert len(gate['missing_required_evidence']) >= 5
    required_text = ' '.join(gate['missing_required_evidence']).lower()
    for concept in ['cost', 'constraint', 'response']:
        assert concept in required_text


def test_scenario_engine_is_reproducible():
    frames = generate(seed=42)
    mart = monthly_enterprise_mart(frames)
    a = run_scenarios(mart)
    b = run_scenarios(mart)

    pd.testing.assert_frame_equal(a['scenarios'], b['scenarios'])
    pd.testing.assert_frame_equal(a['assumptions'], b['assumptions'])
    pd.testing.assert_frame_equal(a['monitoring_plan'], b['monitoring_plan'])
    assert a['optimization_gate'] == b['optimization_gate']
