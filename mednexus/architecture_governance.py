from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd


CATEGORY_FIELDS = {
    'fact_quality': 'defect_category',
    'fact_downtime': 'downtime_reason',
    'fact_maintenance': 'maintenance_type',
    'fact_customer_service': 'issue_type',
    'fact_technology_incident': 'severity',
}


DRIFT_THRESHOLDS = {
    'row_count_relative_change': 0.10,
    'null_rate_absolute_change': 0.02,
    'model_positive_rate_absolute_change': 0.05,
    'kpi_relative_change': 0.20,
}


def build_operations_twin_catalog() -> pd.DataFrame:
    rows = [
        ('Enterprise', 'Plant', 'contains', 'enterprise→plant', 'one row per plant', 'SUPPORTED'),
        ('Plant', 'Line', 'contains', 'plant_id', 'one row per line', 'SUPPORTED'),
        ('Line', 'Machine', 'contains', 'line_id', 'one row per machine', 'SUPPORTED'),
        ('Machine', 'Production', 'operates', 'machine_id', 'one row per machine-day production order', 'SUPPORTED'),
        ('Machine', 'Downtime', 'experiences', 'machine_id', 'one row per downtime event', 'SUPPORTED'),
        ('Machine', 'Quality Event', 'associated_with', 'machine_id', 'one row per quality event', 'SUPPORTED'),
        ('Machine', 'Maintenance', 'receives', 'machine_id', 'one row per maintenance event', 'SUPPORTED'),
        ('Machine', 'Sensor Snapshot', 'measured_by', 'machine_id', 'one row per machine-day sensor snapshot', 'SUPPORTED'),
        ('Plant', 'Workforce', 'staffed_by', 'plant_id', 'one row per plant-month', 'SUPPORTED'),
        ('Plant', 'Recruitment', 'capacity_pipeline', 'plant_id', 'one row per plant-month funnel', 'SUPPORTED'),
        ('Supplier', 'Supply', 'provides', 'supplier_id', 'one row per supplier-month', 'SUPPORTED'),
        ('Customer', 'Order', 'places', 'customer_id', 'one row per order', 'SUPPORTED'),
        ('Product', 'Order', 'requested_as', 'product_id', 'one row per order', 'SUPPORTED'),
        ('Order', 'Shipment', 'fulfilled_by', 'order_id', 'one row per shipment/order', 'SUPPORTED'),
        ('Order', 'Customer Service', 'may_generate', 'order_id', 'one row per service event', 'SUPPORTED'),
        ('Enterprise', 'Finance', 'summarized_by', 'month', 'one row per month', 'SUPPORTED'),
        ('Enterprise', 'Technology Incident', 'depends_on', 'system/date', 'one row per incident', 'SUPPORTED'),
        ('Enterprise', 'SaaS Usage', 'uses', 'system/date', 'one row per system-day', 'SUPPORTED'),
        ('Enterprise', 'Enterprise Monthly Mart', 'integrated_view', 'month', 'one row per month', 'SUPPORTED'),
        ('Enterprise Monthly Mart', 'MORI', 'risk_summary', 'month', 'one row per month', 'SUPPORTED'),
        ('Enterprise Monthly Mart', 'Scenario Outputs', 'simulated_decision_support', 'latest baseline', 'one row per scenario', 'SIMULATED'),
    ]
    out = pd.DataFrame(
        rows,
        columns=[
            'source_entity',
            'target_entity',
            'relationship_type',
            'link_key',
            'target_grain',
            'evidence_status',
        ],
    )
    out['twin_type'] = 'CONCEPTUAL_ENTERPRISE_OPERATIONS_TWIN'
    out['three_dimensional_model'] = False
    return out


