from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error
from statsmodels.stats.diagnostic import acorr_ljungbox


CANDIDATE_METHODS = (
    'naive_last',
    'moving_average_3',
    'seasonal_naive_12',
    'linear_trend',
)

METHOD_LABELS = {
    'naive_last': 'Naive last-value',
    'moving_average_3': '3-month moving average',
    'seasonal_naive_12': 'Seasonal naive (12-month)',
    'linear_trend': 'Expanding linear trend',
}

MIN_COMMON_TRAIN_MONTHS = 12
MIN_BACKTEST_POINTS = 8


def _monthly_demand(orders: pd.DataFrame) -> pd.DataFrame:
    required = {'order_date', 'quantity'}
    missing = required.difference(orders.columns)
    if missing:
        raise ValueError(f'Orders missing required forecasting columns: {sorted(missing)}')

    d = orders.copy()
    d['month'] = pd.to_datetime(d['order_date']).dt.to_period('M').dt.to_timestamp()
    ts = (
        d.groupby('month', as_index=False)['quantity']
        .sum()
        .rename(columns={'quantity': 'demand'})
        .sort_values('month')
        .reset_index(drop=True)
    )

    if ts.empty:
        raise ValueError('Cannot forecast demand from an empty order history.')

    expected = pd.date_range(ts['month'].min(), ts['month'].max(), freq='MS')
    observed = pd.DatetimeIndex(ts['month'])
    if not observed.equals(expected):
        missing_months = expected.difference(observed).strftime('%Y-%m').tolist()
        raise ValueError(
            'Monthly demand history is not contiguous; refusing to treat missing months as zero demand. '
            f'Missing months: {missing_months}'
        )

    if (ts['demand'] < 0).any():
        raise ValueError('Demand contains negative values.')

    return ts


def _predict_one(method: str, history: np.ndarray) -> float:
    y = np.asarray(history, dtype=float)
    if len(y) == 0:
        raise ValueError('Forecast history cannot be empty.')

    if method == 'naive_last':
        pred = y[-1]
    elif method == 'moving_average_3':
        if len(y) < 3:
            raise ValueError('3-month moving average requires at least 3 months.')
        pred = y[-3:].mean()
    elif method == 'seasonal_naive_12':
        if len(y) < 12:
            raise ValueError('Seasonal naive requires at least 12 months.')
        pred = y[-12]
    elif method == 'linear_trend':
        if len(y) < 6:
            raise ValueError('Linear trend requires at least 6 months.')
        x = np.arange(len(y), dtype=float)
        slope, intercept = np.polyfit(x, y, 1)
        pred = intercept + slope * len(y)
    else:
        raise ValueError(f'Unknown forecast method: {method}')

    return float(max(pred, 0.0))


def _smape(actual: np.ndarray, forecast: np.ndarray) -> np.ndarray:
    actual = np.asarray(actual, dtype=float)
    forecast = np.asarray(forecast, dtype=float)
    denominator = np.abs(actual) + np.abs(forecast)
    return np.where(
        denominator == 0,
        0.0,
        200.0 * np.abs(forecast - actual) / denominator,
    )


def rolling_origin_backtest(ts: pd.DataFrame) -> pd.DataFrame:
    if len(ts) <= MIN_COMMON_TRAIN_MONTHS:
        raise ValueError(
            f'Forecast comparison requires more than {MIN_COMMON_TRAIN_MONTHS} contiguous monthly observations.'
        )

    rows = []
    demand = ts['demand'].astype(float).to_numpy()

    for origin in range(MIN_COMMON_TRAIN_MONTHS, len(ts)):
        history = demand[:origin]
        actual = float(demand[origin])
        month = pd.Timestamp(ts.loc[origin, 'month'])

        for method in CANDIDATE_METHODS:
            forecast = _predict_one(method, history)
            error = forecast - actual
            rows.append(
                {
                    'month': month,
                    'model': method,
                    'model_label': METHOD_LABELS[method],
                    'train_start_month': pd.Timestamp(ts.loc[0, 'month']),
                    'train_end_month': pd.Timestamp(ts.loc[origin - 1, 'month']),
                    'train_months': int(origin),
                    'actual_demand': actual,
                    'forecast_demand': forecast,
                    'error_forecast_minus_actual': error,
                    'absolute_error': abs(error),
                    'squared_error': error ** 2,
                    'smape_pct': float(_smape(np.array([actual]), np.array([forecast]))[0]),
                    'validation_design': 'rolling_origin_one_step_ahead',
                }
            )

    out = pd.DataFrame(rows)
    if out.empty:
        raise RuntimeError('Rolling-origin backtest produced no validation rows.')
    return out


