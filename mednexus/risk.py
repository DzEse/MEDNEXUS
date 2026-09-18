from __future__ import annotations

import numpy as np
import pandas as pd


COMPONENTS = (
    'quality',
    'equipment',
    'downtime',
    'capacity',
    'supply',
    'logistics',
    'workforce',
    'technology',
)

BASE_THRESHOLDS = {
    'stable_upper_exclusive': 25.0,
    'watch_upper_exclusive': 50.0,
    'elevated_upper_exclusive': 75.0,
}

WEIGHT_PERTURBATION = 0.25
THRESHOLD_SHIFT_POINTS = 5.0


def _validate_weights(weights: dict) -> dict[str, float]:
    if set(weights) != set(COMPONENTS):
        missing = sorted(set(COMPONENTS).difference(weights))
        extra = sorted(set(weights).difference(COMPONENTS))
        raise ValueError(f'MORI weight keys invalid. Missing={missing}; extra={extra}')

    validated = {component: float(weights[component]) for component in COMPONENTS}
    values = np.asarray(list(validated.values()), dtype=float)
    if not np.isfinite(values).all():
        raise ValueError('MORI weights must be finite.')
    if (values < 0).any():
        raise ValueError('MORI weights cannot be negative.')
    if not np.isclose(values.sum(), 1.0, atol=1e-9):
        raise ValueError(f'MORI weights must sum to 1.0; found {values.sum():.12f}.')
    return validated


def _norm(series: pd.Series, inverse: bool = False) -> pd.Series:
    s = pd.to_numeric(series, errors='coerce').astype(float)
    valid = s.dropna()
    out = pd.Series(np.nan, index=s.index, dtype=float)

    if valid.empty:
        return out

    lo = float(valid.min())
    hi = float(valid.max())
    if np.isclose(hi, lo):
        out.loc[valid.index] = 0.0
    else:
        out.loc[valid.index] = (valid - lo) / (hi - lo)

    if inverse:
        out.loc[valid.index] = 1.0 - out.loc[valid.index]

    return out.clip(0.0, 1.0)


def _risk_components(mart: pd.DataFrame) -> pd.DataFrame:
    required = {
        'month',
        'defect_units',
        'total_units',
        'unplanned_downtime_min',
        'downtime_cost',
        'capacity_gap_pct',
        'shortage_hours',
        'on_time_delivery',
        'overtime_hours',
        'technology_downtime_min',
    }
    missing = required.difference(mart.columns)
    if missing:
        raise ValueError(f'MORI mart is missing required columns: {sorted(missing)}')

    m = mart.copy()
    total_units = pd.to_numeric(m['total_units'], errors='coerce').replace(0, np.nan)
    defect_rate = pd.to_numeric(m['defect_units'], errors='coerce') / total_units

    components = pd.DataFrame({'month': m['month']})
    components['quality'] = _norm(defect_rate)
    components['equipment'] = _norm(m['unplanned_downtime_min'])
    components['downtime'] = _norm(m['downtime_cost'])
    components['capacity'] = _norm(m['capacity_gap_pct'])
    components['supply'] = _norm(m['shortage_hours'])
    components['logistics'] = _norm(m['on_time_delivery'], inverse=True)
    components['workforce'] = _norm(m['overtime_hours'])
    components['technology'] = _norm(m['technology_downtime_min'])
    return components


def _bands(scores: pd.Series, thresholds: dict | None = None) -> pd.Series:
    t = thresholds or BASE_THRESHOLDS
    stable = float(t['stable_upper_exclusive'])
    watch = float(t['watch_upper_exclusive'])
    elevated = float(t['elevated_upper_exclusive'])

    if not (0 < stable < watch < elevated <= 100):
        raise ValueError('MORI thresholds must be strictly increasing within 0-100.')

    s = pd.to_numeric(scores, errors='coerce')
    values = np.select(
        [
            s < stable,
            (s >= stable) & (s < watch),
            (s >= watch) & (s < elevated),
            s >= elevated,
        ],
        ['Stable', 'Watch', 'Elevated', 'Critical'],
        default='Unavailable',
    )
    values[pd.isna(s)] = 'Unavailable'
    return pd.Series(values, index=s.index, dtype='object')