def build_output_lineage_registry() -> pd.DataFrame:
    rows = [
        ('ProductionKPI', 'fact_production', 'production_kpis()', 'mart_production_kpi', 'OEE / FPY / throughput', 'Manufacturing pages', 'capacity-loss investigation'),
        ('QualityPChart', 'fact_production', 'p_chart_by_plant()', 'mart_quality_p_chart', 'p-chart signal', 'Quality page', 'process-stability investigation'),
        ('SixBigLosses', 'production + downtime', 'six_big_losses()', 'mart_six_big_losses', 'loss decomposition', 'Manufacturing page', 'loss prioritization'),
        ('ValueLeakage', 'finance + production', 'value_leakage()', 'mart_value_leakage', 'cost-per-good-unit / leakage', 'Finance page', 'value-loss investigation'),
        ('RootCausePriorities', 'production + workforce + machine', 'run_root_cause_analysis()', 'mart_root_cause_priorities', 'association priorities', 'Quality page', 'investigation prioritization'),
        ('PredictiveMaintenanceScores', 'fact_sensor', 'train_predictive_maintenance()', 'scored holdout rows', 'failure risk score', 'Reliability page', 'maintenance investigation'),
        ('DemandForecast', 'fact_orders', 'forecast_demand()', 'future forecast rows', 'model-derived demand', 'Prediction page', 'capacity planning'),
        ('MORI', 'enterprise_monthly_mart', 'run_mori_validation()', 'mart_mori', 'project-defined MORI', 'Executive / Prediction pages', 'cross-domain risk review'),
        ('ScenarioOutputs', 'enterprise_monthly_mart', 'run_scenarios()', 'mart_scenarios', 'simulated differences', 'Scenario page', 'intervention comparison'),
        ('DecisionQueue', 'mart + MORI + reliability + Pareto', 'build_decision_queue()', 'mart_decision_queue', 'priority / owner / urgency', 'Executive / Scenario pages', 'management action review'),
        ('ProcessTransitions', 'orders + shipments', 'run_process_and_experiment_gates()', 'mart_process_transition_summary', 'cycle-time bottleneck', 'Logistics page', 'fulfillment investigation'),
        ('DataTrust', 'quality + RI + observability', 'data_trust_score()', 'data_trust.json', 'project-defined score', 'Technology / Executive pages', 'data reliability review'),
    ]
    return pd.DataFrame(
        rows,
        columns=[
            'output',
            'source',
            'transformation',
            'analytical_table_or_artifact',
            'method_or_metric',
            'bi_surface',
            'decision_supported',
        ],
    )


def build_analysis_design_checklist() -> pd.DataFrame:
    rows = [
        ('business_question', 'What decision-relevant question is being answered?', True),
        ('unit_and_grain', 'What is the unit of analysis and grain?', True),
        ('required_data', 'Which source fields/tables are required and linked validly?', True),
        ('assumptions', 'Which assumptions are observed, derived, illustrative or simulated?', True),
        ('bias_and_leakage', 'What bias, leakage, confounding or selection risks apply?', True),
        ('method_suitability', 'Why is the analytical method appropriate for this data structure?', True),
        ('proof_boundary', 'What does the result prove and explicitly not prove?', True),
        ('validation', 'Which reconciliation, benchmark, test or gate validates the result?', True),
        ('decision_supported', 'Which management action or decision can use the evidence?', True),
        ('monitoring', 'How will the result or intervention be monitored over time?', True),
    ]
    out = pd.DataFrame(rows, columns=['check_id', 'required_question', 'mandatory'])
    out['gate_status'] = 'REQUIRED_FOR_NEW_MAJOR_ANALYSIS'
    return out


def build_drift_profile(
    table_quality: pd.DataFrame,
    model_profile: pd.DataFrame,
    enterprise_mart: pd.DataFrame,
    frames: dict[str, pd.DataFrame] | None = None,
) -> pd.DataFrame:
    rows = []

    for row in table_quality.itertuples(index=False):
        rows.extend([
            {
                'scope': 'table',
                'entity': row.table,
                'metric': 'row_count',
                'value': float(row.row_count),
            },
            {
                'scope': 'table',
                'entity': row.table,
                'metric': 'null_rate',
                'value': float(row.null_rate),
            },
        ])
        schema_numeric = int(hashlib.sha256(str(row.schema_signature).encode('utf-8')).hexdigest()[:12], 16)
        rows.append({
            'scope': 'table',
            'entity': row.table,
            'metric': 'schema_signature_numeric',
            'value': float(schema_numeric),
        })

    if frames is not None:
        for table_name, field in CATEGORY_FIELDS.items():
            if table_name not in frames or field not in frames[table_name].columns:
                continue
            values = sorted(
                frames[table_name][field].dropna().astype(str).unique().tolist()
            )
            payload = '|'.join(values)
            signature_numeric = int(
                hashlib.sha256(payload.encode('utf-8')).hexdigest()[:12], 16
            )
            rows.extend([
                {
                    'scope': 'category',
                    'entity': f'{table_name}.{field}',
                    'metric': 'category_count',
                    'value': float(len(values)),
                },
                {
                    'scope': 'category',
                    'entity': f'{table_name}.{field}',
                    'metric': 'category_set_signature_numeric',
                    'value': float(signature_numeric),
                },
            ])

    target = model_profile.loc[model_profile['role'] == 'target']
    if not target.empty:
        rows.append({
            'scope': 'model',
            'entity': 'predictive_maintenance',
            'metric': 'positive_rate',
            'value': float(target['positive_rate'].iloc[0]),
        })

    latest = enterprise_mart.iloc[-1]
    for metric in [
        'revenue',
        'operating_cost',
        'oee',
        'fpy',
        'capacity_gap_pct',
        'on_time_delivery',
        'shortage_hours',
        'technology_downtime_min',
    ]:
        if metric in enterprise_mart.columns and pd.notna(latest[metric]):
            rows.append({
                'scope': 'kpi',
                'entity': 'enterprise_latest',
                'metric': metric,
                'value': float(latest[metric]),
            })

    return pd.DataFrame(rows)