def _residual_diagnostics(errors: pd.Series) -> dict:
    e = pd.Series(errors, dtype=float).reset_index(drop=True)
    lag1 = float(e.autocorr(lag=1)) if len(e) >= 3 else np.nan

    if len(e) >= 6:
        lag = min(4, max(1, len(e) // 3))
        lb = acorr_ljungbox(e, lags=[lag], return_df=True)
        lb_stat = float(lb['lb_stat'].iloc[0])
        lb_pvalue = float(lb['lb_pvalue'].iloc[0])
    else:
        lag = None
        lb_stat = np.nan
        lb_pvalue = np.nan

    return {
        'residual_lag1_autocorrelation': lag1,
        'ljung_box_lag': lag,
        'ljung_box_statistic': lb_stat,
        'ljung_box_p_value': lb_pvalue,
    }


def compare_forecasts(backtest: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for model, group in backtest.groupby('model', sort=False):
        actual = group['actual_demand'].to_numpy(dtype=float)
        forecast = group['forecast_demand'].to_numpy(dtype=float)
        errors = forecast - actual
        residual = _residual_diagnostics(pd.Series(actual - forecast))

        rows.append(
            {
                'model': model,
                'model_label': METHOD_LABELS[model],
                'backtest_periods': int(len(group)),
                'backtest_start': pd.Timestamp(group['month'].min()),
                'backtest_end': pd.Timestamp(group['month'].max()),
                'mae': float(mean_absolute_error(actual, forecast)),
                'rmse': float(mean_squared_error(actual, forecast) ** 0.5),
                'smape_pct': float(_smape(actual, forecast).mean()),
                'bias_forecast_minus_actual': float(errors.mean()),
                'mean_actual_demand': float(actual.mean()),
                **residual,
            }
        )

    comparison = pd.DataFrame(rows)
    naive = comparison.loc[comparison['model'] == 'naive_last'].iloc[0]
    baseline = comparison.loc[comparison['model'] == 'moving_average_3'].iloc[0]

    comparison['mae_improvement_vs_naive_pct'] = np.where(
        naive['mae'] == 0,
        0.0,
        (naive['mae'] - comparison['mae']) / naive['mae'] * 100.0,
    )
    comparison['rmse_improvement_vs_naive_pct'] = np.where(
        naive['rmse'] == 0,
        0.0,
        (naive['rmse'] - comparison['rmse']) / naive['rmse'] * 100.0,
    )
    comparison['mae_improvement_vs_ma3_pct'] = np.where(
        baseline['mae'] == 0,
        0.0,
        (baseline['mae'] - comparison['mae']) / baseline['mae'] * 100.0,
    )
    ordered_index = comparison.sort_values(['mae', 'rmse', 'smape_pct']).index.tolist()
    rank_map = {original_index: rank for rank, original_index in enumerate(ordered_index, start=1)}
    comparison['selection_rank'] = comparison.index.map(rank_map).astype(int)
    comparison['interpretation'] = (
        'Rolling-origin one-step-ahead model comparison on synthetic monthly demand; '
        'forecast performance is model-derived and not guaranteed to generalize.'
    )

    return comparison.sort_values('selection_rank').reset_index(drop=True)


def _select_model(comparison: pd.DataFrame) -> tuple[str, dict]:
    ranked = comparison.sort_values(['mae', 'rmse', 'smape_pct']).reset_index(drop=True)
    best = ranked.iloc[0]
    naive = comparison.loc[comparison['model'] == 'naive_last'].iloc[0]
    baseline = comparison.loc[comparison['model'] == 'moving_average_3'].iloc[0]

    sample_gate = int(best['backtest_periods']) >= MIN_BACKTEST_POINTS
    mae_gate = float(best['mae']) <= float(naive['mae']) + 1e-12
    rmse_gate = float(best['rmse']) <= float(naive['rmse']) + 1e-12

    if sample_gate and mae_gate and rmse_gate and best['model'] != 'naive_last':
        adequacy_status = 'PASS_OUTPERFORMS_NAIVE_ON_MAE_AND_RMSE'
    elif sample_gate and best['model'] == 'naive_last':
        adequacy_status = 'LIMITED_NO_CANDIDATE_BEATS_NAIVE'
    elif not sample_gate:
        adequacy_status = 'LIMITED_INSUFFICIENT_BACKTEST_PERIODS'
    else:
        adequacy_status = 'LIMITED_MIXED_BENCHMARK_PERFORMANCE'

    gate = {
        'sample_adequacy_pass': bool(sample_gate),
        'minimum_backtest_periods': MIN_BACKTEST_POINTS,
        'selected_mae_not_worse_than_naive': bool(mae_gate),
        'selected_rmse_not_worse_than_naive': bool(rmse_gate),
        'selected_model': str(best['model']),
        'selected_model_label': str(best['model_label']),
        'adequacy_status': adequacy_status,
        'selection_basis': 'Lowest rolling-origin MAE; RMSE then sMAPE used as tie-breakers.',
        'naive_benchmark_model': 'naive_last',
        'canonical_baseline_model': 'moving_average_3',
        'selected_mae_improvement_vs_naive_pct': float(best['mae_improvement_vs_naive_pct']),
        'selected_rmse_improvement_vs_naive_pct': float(best['rmse_improvement_vs_naive_pct']),
        'selected_mae_improvement_vs_ma3_pct': float(best['mae_improvement_vs_ma3_pct']),
        'note': (
            'Adequacy is a backtest evidence gate, not a guarantee of future accuracy. '
            'If no candidate beats naive demand forecasting, the result remains explicitly limited.'
        ),
    }
    return str(best['model']), gate


def _future_forecast(ts: pd.DataFrame, selected_model: str, horizon: int, adequacy_status: str) -> pd.DataFrame:
    history = ts['demand'].astype(float).tolist()
    last_month = pd.Timestamp(ts['month'].max())
    rows = []

    for step in range(1, horizon + 1):
        forecast = _predict_one(selected_model, np.asarray(history, dtype=float))
        month = last_month + pd.offsets.MonthBegin(step)
        rows.append(
            {
                'month': month,
                'forecast_demand': forecast,
                'selected_model': selected_model,
                'selected_model_label': METHOD_LABELS[selected_model],
                'forecast_horizon_month': step,
                'forecast_semantics': 'model_derived_synthetic_demand_forecast',
                'adequacy_status': adequacy_status,
            }
        )
        history.append(forecast)

    return pd.DataFrame(rows)


def forecast_demand(orders: pd.DataFrame, horizon: int = 3):
    ts = _monthly_demand(orders)
    backtest = rolling_origin_backtest(ts)
    comparison = compare_forecasts(backtest)
    selected_model, gate = _select_model(comparison)

    selected = comparison.loc[comparison['model'] == selected_model].iloc[0]
    future = _future_forecast(ts, selected_model, horizon, gate['adequacy_status'])

    diagnostics = pd.DataFrame(
        [
            {
                'selected_model': selected_model,
                'selected_model_label': METHOD_LABELS[selected_model],
                'backtest_periods': int(selected['backtest_periods']),
                'backtest_start': selected['backtest_start'],
                'backtest_end': selected['backtest_end'],
                'mae': float(selected['mae']),
                'rmse': float(selected['rmse']),
                'smape_pct': float(selected['smape_pct']),
                'bias_forecast_minus_actual': float(selected['bias_forecast_minus_actual']),
                'residual_lag1_autocorrelation': float(selected['residual_lag1_autocorrelation']),
                'ljung_box_lag': selected['ljung_box_lag'],
                'ljung_box_statistic': float(selected['ljung_box_statistic']),
                'ljung_box_p_value': float(selected['ljung_box_p_value']),
                **gate,
            }
        ]
    )

    metrics = {
        'method': METHOD_LABELS[selected_model],
        'selected_model': selected_model,
        'selected_model_label': METHOD_LABELS[selected_model],
        'mae': float(selected['mae']),
        'rmse': float(selected['rmse']),
        'smape_pct': float(selected['smape_pct']),
        'bias': float(selected['bias_forecast_minus_actual']),
        'backtest_periods': int(selected['backtest_periods']),
        'backtest_start': pd.Timestamp(selected['backtest_start']).strftime('%Y-%m-%d'),
        'backtest_end': pd.Timestamp(selected['backtest_end']).strftime('%Y-%m-%d'),
        'residual_lag1_autocorrelation': float(selected['residual_lag1_autocorrelation']),
        'ljung_box_lag': (
            int(selected['ljung_box_lag'])
            if pd.notna(selected['ljung_box_lag'])
            else None
        ),
        'ljung_box_statistic': (
            float(selected['ljung_box_statistic'])
            if pd.notna(selected['ljung_box_statistic'])
            else None
        ),
        'ljung_box_p_value': (
            float(selected['ljung_box_p_value'])
            if pd.notna(selected['ljung_box_p_value'])
            else None
        ),
        **gate,
        'candidate_models': list(CANDIDATE_METHODS),
        'forecast_horizon_months': int(horizon),
        'forecast_semantics': 'model_derived_synthetic_demand_forecast',
        'note': (
            'Selected from rolling-origin one-step-ahead comparison. '
            'Synthetic backtest performance does not establish real-world forecast accuracy.'
        ),
    }

    return metrics, backtest, future, comparison, diagnostics
