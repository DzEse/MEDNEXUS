import pytest

from mednexus.data_dictionary import build_data_dictionary, build_table_register
from mednexus.quality import (
    build_observability,
    data_trust_score,
    evaluate,
    evaluate_referential_integrity,
    model_input_profile,
)
from mednexus.synthetic import generate


@pytest.fixture(scope='module')
def frames():
    return generate(seed=42)


def test_canonical_governance_gate_scores_100(frames):
    table_q, business_q = evaluate(frames)
    referential_q = evaluate_referential_integrity(frames)
    observability = build_observability(frames)
    score, components = data_trust_score(table_q, business_q, referential_q, observability)

    assert (table_q['status'] == 'PASS').all()
    assert (business_q['status'] == 'PASS').all()
    assert (referential_q['status'] == 'PASS').all()
    assert (observability['status'] == 'PASS').all()
    assert score == 100.0
    assert set(components) == {
        'completeness',
        'validity',
        'consistency',
        'uniqueness',
        'timeliness',
        'referential_integrity',
        'schema_consistency',
        'freshness',
    }


def test_orphan_record_is_detected_and_reduces_trust(frames):
    corrupted = {name: df.copy() for name, df in frames.items()}
    corrupted['fact_orders'].loc[corrupted['fact_orders'].index[0], 'customer_id'] = 'CUS_MISSING'

    table_q, business_q = evaluate(corrupted)
    referential_q = evaluate_referential_integrity(corrupted)
    observability = build_observability(corrupted)
    score, components = data_trust_score(table_q, business_q, referential_q, observability)

    order_customer_check = referential_q[
        (referential_q['child_table'] == 'fact_orders')
        & (referential_q['child_key'] == 'customer_id')
    ]
    assert not order_customer_check.empty
    assert (order_customer_check['status'] == 'FAIL').any()
    assert components['referential_integrity'] < 1.0
    assert score < 100.0


def test_generated_data_dictionary_covers_every_field(frames):
    dictionary = build_data_dictionary(frames)
    expected_fields = sum(len(df.columns) for df in frames.values())

    assert len(dictionary) == expected_fields
    assert not dictionary[['table', 'column', 'dtype', 'semantic_role', 'description']].isna().any().any()
    assert {'primary_key', 'foreign_key', 'date', 'measure', 'attribute', 'identifier'}.intersection(
        set(dictionary['semantic_role'])
    )


def test_table_register_has_one_row_per_source_table(frames):
    register = build_table_register(frames)
    assert set(register['table']) == set(frames)
    assert register['grain'].str.len().gt(0).all()
    assert register['business_meaning'].str.len().gt(0).all()


def test_model_input_profile_exposes_class_balance_and_sparsity(frames):
    profile = model_input_profile(frames)
    target = profile[profile['role'] == 'target'].iloc[0]

    assert profile['missing_rate'].eq(0).all()
    assert not profile['zero_variance'].any()
    assert 0 < target['positive_rate'] < 1
