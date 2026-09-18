from pathlib import Path
import re

import pandas as pd
import pytest

from mednexus.analytics import monthly_enterprise_mart
from mednexus.risk import run_mori_validation
from mednexus.semantic_model import (
    DISCONNECTED_TABLES,
    EXPECTED_EXPORTS,
    build_headline_reconciliation_targets,
    build_relationship_contract,
    build_table_role_contract,
    validate_semantic_model_contract,
)
from mednexus.synthetic import generate


@pytest.fixture(scope='module')
def exports():
    frames = generate(seed=42)
    mart = monthly_enterprise_mart(frames).copy()
    mart['month_date'] = pd.to_datetime(mart['month'].astype(str).str.slice(0, 7) + '-01')

    mori = run_mori_validation(
        mart,
        {
            'quality': 0.16,
            'equipment': 0.16,
            'downtime': 0.12,
            'capacity': 0.12,
            'supply': 0.12,
            'logistics': 0.10,
            'workforce': 0.10,
            'technology': 0.12,
        },
    )['mori'].copy()
    mori['month_date'] = pd.to_datetime(mori['month'].astype(str).str.slice(0, 7) + '-01')

    all_dates = []
    for frame in frames.values():
        for column in ['date', 'month', 'order_date', 'ship_date', 'promised_date', 'actual_delivery_date']:
            if column in frame.columns:
                parsed = pd.to_datetime(frame[column], errors='coerce').dropna()
                if not parsed.empty:
                    all_dates.extend([parsed.min(), parsed.max()])
    future_months = pd.date_range(
        pd.to_datetime(mart['month_date']).max() + pd.offsets.MonthBegin(1),
        periods=3,
        freq='MS',
    )
    all_dates.extend([future_months.min(), future_months.max()])
    dim_date = pd.DataFrame({
        'date': pd.date_range(min(all_dates).normalize(), max(all_dates).normalize(), freq='D')
    })

    monthly = mart[['month_date']].rename(columns={'month_date': 'month'}).copy()

    result = {
        'DimDate': dim_date,
        'DimPlant': frames['dim_plant'],
        'DimLine': frames['dim_line'],
        'DimMachine': frames['dim_machine'],
        'DimProduct': frames['dim_product'],
        'DimSupplier': frames['dim_supplier'],
        'DimCustomer': frames['dim_customer'],
        'DimEmployee': frames['dim_employee'],
        'EnterpriseMonthly': mart,
        'ProductionKPI': frames['fact_production'],
        'Downtime': frames['fact_downtime'],
        'QualityEvents': frames['fact_quality'],
        'Maintenance': frames['fact_maintenance'],
        'MORI': mori,
        'QualityPChart': frames['fact_production'][['date', 'plant_id']].copy(),
        'SixBigLosses': mart[['month_date']].copy(),
        'CapacityWaterfall': mart[['month_date']].copy(),
        'ValueLeakage': mart[['month_date']].copy(),
        'Reliability': frames['dim_machine'][['machine_id']].copy(),
        'PredictiveMaintenanceScores': frames['fact_sensor'][['date', 'machine_id']].copy(),
        'DemandForecast': pd.DataFrame({'month': future_months}),
        'Finance': frames['fact_finance'],
        'Workforce': frames['fact_workforce'],
        'Recruitment': frames['fact_recruitment'],
        'Supply': frames['fact_supply'],
        'Orders': frames['fact_orders'],
        'Shipments': frames['fact_shipment'],
        'CustomerService': frames['fact_customer_service'],
        'TechnologyIncidents': frames['fact_technology_incident'],
        'SaaSUsage': frames['fact_saas_usage'],
    }

    for table in DISCONNECTED_TABLES:
        result.setdefault(table, pd.DataFrame())

    return result


def test_export_contract_matches_powerbi_prep_script():
    script = Path('scripts/phase2_powerbi_prep.ps1').read_text(encoding='utf-8')
    names = {
        match[:-4]
        for match in re.findall(r'"([A-Za-z0-9]+\.csv)"', script)
    }
    assert names == set(EXPECTED_EXPORTS)


def test_operations_hierarchy_has_no_parallel_fact_paths():
    rel = build_relationship_contract()
    active = rel[rel['active']]
    assert not (
        (active['one_table'] == 'DimPlant')
        & (active['many_table'] == 'ProductionKPI')
    ).any()
    assert not (
        (active['one_table'] == 'DimLine')
        & (active['many_table'] == 'ProductionKPI')
    ).any()

    expected_edges = {
        ('DimPlant', 'DimLine'),
        ('DimLine', 'DimMachine'),
        ('DimMachine', 'ProductionKPI'),
    }
    observed = set(zip(active['one_table'], active['many_table']))
    assert expected_edges.issubset(observed)


def test_relationship_contract_is_one_to_many_single_direction():
    rel = build_relationship_contract()
    assert rel['cardinality'].eq('1:*').all()
    assert rel['cross_filter_direction'].eq('single').all()
    assert int((~rel['active']).sum()) == 2
    inactive = rel.loc[~rel['active'], 'many_column'].tolist()
    assert sorted(inactive) == ['actual_delivery_date', 'promised_date']


def test_disconnected_tables_have_no_relationships():
    rel = build_relationship_contract()
    disconnected = set(DISCONNECTED_TABLES)
    assert not rel['one_table'].isin(disconnected).any()
    assert not rel['many_table'].isin(disconnected).any()

    roles = build_table_role_contract().set_index('table')
    for table in disconnected:
        assert roles.loc[table, 'model_status'] == 'DISCONNECTED'


def test_semantic_model_fixture_passes_integrity_and_ambiguity_audit(exports):
    issues, summary = validate_semantic_model_contract(exports)
    assert summary['status'] == 'PASS'
    assert summary['issue_count'] == 0
    assert issues.empty
    assert summary['actual_export_count'] == summary['expected_export_count']


def test_saas_usage_has_controlled_date_relationship():
    rel = build_relationship_contract()
    match = rel[
        (rel['one_table'] == 'DimDate')
        & (rel['many_table'] == 'SaaSUsage')
        & (rel['many_column'] == 'date')
        & (rel['active'])
    ]
    assert len(match) == 1


def test_headline_reconciliation_targets_cover_executive_measures(exports):
    targets = build_headline_reconciliation_targets(exports)
    measures = set(targets['measure'])
    required = {
        'Latest Revenue',
        'Latest Operating Cost',
        'Latest Operating Margin Proxy',
        'Latest OEE',
        'Latest OLI',
        'Latest FPY',
        'Latest Defect Rate',
        'Latest On-Time Delivery',
        'Latest Capacity Gap %',
        'Latest Supplier Reliability',
        'Latest Technology Downtime Minutes',
        'Latest MORI',
        'Latest MORI Band',
    }
    assert required.issubset(measures)
    assert targets['pbix_status'].eq(
        'TO_BE_RECONCILED_AFTER_USER_BUILDS_REPORT'
    ).all()


def test_headline_targets_use_single_latest_enterprise_month(exports):
    targets = build_headline_reconciliation_targets(exports)
    assert targets['latest_month'].nunique() == 1
    expected = pd.to_datetime(exports['EnterpriseMonthly']['month_date']).max().date().isoformat()
    assert targets['latest_month'].iloc[0] == expected
