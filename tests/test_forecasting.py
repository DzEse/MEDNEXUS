import numpy as np
import pandas as pd
import pytest

from mednexus.forecasting import (
    CANDIDATE_METHODS,
    MIN_BACKTEST_POINTS,
    forecast_demand,
)
from mednexus.synthetic import generate


@pytest.fixture(scope='module')
def result():
    frames = generate(seed=42)
    return forecast_demand(frames['fact_orders'])


def test_rolling_origin_backtest_is_temporally_strict(result):
    _, backtest, _, _, _ = result
    assert not backtest.empty
    assert (pd.to_datetime(backtest['train_end_month']) < pd.to_datetime(backtest['month'])).all()
    assert backtest['validation_design'].eq('rolling_origin_one_step_ahead').all()


def test_all_candidates_share_same_backtest_months(result):
    _, backtest, _, comparison, _ = result
    counts = backtest.groupby('model')['month'].nunique()
    assert set(counts.index) == set(CANDIDATE_METHODS)
    assert counts.nunique() == 1
    assert comparison['backtest_periods'].nunique() == 1
    assert comparison['backtest_periods'].iloc[0] >= MIN_BACKTEST_POINTS


def test_forecast_metrics_are_finite_and_smape_is_bounded(result):
    metrics, _, _, comparison, _ = result
    for column in ['mae', 'rmse', 'smape_pct', 'bias']:
        assert np.isfinite(metrics[column])
    assert comparison['mae'].ge(0).all()
    assert comparison['rmse'].ge(0).all()
    assert comparison['smape_pct'].between(0, 200).all()


def test_selected_model_is_rank_one_and_benchmark_gate_is_explicit(result):
    metrics, _, _, comparison, diagnostics = result
    selected = comparison.loc[comparison['model'] == metrics['selected_model']].iloc[0]
    assert int(selected['selection_rank']) == 1
    assert diagnostics['selected_model'].iloc[0] == metrics['selected_model']
    assert metrics['adequacy_status'] in {
        'PASS_OUTPERFORMS_NAIVE_ON_MAE_AND_RMSE',
        'LIMITED_NO_CANDIDATE_BEATS_NAIVE',
        'LIMITED_INSUFFICIENT_BACKTEST_PERIODS',
        'LIMITED_MIXED_BENCHMARK_PERFORMANCE',
    }
    assert isinstance(metrics['selected_mae_not_worse_than_naive'], bool)
    assert isinstance(metrics['selected_rmse_not_worse_than_naive'], bool)


def test_naive_and_canonical_moving_average_baselines_are_preserved(result):
    metrics, _, _, comparison, _ = result
    models = set(comparison['model'])
    assert 'naive_last' in models
    assert 'moving_average_3' in models
    assert metrics['naive_benchmark_model'] == 'naive_last'
    assert metrics['canonical_baseline_model'] == 'moving_average_3'


def test_future_forecast_is_nonnegative_and_labeled_model_derived(result):
    metrics, _, future, _, _ = result
    assert len(future) == 3
    assert future['forecast_horizon_month'].tolist() == [1, 2, 3]
    assert future['forecast_demand'].ge(0).all()
    assert future['selected_model'].eq(metrics['selected_model']).all()
    assert future['forecast_semantics'].eq('model_derived_synthetic_demand_forecast').all()


def test_residual_diagnostics_are_retained_without_overclaim(result):
    metrics, _, _, comparison, _ = result
    assert 'residual_lag1_autocorrelation' in metrics
    assert 'ljung_box_p_value' in metrics
    assert comparison['interpretation'].str.contains(
        'not guaranteed to generalize', case=False
    ).all()


def test_forecasting_is_reproducible():
    frames = generate(seed=42)
    a = forecast_demand(frames['fact_orders'])
    b = forecast_demand(frames['fact_orders'])
    assert a[0]['selected_model'] == b[0]['selected_model']
    assert np.isclose(a[0]['mae'], b[0]['mae'])
    pd.testing.assert_frame_equal(a[2], b[2])
