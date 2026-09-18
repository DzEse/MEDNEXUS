import sqlite3

import pandas as pd
import pytest

from mednexus.analytics import monthly_enterprise_mart
from mednexus.architecture_governance import (
    build_analysis_design_checklist,
    build_drift_profile,
    build_operations_twin_catalog,
    build_output_lineage_registry,
    compare_drift,
    run_persistent_drift_monitor,
)
from mednexus.database import execute_sql_file, load_frames
from mednexus.quality import evaluate, model_input_profile
from mednexus.synthetic import generate


@pytest.fixture(scope='module')
def canonical():
    frames = generate(seed=42)
    table_q, _ = evaluate(frames)
    model_profile = model_input_profile(frames)
    mart = monthly_enterprise_mart(frames)
    return frames, table_q, model_profile, mart


def test_enterprise_operations_twin_is_conceptual_and_cross_domain():
    twin = build_operations_twin_catalog()
    assert not twin.empty
    assert twin['twin_type'].eq('CONCEPTUAL_ENTERPRISE_OPERATIONS_TWIN').all()
    assert twin['three_dimensional_model'].eq(False).all()
    edges = set(zip(twin['source_entity'], twin['target_entity']))
    assert ('Plant', 'Line') in edges
    assert ('Line', 'Machine') in edges
    assert ('Order', 'Shipment') in edges
    assert ('Enterprise Monthly Mart', 'MORI') in edges


def test_output_lineage_registry_reaches_bi_and_decision():
    lineage = build_output_lineage_registry()
    required = {
        'ProductionKPI',
        'PredictiveMaintenanceScores',
        'DemandForecast',
        'MORI',
        'ScenarioOutputs',
        'DecisionQueue',
        'ProcessTransitions',
        'DataTrust',
    }
    assert required.issubset(set(lineage['output']))
    assert lineage['source'].str.len().gt(0).all()
    assert lineage['transformation'].str.len().gt(0).all()
    assert lineage['bi_surface'].str.len().gt(0).all()
    assert lineage['decision_supported'].str.len().gt(0).all()


def test_analysis_design_checklist_enforces_all_required_questions():
    checklist = build_analysis_design_checklist()
    assert len(checklist) == 10
    assert checklist['mandatory'].eq(True).all()
    assert checklist['gate_status'].eq('REQUIRED_FOR_NEW_MAJOR_ANALYSIS').all()
    assert {
        'business_question',
        'unit_and_grain',
        'assumptions',
        'bias_and_leakage',
        'proof_boundary',
        'validation',
        'monitoring',
    }.issubset(set(checklist['check_id']))


def test_drift_profile_is_stable_against_itself(canonical):
    _, table_q, model_profile, mart = canonical
    profile = build_drift_profile(table_q, model_profile, mart, frames=canonical[0])
    comparison = compare_drift(profile, profile.copy())
    assert comparison['status'].eq('PASS').all()


def test_row_count_drift_alerts_on_material_change(canonical):
    _, table_q, model_profile, mart = canonical
    baseline = build_drift_profile(table_q, model_profile, mart, frames=canonical[0])
    current = baseline.copy()
    mask = (
        (current['scope'] == 'table')
        & (current['entity'] == 'fact_production')
        & (current['metric'] == 'row_count')
    )
    current.loc[mask, 'value'] = current.loc[mask, 'value'] * 1.25
    comparison = compare_drift(current, baseline)
    status = comparison.loc[
        (comparison['scope'] == 'table')
        & (comparison['entity'] == 'fact_production')
        & (comparison['metric'] == 'row_count'),
        'status',
    ].iloc[0]
    assert status == 'ALERT_ROW_COUNT_DRIFT'




def test_category_drift_alerts_on_changed_domain(canonical):
    frames, table_q, model_profile, mart = canonical
    baseline = build_drift_profile(table_q, model_profile, mart, frames=frames)
    current = baseline.copy()
    mask = (
        (current['scope'] == 'category')
        & (current['entity'] == 'fact_quality.defect_category')
        & (current['metric'] == 'category_set_signature_numeric')
    )
    assert mask.any()
    current.loc[mask, 'value'] = current.loc[mask, 'value'] + 1
    comparison = compare_drift(current, baseline)
    status = comparison.loc[
        (comparison['scope'] == 'category')
        & (comparison['entity'] == 'fact_quality.defect_category')
        & (comparison['metric'] == 'category_set_signature_numeric'),
        'status',
    ].iloc[0]
    assert status == 'ALERT_CATEGORY_DRIFT'


def test_persistent_runtime_baseline_survives_between_runs(canonical, tmp_path):
    _, table_q, model_profile, mart = canonical
    baseline_path = tmp_path / 'runtime' / 'observability_baseline.csv'

    _, first, first_summary = run_persistent_drift_monitor(
        table_q, model_profile, mart, baseline_path, frames=canonical[0]
    )
    assert baseline_path.exists()
    assert first_summary['baseline_previously_available'] is False
    assert first['status'].eq('BASELINE_INITIALIZED').all()

    _, second, second_summary = run_persistent_drift_monitor(
        table_q, model_profile, mart, baseline_path, frames=canonical[0]
    )
    assert second_summary['baseline_previously_available'] is True
    assert second_summary['alert_count'] == 0
    assert second['status'].eq('PASS').all()


def test_layered_sql_views_preserve_expected_grains(canonical):
    frames, _, _, mart = canonical
    con = sqlite3.connect(':memory:')
    try:
        load_frames(con, frames)
        mart.to_sql('mart_enterprise_monthly', con, if_exists='replace', index=False)
        execute_sql_file(con, 'sql/layered_architecture.sql')

        order = pd.read_sql_query('SELECT * FROM val_order_fulfillment_grain', con).iloc[0]
        machine = pd.read_sql_query('SELECT * FROM val_machine_hierarchy_grain', con).iloc[0]

        assert int(order['duplicate_order_rows']) == 0
        assert int(order['row_count']) == len(frames['fact_orders'])
        assert int(machine['duplicate_machine_rows']) == 0
        assert int(machine['row_count']) == len(frames['dim_machine'])
    finally:
        con.close()


def test_layered_sql_contains_staging_dimension_fact_kpi_and_validation_views(canonical):
    frames, _, _, mart = canonical
    con = sqlite3.connect(':memory:')
    try:
        load_frames(con, frames)
        mart.to_sql('mart_enterprise_monthly', con, if_exists='replace', index=False)
        execute_sql_file(con, 'sql/layered_architecture.sql')
        views = set(
            pd.read_sql_query(
                "SELECT name FROM sqlite_master WHERE type='view'",
                con,
            )['name']
        )
        assert {
            'stg_production_validated',
            'dim_machine_hierarchy',
            'fact_order_fulfillment_enriched',
            'kpi_monthly_operations',
            'val_order_fulfillment_grain',
            'val_machine_hierarchy_grain',
        }.issubset(views)
    finally:
        con.close()