def compare_drift(current: pd.DataFrame, baseline: pd.DataFrame | None) -> pd.DataFrame:
    if baseline is None or baseline.empty:
        out = current.copy()
        out['baseline_value'] = np.nan
        out['absolute_change'] = np.nan
        out['relative_change'] = np.nan
        out['threshold'] = np.nan
        out['status'] = 'BASELINE_INITIALIZED'
        return out

    merged = current.merge(
        baseline[['scope', 'entity', 'metric', 'value']].rename(columns={'value': 'baseline_value'}),
        on=['scope', 'entity', 'metric'],
        how='outer',
        indicator=True,
    )
    rows = []
    for row in merged.itertuples(index=False):
        value = getattr(row, 'value')
        baseline_value = getattr(row, 'baseline_value')
        merge_status = getattr(row, '_4') if hasattr(row, '_4') else None

        if pd.isna(value) or pd.isna(baseline_value):
            rows.append({
                'scope': row.scope,
                'entity': row.entity,
                'metric': row.metric,
                'value': value,
                'baseline_value': baseline_value,
                'absolute_change': np.nan,
                'relative_change': np.nan,
                'threshold': np.nan,
                'status': 'ALERT_PROFILE_SHAPE_CHANGED',
            })
            continue

        absolute_change = float(value - baseline_value)
        relative_change = (
            abs(absolute_change) / abs(float(baseline_value))
            if float(baseline_value) != 0
            else (0.0 if float(value) == 0 else np.inf)
        )

        if row.metric == 'schema_signature_numeric':
            threshold = 0.0
            status = 'PASS' if float(value) == float(baseline_value) else 'ALERT_SCHEMA_CHANGED'
        elif row.metric == 'category_set_signature_numeric':
            threshold = 0.0
            status = 'PASS' if float(value) == float(baseline_value) else 'ALERT_CATEGORY_DRIFT'
        elif row.metric == 'category_count':
            threshold = 0.0
            status = 'PASS' if float(value) == float(baseline_value) else 'ALERT_CATEGORY_DRIFT'
        elif row.metric == 'row_count':
            threshold = DRIFT_THRESHOLDS['row_count_relative_change']
            status = 'PASS' if relative_change <= threshold else 'ALERT_ROW_COUNT_DRIFT'
        elif row.metric == 'null_rate':
            threshold = DRIFT_THRESHOLDS['null_rate_absolute_change']
            status = 'PASS' if abs(absolute_change) <= threshold else 'ALERT_MISSINGNESS_DRIFT'
        elif row.scope == 'model' and row.metric == 'positive_rate':
            threshold = DRIFT_THRESHOLDS['model_positive_rate_absolute_change']
            status = 'PASS' if abs(absolute_change) <= threshold else 'ALERT_MODEL_TARGET_DRIFT'
        elif row.scope == 'kpi':
            threshold = DRIFT_THRESHOLDS['kpi_relative_change']
            status = 'PASS' if relative_change <= threshold else 'ALERT_KPI_DRIFT'
        else:
            threshold = np.nan
            status = 'PASS'

        rows.append({
            'scope': row.scope,
            'entity': row.entity,
            'metric': row.metric,
            'value': float(value),
            'baseline_value': float(baseline_value),
            'absolute_change': absolute_change,
            'relative_change': float(relative_change),
            'threshold': threshold,
            'status': status,
        })

    return pd.DataFrame(rows)


def run_persistent_drift_monitor(
    table_quality: pd.DataFrame,
    model_profile: pd.DataFrame,
    enterprise_mart: pd.DataFrame,
    baseline_path: Path,
    frames: dict[str, pd.DataFrame] | None = None,
):
    current = build_drift_profile(table_quality, model_profile, enterprise_mart, frames=frames)
    baseline = None
    if baseline_path.exists():
        baseline = pd.read_csv(baseline_path)

    comparison = compare_drift(current, baseline)

    baseline_path.parent.mkdir(parents=True, exist_ok=True)
    current.to_csv(baseline_path, index=False)

    alert_mask = comparison['status'].astype(str).str.startswith('ALERT_')
    summary = {
        'baseline_path': str(baseline_path),
        'baseline_previously_available': baseline is not None,
        'profile_rows': int(len(current)),
        'alert_count': int(alert_mask.sum()),
        'statuses': comparison['status'].value_counts().to_dict(),
        'thresholds': DRIFT_THRESHOLDS,
        'behavior': (
            'Persistent runtime baseline survives --clean because artifacts/runtime is not deleted. '
            'A fresh environment initializes a baseline; later runs compare against the previous profile.'
        ),
    }
    return current, comparison, summary