def build_mori(mart: pd.DataFrame, weights: dict) -> pd.DataFrame:
    validated_weights = _validate_weights(weights)
    components = _risk_components(mart)

    component_matrix = components[list(COMPONENTS)]
    components['missing_component_count'] = component_matrix.isna().sum(axis=1).astype(int)
    components['available_weight'] = component_matrix.notna().mul(
        pd.Series(validated_weights)
    ).sum(axis=1)
    components['score_status'] = np.where(
        components['missing_component_count'].eq(0),
        'COMPLETE',
        'UNAVAILABLE_MISSING_COMPONENTS',
    )

    score = np.zeros(len(components), dtype=float)
    for component, weight in validated_weights.items():
        contribution = components[component] * weight * 100.0
        components[f'{component}_contribution'] = contribution
        score += contribution.fillna(0.0).to_numpy()

    complete = components['missing_component_count'].eq(0)
    components['mori_score'] = np.where(complete, np.clip(score, 0.0, 100.0), np.nan)
    components['mori_band'] = _bands(components['mori_score'])
    components['index_semantics'] = 'project_defined_composite_index'
    components['missing_data_policy'] = 'fail_closed_no_partial_score'
    components['normalization_method'] = 'full_available_history_min_max'
    return components


def component_contributions(mori: pd.DataFrame, weights: dict) -> pd.DataFrame:
    validated_weights = _validate_weights(weights)
    rows = []
    for row in mori.itertuples(index=False):
        for component in COMPONENTS:
            score = getattr(row, component)
            contribution = getattr(row, f'{component}_contribution')
            rows.append(
                {
                    'month': row.month,
                    'component': component,
                    'configured_weight': validated_weights[component],
                    'normalized_risk': score,
                    'weighted_contribution_points': contribution,
                    'mori_score': row.mori_score,
                    'mori_band': row.mori_band,
                    'score_status': row.score_status,
                    'interpretation': (
                        'Component contribution to project-defined MORI; not an industry-standard risk weight.'
                    ),
                }
            )
    return pd.DataFrame(rows)


def _perturb_weights(weights: dict, component: str, factor: float) -> dict[str, float]:
    validated = _validate_weights(weights)
    raw = validated.copy()
    raw[component] = raw[component] * factor
    total = sum(raw.values())
    if total <= 0:
        raise ValueError('Perturbed MORI weights must have positive total weight.')
    return {name: value / total for name, value in raw.items()}


def weight_sensitivity(mart: pd.DataFrame, weights: dict) -> pd.DataFrame:
    baseline = build_mori(mart, weights)[['month', 'mori_score', 'mori_band']].rename(
        columns={'mori_score': 'baseline_score', 'mori_band': 'baseline_band'}
    )
    scenarios = []

    baseline_weights = _validate_weights(weights)
    baseline_run = build_mori(mart, baseline_weights)
    base = baseline_run[['month', 'mori_score', 'mori_band']].copy()
    base['scenario'] = 'baseline'
    base['perturbed_component'] = 'none'
    base['relative_weight_change'] = 0.0
    base['weight_vector'] = str(baseline_weights)
    scenarios.append(base)

    for component in COMPONENTS:
        for direction, factor in (
            ('down_25pct', 1.0 - WEIGHT_PERTURBATION),
            ('up_25pct', 1.0 + WEIGHT_PERTURBATION),
        ):
            scenario_weights = _perturb_weights(weights, component, factor)
            run = build_mori(mart, scenario_weights)[['month', 'mori_score', 'mori_band']].copy()
            run['scenario'] = f'{component}_{direction}'
            run['perturbed_component'] = component
            run['relative_weight_change'] = factor - 1.0
            run['weight_vector'] = str(scenario_weights)
            scenarios.append(run)

    out = pd.concat(scenarios, ignore_index=True)
    out = out.merge(baseline, on='month', how='left', validate='many_to_one')
    out['score_delta_vs_baseline'] = out['mori_score'] - out['baseline_score']
    out['absolute_score_delta'] = out['score_delta_vs_baseline'].abs()
    out['band_changed_vs_baseline'] = out['mori_band'] != out['baseline_band']
    return out


def threshold_sensitivity(mori: pd.DataFrame) -> pd.DataFrame:
    scenarios = {
        'base_thresholds': BASE_THRESHOLDS,
        'thresholds_minus_5_points': {
            'stable_upper_exclusive': 20.0,
            'watch_upper_exclusive': 45.0,
            'elevated_upper_exclusive': 70.0,
        },
        'thresholds_plus_5_points': {
            'stable_upper_exclusive': 30.0,
            'watch_upper_exclusive': 55.0,
            'elevated_upper_exclusive': 80.0,
        },
    }

    baseline_band = _bands(mori['mori_score'], BASE_THRESHOLDS)
    rows = []
    for scenario, thresholds in scenarios.items():
        bands = _bands(mori['mori_score'], thresholds)
        for idx, month in enumerate(mori['month']):
            rows.append(
                {
                    'month': month,
                    'threshold_scenario': scenario,
                    'stable_upper_exclusive': thresholds['stable_upper_exclusive'],
                    'watch_upper_exclusive': thresholds['watch_upper_exclusive'],
                    'elevated_upper_exclusive': thresholds['elevated_upper_exclusive'],
                    'mori_score': mori['mori_score'].iloc[idx],
                    'mori_band': bands.iloc[idx],
                    'baseline_band': baseline_band.iloc[idx],
                    'band_changed_vs_baseline': bands.iloc[idx] != baseline_band.iloc[idx],
                }
            )
    return pd.DataFrame(rows)


