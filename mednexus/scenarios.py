from __future__ import annotations

import json

import numpy as np
import pandas as pd


SCENARIO_DEFINITIONS = [
    {
        'scenario': 'Baseline',
        'downtime_reduction_pct': 0.0,
        'defect_reduction_pct': 0.0,
        'workforce_capacity_change_pct': 0.0,
        'scenario_type': 'baseline',
    },
    {
        'scenario': 'Targeted reliability',
        'downtime_reduction_pct': 15.0,
        'defect_reduction_pct': 0.0,
        'workforce_capacity_change_pct': 0.0,
        'scenario_type': 'single_lever',
    },
    {
        'scenario': 'Quality improvement',
        'downtime_reduction_pct': 0.0,
        'defect_reduction_pct': 12.0,
        'workforce_capacity_change_pct': 0.0,
        'scenario_type': 'single_lever',
    },
    {
        'scenario': 'Workforce recovery',
        'downtime_reduction_pct': 0.0,
        'defect_reduction_pct': 0.0,
        'workforce_capacity_change_pct': 5.0,
        'scenario_type': 'single_lever',
    },
    {
        'scenario': 'Combined intervention',
        'downtime_reduction_pct': 15.0,
        'defect_reduction_pct': 12.0,
        'workforce_capacity_change_pct': 5.0,
        'scenario_type': 'multi_lever',
    },
]


def _validate_latest_row(base: pd.Series) -> None:
    required = [
        'month',
        'unplanned_downtime_min',
        'defect_units',
        'capacity_gap_pct',
        'good_units',
        'downtime_cost',
        'scrap_cost',
    ]
    missing = [c for c in required if c not in base.index]
    if missing:
        raise ValueError(f'Scenario engine missing required baseline fields: {missing}')

    numeric = [c for c in required if c != 'month']
    if pd.isna(base[numeric]).any():
        bad = [c for c in numeric if pd.isna(base[c])]
        raise ValueError(f'Scenario baseline contains missing required values: {bad}')

    if (base[numeric] < 0).any():
        bad = [c for c in numeric if float(base[c]) < 0]
        raise ValueError(f'Scenario baseline contains negative values: {bad}')


def _throughput_gain_fraction(dt_red: float, defect_red: float, wf_change: float) -> float:
    # Illustrative response relationship retained from the original transparent scenario baseline.
    # This is a simulation assumption, not an estimated causal response function.
    return float((dt_red * 0.20 + defect_red * 0.08 + wf_change * 0.35) / 100.0)


def _expected_change_text(dt_red: float, defect_red: float, wf_change: float) -> str:
    changes = []
    if dt_red:
        changes.append(f'unplanned downtime reduced by {dt_red:.1f}%')
    if defect_red:
        changes.append(f'defect units reduced by {defect_red:.1f}%')
    if wf_change:
        changes.append(f'capacity gap reduced by {wf_change:.1f} percentage points')
    return '; '.join(changes) if changes else 'No intervention change; baseline retained.'


def _assumption_text(dt_red: float, defect_red: float, wf_change: float) -> str:
    return (
        f'Downtime reduction={dt_red:.1f}%; defect reduction={defect_red:.1f}%; '
        f'workforce capacity-gap change={wf_change:.1f} percentage points. '
        'Throughput response uses the documented illustrative scenario relationship.'
    )


