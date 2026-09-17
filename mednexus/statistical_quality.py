from __future__ import annotations

import numpy as np
import pandas as pd


def methodology_gates() -> pd.DataFrame:
    """Explicitly record which requested quality methods are supportable."""
    rows = [
        {
            'method': 'First Pass Yield (FPY)',
            'status': 'IMPLEMENTED',
            'reason': 'Synthetic defect_units represent units failing the first pass; total_count - defect_units therefore represents units passing without rework.',
            'required_evidence': 'total_count and defect_units at production-order grain',
        },
        {
            'method': 'Rolled Throughput Yield (RTY)',
            'status': 'NOT_CALCULABLE',
            'reason': 'Sequential process-stage yields are not modeled.',
            'required_evidence': 'ordered stage-level first-pass yields for the same units',
        },
        {
            'method': 'DPMO',
            'status': 'NOT_CALCULABLE',
            'reason': 'Defect opportunities per unit are undefined.',
            'required_evidence': 'defect count, units, and defensible opportunities per unit',
        },
        {
            'method': 'p chart',
            'status': 'IMPLEMENTED',
            'reason': 'Daily plant-level defective-unit proportions have varying subgroup sizes and support a binomial proportion chart.',
            'required_evidence': 'defect_units and total_count by rational daily plant subgroup',
        },
        {
            'method': 'Cp/Cpk/Pp/Ppk',
            'status': 'NOT_CALCULABLE',
            'reason': 'No valid engineering specification limits exist in the canonical synthetic data.',
            'required_evidence': 'validated USL/LSL and a continuous quality characteristic with suitable distribution/stability assessment',
        },
        {
            'method': 'Startup Reject loss',
            'status': 'NOT_CALCULABLE',
            'reason': 'The production data does not identify startup-period rejects separately from other defects.',
            'required_evidence': 'startup/changeover phase marker plus rejected-unit counts',
        },
        {
            'method': 'Full COPQ',
            'status': 'NOT_CALCULABLE',
            'reason': 'Rework labor/time cost and external failure cost are not separately observed.',
            'required_evidence': 'rework resource cost, appraisal/prevention policy if included, and external failure cost definitions',
        },
    ]
    return pd.DataFrame(rows)


def p_chart_by_plant(production: pd.DataFrame) -> pd.DataFrame:
    p = production.copy()
    p['date'] = pd.to_datetime(p['date'])
    daily = (
        p.groupby(['plant_id', 'date'], as_index=False)
        .agg(total_count=('total_count', 'sum'), defect_units=('defect_units', 'sum'))
        .sort_values(['plant_id', 'date'])
    )
    daily['defect_rate'] = daily['defect_units'] / daily['total_count'].replace(0, np.nan)

    totals = (
        daily.groupby('plant_id', as_index=False)
        .agg(plant_defects=('defect_units', 'sum'), plant_units=('total_count', 'sum'))
    )
    totals['center_line'] = totals['plant_defects'] / totals['plant_units'].replace(0, np.nan)
    daily = daily.merge(totals[['plant_id', 'center_line']], on='plant_id', how='left')

    se = np.sqrt(
        daily['center_line'] * (1 - daily['center_line']) / daily['total_count'].replace(0, np.nan)
    )
    daily['lcl'] = (daily['center_line'] - 3 * se).clip(lower=0)
    daily['ucl'] = (daily['center_line'] + 3 * se).clip(upper=1)
    daily['out_of_control'] = (
        (daily['defect_rate'] < daily['lcl']) | (daily['defect_rate'] > daily['ucl'])
    ).astype(int)
    daily['interpretation'] = np.where(
        daily['out_of_control'].eq(1),
        'Statistical signal requiring investigation; not proof of a causal special cause.',
        'Within calculated p-chart limits.',
    )
    return daily


def p_chart_summary(p_chart: pd.DataFrame) -> pd.DataFrame:
    return (
        p_chart.groupby('plant_id', as_index=False)
        .agg(
            observations=('date', 'count'),
            center_line=('center_line', 'first'),
            mean_defect_rate=('defect_rate', 'mean'),
            out_of_control_points=('out_of_control', 'sum'),
        )
    )


