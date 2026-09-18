import numpy as np
import pandas as pd
import pytest

from mednexus.analytics import monthly_enterprise_mart
from mednexus.risk import (
    BASE_THRESHOLDS,
    COMPONENTS,
    build_mori,
    run_mori_validation,
)
from mednexus.synthetic import generate


@pytest.fixture(scope='module')
def mart():
    return monthly_enterprise_mart(generate(seed=42))


@pytest.fixture(scope='module')
def weights():
    return {
        'quality': .16,
        'equipment': .16,
        'downtime': .12,
        'capacity': .12,
        'supply': .12,
        'logistics': .10,
        'workforce': .10,
        'technology': .12,
    }


@pytest.fixture(scope='module')
def result(mart, weights):
    return run_mori_validation(mart, weights)


def test_mori_bounds_and_complete_status(result):
    mori = result['mori']
    assert mori['mori_score'].between(0, 100).all()
    assert mori['missing_component_count'].eq(0).all()
    assert mori['score_status'].eq('COMPLETE').all()
    assert mori['available_weight'].eq(1.0).all()


def test_weight_vector_must_be_complete_nonnegative_and_sum_to_one(mart, weights):
    bad = dict(weights)
    bad['quality'] = -0.1
    with pytest.raises(ValueError):
        build_mori(mart, bad)

    bad = dict(weights)
    bad.pop('quality')
    with pytest.raises(ValueError):
        build_mori(mart, bad)

    bad = dict(weights)
    bad['quality'] += 0.01
    with pytest.raises(ValueError):
        build_mori(mart, bad)


def test_missing_data_policy_fails_closed_without_partial_score(mart, weights):
    damaged = mart.copy()
    damaged.loc[0, 'shortage_hours'] = np.nan
    mori = build_mori(damaged, weights)

    assert mori.loc[0, 'score_status'] == 'UNAVAILABLE_MISSING_COMPONENTS'
    assert mori.loc[0, 'missing_component_count'] >= 1
    assert pd.isna(mori.loc[0, 'mori_score'])
    assert mori.loc[0, 'mori_band'] == 'Unavailable'
    assert mori.loc[0, 'available_weight'] < 1.0


def test_component_contributions_reconcile_exactly(result):
    mori = result['mori']
    contribution_cols = [f'{component}_contribution' for component in COMPONENTS]
    reconciled = mori[contribution_cols].sum(axis=1)
    assert np.allclose(reconciled, mori['mori_score'], equal_nan=True)


def test_mori_bands_follow_canonical_cutpoints():
    from mednexus.risk import _bands

    scores = pd.Series([0.0, 24.999, 25.0, 49.999, 50.0, 74.999, 75.0, 100.0, np.nan])
    bands = _bands(scores, BASE_THRESHOLDS).tolist()
    assert bands == [
        'Stable',
        'Stable',
        'Watch',
        'Watch',
        'Elevated',
        'Elevated',
        'Critical',
        'Critical',
        'Unavailable',
    ]


def test_weight_sensitivity_preserves_weight_sum_and_baseline(result):
    sensitivity = result['weight_sensitivity']
    expected_scenarios = 1 + len(COMPONENTS) * 2
    assert sensitivity['scenario'].nunique() == expected_scenarios

    baseline = sensitivity[sensitivity['scenario'] == 'baseline']
    assert np.allclose(baseline['score_delta_vs_baseline'], 0.0)
    assert (~baseline['band_changed_vs_baseline']).all()

    for vector in sensitivity['weight_vector'].dropna().unique():
        parsed = eval(vector, {'__builtins__': {}}, {})
        assert np.isclose(sum(parsed.values()), 1.0)


def test_threshold_sensitivity_uses_documented_plus_minus_five_points(result):
    sensitivity = result['threshold_sensitivity']
    assert set(sensitivity['threshold_scenario']) == {
        'base_thresholds',
        'thresholds_minus_5_points',
        'thresholds_plus_5_points',
    }

    minus = sensitivity[sensitivity['threshold_scenario'] == 'thresholds_minus_5_points'].iloc[0]
    plus = sensitivity[sensitivity['threshold_scenario'] == 'thresholds_plus_5_points'].iloc[0]
    assert minus['stable_upper_exclusive'] == 20.0
    assert plus['stable_upper_exclusive'] == 30.0


def test_sensitivity_summary_and_methodology_disclose_project_defined_status(result):
    summary = result['sensitivity_summary']
    methodology = result['methodology']

    assert summary['missing_data_policy'] == 'fail_closed_no_partial_score'
    assert summary['normalization_method'] == 'full_available_history_min_max'
    assert methodology['index_status'] == 'project_defined_not_industry_standard'
    assert 'missing_data_policy' in methodology
    assert 'sensitivity' in methodology
    assert len(methodology['limitations']) >= 5