def build_scenario_outputs(mart: pd.DataFrame) -> pd.DataFrame:
    if mart.empty:
        raise ValueError('Scenario engine requires a non-empty enterprise monthly mart.')

    base = mart.iloc[-1].copy()
    _validate_latest_row(base)

    baseline_month = str(base['month'])
    rows = []

    for spec in SCENARIO_DEFINITIONS:
        name = spec['scenario']
        dt_red = float(spec['downtime_reduction_pct'])
        defect_red = float(spec['defect_reduction_pct'])
        wf_change = float(spec['workforce_capacity_change_pct'])

        simulated_downtime = float(base['unplanned_downtime_min']) * (1.0 - dt_red / 100.0)
        simulated_defects = float(base['defect_units']) * (1.0 - defect_red / 100.0)
        simulated_capacity_gap = max(
            0.0,
            float(base['capacity_gap_pct']) - wf_change / 100.0,
        )
        throughput_gain = _throughput_gain_fraction(dt_red, defect_red, wf_change)
        simulated_good_units = float(base['good_units']) * (1.0 + throughput_gain)

        downtime_value = float(base['downtime_cost']) * (dt_red / 100.0)
        scrap_value = float(base['scrap_cost']) * (defect_red / 100.0)
        simulated_value = downtime_value + scrap_value

        rows.append(
            {
                'scenario': name,
                'scenario_type': spec['scenario_type'],
                'scenario_status': 'SIMULATED',
                'baseline_month': baseline_month,
                'assumption_summary': _assumption_text(dt_red, defect_red, wf_change),
                'expected_change_summary': _expected_change_text(dt_red, defect_red, wf_change),
                'downtime_reduction_pct': dt_red,
                'defect_reduction_pct': defect_red,
                'workforce_capacity_change_pct': wf_change,
                'baseline_downtime_min': float(base['unplanned_downtime_min']),
                'simulated_downtime_min': simulated_downtime,
                'difference_downtime_min': simulated_downtime - float(base['unplanned_downtime_min']),
                'baseline_defect_units': float(base['defect_units']),
                'simulated_defect_units': simulated_defects,
                'difference_defect_units': simulated_defects - float(base['defect_units']),
                'baseline_capacity_gap_pct': float(base['capacity_gap_pct']),
                'simulated_capacity_gap_pct': simulated_capacity_gap,
                'difference_capacity_gap_pct': simulated_capacity_gap - float(base['capacity_gap_pct']),
                'baseline_good_units': float(base['good_units']),
                'simulated_good_units': simulated_good_units,
                'difference_good_units': simulated_good_units - float(base['good_units']),
                'baseline_downtime_cost': float(base['downtime_cost']),
                'baseline_scrap_cost': float(base['scrap_cost']),
                'simulated_downtime_value_proxy': downtime_value,
                'simulated_scrap_value_proxy': scrap_value,
                'simulated_opportunity_value': simulated_value,
                'value_semantics': 'SIMULATED_OPPORTUNITY_NOT_REALIZED_SAVINGS',
                'response_function_status': 'ILLUSTRATIVE_ASSUMPTION_NOT_CAUSAL',
                'result_summary': (
                    f'Simulated downtime={simulated_downtime:.1f} min; '
                    f'defects={simulated_defects:.1f}; '
                    f'capacity gap={simulated_capacity_gap:.3%}; '
                    f'good units={simulated_good_units:.1f}.'
                ),
            }
        )

    out = pd.DataFrame(rows)
    baseline = out['scenario'].eq('Baseline')
    out['decision_priority_rank'] = np.nan

    candidates = out.loc[~baseline].copy()
    if not candidates.empty:
        ranked = candidates.sort_values(
            ['simulated_opportunity_value', 'difference_good_units'],
            ascending=[False, False],
        ).index
        rank_map = {idx: rank for rank, idx in enumerate(ranked, start=1)}
        out.loc[~baseline, 'decision_priority_rank'] = out.loc[~baseline].index.map(rank_map)

    out.loc[baseline, 'decision_priority_rank'] = 0
    out['decision_priority_rank'] = out['decision_priority_rank'].astype(int)
    out['ranking_semantics'] = (
        'Scenario-prioritization heuristic based on simulated opportunity value, not mathematical optimization.'
    )
    return out


def build_scenario_assumptions(scenarios: pd.DataFrame) -> pd.DataFrame:
    rows = []
    lever_map = [
        ('downtime_reduction_pct', 'Unplanned downtime reduction', 'percent'),
        ('defect_reduction_pct', 'Defect reduction', 'percent'),
        ('workforce_capacity_change_pct', 'Workforce capacity-gap improvement', 'percentage_points'),
    ]

    for scenario in scenarios.itertuples(index=False):
        for field, lever, unit in lever_map:
            value = float(getattr(scenario, field))
            rows.append(
                {
                    'scenario': scenario.scenario,
                    'scenario_status': scenario.scenario_status,
                    'lever': lever,
                    'assumption_value': value,
                    'unit': unit,
                    'assumption_classification': 'ILLUSTRATIVE_ASSUMPTION',
                    'causal_status': 'NOT_CAUSAL',
                }
            )

    return pd.DataFrame(rows)