def six_big_losses(frames) -> pd.DataFrame:
    production = frames['fact_production'].copy()
    production['date'] = pd.to_datetime(production['date'])
    production['month'] = production['date'].dt.to_period('M').astype(str)

    downtime = frames['fact_downtime'].copy()
    downtime['date'] = pd.to_datetime(downtime['date'])
    downtime['month'] = downtime['date'].dt.to_period('M').astype(str)

    downtime_map = {
        'Equipment Failure': 'Equipment Failure',
        'Setup Adjustment': 'Setup & Adjustment',
        'Minor Stop': 'Idling & Minor Stops',
    }
    supported_downtime = downtime[downtime['downtime_reason'].isin(downtime_map)].copy()
    supported_downtime['loss_category'] = supported_downtime['downtime_reason'].map(downtime_map)
    dt = (
        supported_downtime.groupby(['month', 'loss_category'], as_index=False)
        .agg(loss_minutes=('duration_min', 'sum'))
    )
    dt['loss_units_equivalent'] = np.nan
    dt['basis'] = 'Observed downtime-event minutes'

    production['runtime_theoretical_units'] = production['run_time_min'] / production['ideal_cycle_min'].clip(lower=0.01)
    production['reduced_speed_units'] = (
        production['runtime_theoretical_units'] - production['total_count']
    ).clip(lower=0)
    production['reduced_speed_loss_min'] = (
        production['reduced_speed_units'] * production['ideal_cycle_min']
    )
    speed = (
        production.groupby('month', as_index=False)
        .agg(
            loss_minutes=('reduced_speed_loss_min', 'sum'),
            loss_units_equivalent=('reduced_speed_units', 'sum'),
        )
    )
    speed['loss_category'] = 'Reduced Speed'
    speed['basis'] = 'Derived from run-time theoretical output minus actual total count'

    production['first_pass_defect_loss_min_proxy'] = (
        production['defect_units'] * production['ideal_cycle_min']
    )
    defects = (
        production.groupby('month', as_index=False)
        .agg(
            loss_minutes=('first_pass_defect_loss_min_proxy', 'sum'),
            loss_units_equivalent=('defect_units', 'sum'),
        )
    )
    defects['loss_category'] = 'Process Defects'
    defects['basis'] = 'Time-equivalent proxy: first-pass defective units x ideal cycle time'

    combined = pd.concat(
        [
            dt[['month', 'loss_category', 'loss_minutes', 'loss_units_equivalent', 'basis']],
            speed[['month', 'loss_category', 'loss_minutes', 'loss_units_equivalent', 'basis']],
            defects[['month', 'loss_category', 'loss_minutes', 'loss_units_equivalent', 'basis']],
        ],
        ignore_index=True,
    )
    combined['status'] = 'CALCULATED'

    startup = pd.DataFrame({
        'month': sorted(production['month'].unique()),
        'loss_category': 'Startup Rejects',
        'loss_minutes': np.nan,
        'loss_units_equivalent': np.nan,
        'basis': 'Not calculable: startup-period rejects are not identified separately.',
        'status': 'NOT_CALCULABLE',
    })
    return pd.concat([combined, startup], ignore_index=True).sort_values(['month', 'loss_category'])


def capacity_waterfall(production: pd.DataFrame) -> pd.DataFrame:
    p = production.copy()
    p['date'] = pd.to_datetime(p['date'])
    p['month'] = p['date'].dt.to_period('M').astype(str)
    cycle = p['ideal_cycle_min'].clip(lower=0.01)

    p['theoretical_units'] = p['planned_production_min'] / cycle
    p['planned_downtime_loss_units'] = p['planned_downtime_min'] / cycle
    p['unplanned_downtime_loss_units'] = p['unplanned_downtime_min'] / cycle
    p['runtime_theoretical_units'] = p['run_time_min'] / cycle
    p['speed_loss_units'] = (p['runtime_theoretical_units'] - p['total_count']).clip(lower=0)
    p['quality_loss_units'] = (p['total_count'] - p['good_count']).clip(lower=0)

    monthly = p.groupby('month', as_index=False).agg(
        theoretical_units=('theoretical_units', 'sum'),
        planned_downtime_loss_units=('planned_downtime_loss_units', 'sum'),
        unplanned_downtime_loss_units=('unplanned_downtime_loss_units', 'sum'),
        speed_loss_units=('speed_loss_units', 'sum'),
        quality_loss_units=('quality_loss_units', 'sum'),
        good_units=('good_count', 'sum'),
    )

    rows = []
    for r in monthly.itertuples(index=False):
        values = [
            ('Theoretical Capacity', r.theoretical_units, 'starting_capacity'),
            ('Planned Downtime', -r.planned_downtime_loss_units, 'loss'),
            ('Unplanned Downtime', -r.unplanned_downtime_loss_units, 'loss'),
            ('Speed Loss', -r.speed_loss_units, 'loss'),
            ('Quality Loss', -r.quality_loss_units, 'loss'),
            ('Good Production', r.good_units, 'result'),
        ]
        for order, (stage, units, stage_type) in enumerate(values, start=1):
            rows.append({
                'month': r.month,
                'stage_order': order,
                'stage': stage,
                'stage_type': stage_type,
                'units_equivalent': float(units),
            })
    return pd.DataFrame(rows)


def value_leakage(frames) -> pd.DataFrame:
    production = frames['fact_production'].copy()
    production['month'] = pd.to_datetime(production['date']).dt.to_period('M').astype(str)
    prod = production.groupby('month', as_index=False).agg(
        total_units=('total_count', 'sum'),
        good_units=('good_count', 'sum'),
        first_pass_defect_units=('defect_units', 'sum'),
        rework_units=('rework_units', 'sum'),
        scrap_units=('scrap_units', 'sum'),
    )

    finance = frames['fact_finance'].copy()
    finance['month'] = pd.to_datetime(finance['month']).dt.to_period('M').astype(str)
    f = finance[[
        'month',
        'operating_cost',
        'scrap_cost',
        'downtime_cost',
        'logistics_cost',
        'technology_cost',
    ]]

    out = prod.merge(f, on='month', how='left')
    out['cost_per_good_unit'] = out['operating_cost'] / out['good_units'].replace(0, np.nan)
    out['known_internal_quality_cost_proxy'] = out['scrap_cost']
    out['rework_cost'] = np.nan
    out['full_copq'] = np.nan
    out['rework_cost_status'] = 'NOT_CALCULABLE'
    out['copq_status'] = 'NOT_CALCULABLE'
    out['financial_basis'] = (
        'Scrap cost is derived from synthetic material cost; downtime cost uses the documented illustrative $12/min assumption. '
        'Full COPQ is withheld because rework and external-failure costs are not observed.'
    )
    return out