def sensitivity_summary(
    mori: pd.DataFrame,
    weight_results: pd.DataFrame,
    threshold_results: pd.DataFrame,
) -> dict:
    complete = mori[mori['score_status'] == 'COMPLETE']
    if complete.empty:
        raise RuntimeError('MORI sensitivity cannot summarize an entirely unavailable index.')

    latest_month = complete['month'].iloc[-1]
    latest_score = float(complete['mori_score'].iloc[-1])
    latest_band = str(complete['mori_band'].iloc[-1])

    latest_weight = weight_results[weight_results['month'] == latest_month]
    nonbaseline_weight = latest_weight[latest_weight['scenario'] != 'baseline']
    latest_threshold = threshold_results[threshold_results['month'] == latest_month]

    return {
        'latest_month': str(latest_month),
        'baseline_latest_score': latest_score,
        'baseline_latest_band': latest_band,
        'weight_perturbation_relative': WEIGHT_PERTURBATION,
        'weight_sensitivity_latest_min_score': float(nonbaseline_weight['mori_score'].min()),
        'weight_sensitivity_latest_max_score': float(nonbaseline_weight['mori_score'].max()),
        'weight_sensitivity_latest_max_absolute_delta': float(
            nonbaseline_weight['absolute_score_delta'].max()
        ),
        'weight_sensitivity_latest_band_changes': int(
            nonbaseline_weight['band_changed_vs_baseline'].sum()
        ),
        'weight_sensitivity_all_period_band_change_rate': float(
            weight_results.loc[
                weight_results['scenario'] != 'baseline', 'band_changed_vs_baseline'
            ].mean()
        ),
        'threshold_shift_points': THRESHOLD_SHIFT_POINTS,
        'threshold_sensitivity_latest_bands': sorted(
            latest_threshold['mori_band'].dropna().astype(str).unique().tolist()
        ),
        'threshold_sensitivity_latest_band_changes': int(
            latest_threshold['band_changed_vs_baseline'].sum()
        ),
        'missing_data_policy': 'fail_closed_no_partial_score',
        'normalization_method': 'full_available_history_min_max',
        'interpretation': (
            'Sensitivity evidence tests dependence on configured weights and band thresholds. '
            'It does not establish MORI as an externally validated risk scale.'
        ),
    }


def run_mori_validation(mart: pd.DataFrame, weights: dict) -> dict:
    mori = build_mori(mart, weights)
    contributions = component_contributions(mori, weights)
    weight_results = weight_sensitivity(mart, weights)
    threshold_results = threshold_sensitivity(mori)
    summary = sensitivity_summary(mori, weight_results, threshold_results)

    methodology = {
        'index_name': 'MEDNEXUS Operational Risk Index (MORI)',
        'index_status': 'project_defined_not_industry_standard',
        'components': list(COMPONENTS),
        'weights': _validate_weights(weights),
        'normalization': (
            'Per-component min-max normalization across the full available canonical history; '
            'logistics is inverted so lower on-time delivery produces higher risk.'
        ),
        'score_construction': 'Sum(normalized_component_risk * configured_weight) * 100',
        'bands': {
            'Stable': '0 <= score < 25',
            'Watch': '25 <= score < 50',
            'Elevated': '50 <= score < 75',
            'Critical': '75 <= score <= 100',
        },
        'missing_data_policy': (
            'Fail closed by month: if any required MORI component is missing, do not renormalize '
            'remaining weights and do not produce a partial composite score.'
        ),
        'sensitivity': (
            'Each configured component weight is perturbed +/-25% one at a time and the full '
            'weight vector is renormalized to sum to 1. Band thresholds are also shifted +/-5 points.'
        ),
        'limitations': [
            'MORI is project-defined and has no external calibration or industry-standard status.',
            'Full-history min-max normalization makes historical scores relative to the current dataset and can change when history expands.',
            'Component weights are analytical design choices rather than empirically estimated causal weights.',
            'Correlated components can double-count related operational pressure.',
            'Band thresholds are governance choices, not externally validated risk cutoffs.',
            'Sensitivity analysis assesses robustness to design choices but does not validate real-world risk outcomes.',
        ],
    }
    return {
        'mori': mori,
        'contributions': contributions,
        'weight_sensitivity': weight_results,
        'threshold_sensitivity': threshold_results,
        'sensitivity_summary': summary,
        'methodology': methodology,
    }