def build_monitoring_plan(scenarios: pd.DataFrame) -> pd.DataFrame:
    outcomes = [
        {
            'metric': 'unplanned_downtime_min',
            'baseline_field': 'baseline_downtime_min',
            'simulated_field': 'simulated_downtime_min',
            'direction': 'lower_is_better',
            'review_frequency': 'weekly',
            'owner': 'Maintenance Manager',
        },
        {
            'metric': 'defect_units',
            'baseline_field': 'baseline_defect_units',
            'simulated_field': 'simulated_defect_units',
            'direction': 'lower_is_better',
            'review_frequency': 'weekly',
            'owner': 'Quality Manager',
        },
        {
            'metric': 'capacity_gap_pct',
            'baseline_field': 'baseline_capacity_gap_pct',
            'simulated_field': 'simulated_capacity_gap_pct',
            'direction': 'lower_is_better',
            'review_frequency': 'monthly',
            'owner': 'HR & Operations',
        },
        {
            'metric': 'good_units',
            'baseline_field': 'baseline_good_units',
            'simulated_field': 'simulated_good_units',
            'direction': 'higher_is_better',
            'review_frequency': 'weekly',
            'owner': 'Operations Manager',
        },
    ]

    rows = []
    for scenario in scenarios.itertuples(index=False):
        if scenario.scenario == 'Baseline':
            continue
        for spec in outcomes:
            rows.append(
                {
                    'scenario': scenario.scenario,
                    'metric': spec['metric'],
                    'baseline_value': float(getattr(scenario, spec['baseline_field'])),
                    'simulated_expected_value': float(getattr(scenario, spec['simulated_field'])),
                    'direction': spec['direction'],
                    'review_frequency': spec['review_frequency'],
                    'owner': spec['owner'],
                    'validation_design': 'PRE_POST_OR_CONTROLLED_COMPARISON_IF_IMPLEMENTED',
                    'minimum_evidence_before_causal_claim': (
                        'Observed post-intervention data plus an appropriate comparison/identification strategy.'
                    ),
                    'decision_rule': (
                        'Compare observed post-intervention result with baseline and simulated expectation; '
                        'do not attribute causality without a valid design.'
                    ),
                    'status': 'MONITORING_PLAN_ONLY_NOT_EXECUTED',
                }
            )
    return pd.DataFrame(rows)


def optimization_gate() -> dict:
    missing_evidence = [
        'observed intervention implementation costs by lever',
        'validated budget/resource constraints',
        'validated causal or prospectively supported response functions',
        'capacity/resource consumption per intervention',
        'management objective trade-off weights or utility function',
    ]

    return {
        'optimization_status': 'NOT_ADMITTED_INSUFFICIENT_DECISION_MODEL_EVIDENCE',
        'solver_executed': False,
        'recommendation_type': 'SCENARIO_PRIORITIZATION_ONLY',
        'objective_function_status': 'NOT_DEFENSIBLE_FOR_OPTIMIZATION',
        'constraint_model_status': 'NOT_DEFENSIBLE_FOR_OPTIMIZATION',
        'response_function_status': 'ILLUSTRATIVE_SCENARIO_RELATIONSHIPS_ONLY',
        'missing_required_evidence': missing_evidence,
        'admission_rule': (
            'Optimization may be implemented only when the objective, decision variables, '
            'intervention costs, resource/budget constraints and response functions are defensible.'
        ),
        'current_decision': (
            'Keep scenario comparison and prioritization; do not claim a mathematically optimal intervention.'
        ),
    }


def run_scenarios(mart: pd.DataFrame):
    scenarios = build_scenario_outputs(mart)
    assumptions = build_scenario_assumptions(scenarios)
    monitoring = build_monitoring_plan(scenarios)
    gate = optimization_gate()

    methodology = {
        'scenario_status': 'SIMULATED',
        'scenario_count_including_baseline': int(len(scenarios)),
        'canonical_flow': [
            'Baseline',
            'Assumption',
            'Expected Change',
            'Result',
            'Difference',
            'Monitoring',
        ],
        'baseline_period': str(scenarios['baseline_month'].iloc[0]),
        'ranking_basis': (
            'Simulated opportunity value, then simulated good-unit improvement. '
            'This is a prioritization heuristic, not mathematical optimization.'
        ),
        'financial_semantics': 'SIMULATED_OPPORTUNITY_NOT_REALIZED_SAVINGS',
        'causal_claim': False,
        'optimization_status': gate['optimization_status'],
        'limitations': [
            'Scenario response relationships are illustrative assumptions.',
            'Simulated opportunity values are not realized savings.',
            'No causal intervention effect is claimed.',
            'Optimization is not admitted without defensible objective, constraints, costs and response functions.',
        ],
    }

    return {
        'scenarios': scenarios,
        'assumptions': assumptions,
        'monitoring_plan': monitoring,
        'optimization_gate': gate,
        'methodology': methodology,
    }
