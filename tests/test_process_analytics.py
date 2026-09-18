import pandas as pd
import pytest

from mednexus.process_analytics import (
    ALLOWED_ORDER_FULFILLMENT_ACTIVITIES,
    PROHIBITED_UNLINKED_ACTIVITIES,
    run_process_and_experiment_gates,
)
from mednexus.synthetic import generate


@pytest.fixture(scope='module')
def result():
    return run_process_and_experiment_gates(generate(seed=42))


def test_event_log_uses_only_source_supported_activities(result):
    event_log = result['event_log']
    assert set(event_log['activity']).issubset(ALLOWED_ORDER_FULFILLMENT_ACTIVITIES)
    for activity in PROHIBITED_UNLINKED_ACTIVITIES:
        assert activity not in set(event_log['activity'])
    assert event_log['event_semantics'].eq('OBSERVED_SYNTHETIC_SOURCE_EVENT').all()


def test_event_log_has_unique_events_and_monotonic_cases(result):
    event_log = result['event_log']
    assert event_log['event_id'].is_unique
    assert not event_log[['case_id', 'event_date', 'activity']].isna().any().any()
    for _, group in event_log.groupby('case_id'):
        ordered = group.sort_values(['event_date', 'event_sequence'])
        assert ordered['event_date'].is_monotonic_increasing


def test_every_order_has_created_shipped_delivered_events(result):
    event_log = result['event_log']
    activity_sets = event_log.groupby('case_id')['activity'].agg(set)
    required = {'Order Created', 'Shipped', 'Delivered'}
    assert activity_sets.apply(lambda values: required.issubset(values)).all()


def test_case_cycle_times_are_nonnegative_and_reconcile(result):
    cases = result['cases']
    assert cases['order_to_ship_days'].ge(0).all()
    assert cases['ship_to_delivery_days'].ge(0).all()
    assert cases['order_to_delivery_days'].ge(0).all()
    assert (
        cases['order_to_delivery_days']
        == cases['order_to_ship_days'] + cases['ship_to_delivery_days']
    ).all()
    assert (
        cases['delivery_vs_promise_days']
        == cases['delay_days']
    ).all()


def test_transition_summary_is_supported_and_ranked(result):
    transitions = result['transition_summary']
    assert set(transitions['from_activity']) == {'Order Created', 'Shipped'}
    assert set(transitions['to_activity']) == {'Shipped', 'Delivered'}
    assert transitions['transition_status'].eq(
        'SUPPORTED_BY_LINKED_SOURCE_EVENTS'
    ).all()
    assert transitions['bottleneck_rank'].min() == 1
    assert transitions['interpretation'].str.contains(
        'not a full manufacturing-process-mining result', case=False
    ).all()


def test_full_process_mining_is_fail_closed(result):
    gate = result['process_gate']
    assert gate['full_process_mining_status'] == (
        'NOT_ADMITTED_MISSING_END_TO_END_CASE_LINKAGE'
    )
    assert gate['partial_process_analytics_status'] == (
        'SUPPORTED_ORDER_FULFILLMENT_ONLY'
    )
    missing = ' '.join(gate['missing_required_linkage']).lower()
    assert 'production_order_id' in missing
    assert 'inspection' in missing or 'quality' in missing
    assert 'rework' in missing
    assert 'release' in missing


def test_experimentation_is_prospective_only(result):
    gate = result['experiment_gate']
    assert gate['experimentation_status'] == (
        'NOT_ADMITTED_NO_EXECUTED_INTERVENTION_OR_TREATMENT_ASSIGNMENT'
    )
    assert gate['causal_effect_estimated'] is False
    assert gate['experiment_executed'] is False
    assert len(gate['future_design_hierarchy']) >= 3
    fields = set(gate['minimum_future_fields'])
    assert {'intervention_id', 'treatment_flag', 'primary_outcome'}.issubset(fields)


def test_process_and_experiment_gates_are_reproducible():
    a = run_process_and_experiment_gates(generate(seed=42))
    b = run_process_and_experiment_gates(generate(seed=42))
    pd.testing.assert_frame_equal(a['event_log'], b['event_log'])
    pd.testing.assert_frame_equal(a['cases'], b['cases'])
    pd.testing.assert_frame_equal(a['transition_summary'], b['transition_summary'])
    assert a['process_gate'] == b['process_gate']
    assert a['experiment_gate'] == b['experiment_gate']
