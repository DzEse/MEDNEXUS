from __future__ import annotations

from collections import defaultdict

import numpy as np
import pandas as pd


CONNECTED_TABLES = {
    'DimDate': 'dimension',
    'DimPlant': 'dimension',
    'DimLine': 'dimension',
    'DimMachine': 'dimension',
    'DimProduct': 'dimension',
    'DimSupplier': 'dimension',
    'DimCustomer': 'dimension',
    'DimEmployee': 'dimension',
    'DimWarehouse': 'dimension',
    'DimShift': 'dimension',
    'DimDepartment': 'dimension',
    'DimJobRole': 'dimension',
    'EnterpriseMonthly': 'enterprise_mart',
    'ProductionKPI': 'fact',
    'Downtime': 'fact',
    'QualityEvents': 'fact',
    'Maintenance': 'fact',
    'MORI': 'risk_mart',
    'QualityPChart': 'statistical_mart',
    'SixBigLosses': 'analytical_mart',
    'CapacityWaterfall': 'analytical_mart',
    'ValueLeakage': 'analytical_mart',
    'Reliability': 'analytical_mart',
    'PredictiveMaintenanceScores': 'model_output',
    'DemandForecast': 'forecast_output',
    'Finance': 'fact',
    'Workforce': 'fact',
    'Recruitment': 'fact',
    'Supply': 'fact',
    'Orders': 'fact',
    'Shipments': 'fact',
    'CustomerService': 'fact',
    'TechnologyIncidents': 'fact',
    'SaaSUsage': 'fact',
    'EmployeeAssignment': 'workforce_snapshot_fact',
}

DISCONNECTED_TABLES = {
    'MORIComponentContributions': 'risk_evidence',
    'MORIWeightSensitivity': 'risk_evidence',
    'MORIThresholdSensitivity': 'risk_evidence',
    'ScenarioOutputs': 'simulated_scenario',
    'ScenarioAssumptions': 'simulated_scenario_evidence',
    'ScenarioMonitoringPlan': 'prospective_monitoring',
    'ProcessEventLog': 'case_process_evidence',
    'ProcessCases': 'case_process_evidence',
    'ProcessTransitions': 'case_process_evidence',
    'DecisionQueue': 'presentation_mart',
    'QualityPareto': 'presentation_mart',
    'PredictiveMaintenanceModelComparison': 'model_validation',
    'PredictiveMaintenanceCalibration': 'model_validation',
    'PredictiveMaintenanceFeatureImportance': 'model_validation',
    'RootCauseSegments': 'diagnostic_evidence',
    'RootCauseAssociations': 'diagnostic_evidence',
    'RootCauseGroupTests': 'diagnostic_evidence',
    'RootCauseRegression': 'diagnostic_evidence',
    'RootCauseTreeImportance': 'diagnostic_evidence',
    'RootCausePriorities': 'diagnostic_evidence',
    'DemandForecastBacktest': 'forecast_validation',
    'DemandForecastModelComparison': 'forecast_validation',
    'DemandForecastDiagnostics': 'forecast_validation',
}

EXPECTED_EXPORTS = tuple(sorted(set(CONNECTED_TABLES) | set(DISCONNECTED_TABLES)))


def _rel(
    one_table: str,
    one_column: str,
    many_table: str,
    many_column: str,
    *,
    active: bool = True,
    relationship_class: str = 'canonical_active',
    rationale: str = '',
):
    return {
        'one_table': one_table,
        'one_column': one_column,
        'many_table': many_table,
        'many_column': many_column,
        'cardinality': '1:*',
        'cross_filter_direction': 'single',
        'active': bool(active),
        'relationship_class': relationship_class,
        'rationale': rationale,
    }


def build_relationship_contract() -> pd.DataFrame:
    relationships = [
        # Controlled operations hierarchy.
        _rel('DimPlant', 'plant_id', 'DimLine', 'plant_id',
             rationale='Plant filters line; no parallel direct plant path into machine-grain facts.'),
        _rel('DimLine', 'line_id', 'DimMachine', 'line_id',
             rationale='Line filters machine; machine becomes the operational fact filter key.'),

        # Date relationships.
        _rel('DimDate', 'date', 'EnterpriseMonthly', 'month_date'),
        _rel('DimDate', 'date', 'MORI', 'month_date'),
        _rel('DimDate', 'date', 'ProductionKPI', 'date'),
        _rel('DimDate', 'date', 'Downtime', 'date'),
        _rel('DimDate', 'date', 'QualityEvents', 'date'),
        _rel('DimDate', 'date', 'Maintenance', 'date'),
        _rel('DimDate', 'date', 'PredictiveMaintenanceScores', 'date'),
        _rel('DimDate', 'date', 'Workforce', 'month'),
        _rel('DimDate', 'date', 'Recruitment', 'month'),
        _rel('DimDate', 'date', 'Supply', 'month'),
        _rel('DimDate', 'date', 'Finance', 'month'),
        _rel('DimDate', 'date', 'DemandForecast', 'month'),
        _rel('DimDate', 'date', 'Orders', 'order_date'),
        _rel('DimDate', 'date', 'Shipments', 'ship_date'),
        _rel('DimDate', 'date', 'CustomerService', 'date'),
        _rel('DimDate', 'date', 'TechnologyIncidents', 'date'),
        _rel('DimDate', 'date', 'SaaSUsage', 'date'),
        _rel('DimDate', 'date', 'QualityPChart', 'date'),
        _rel('DimDate', 'date', 'SixBigLosses', 'month_date'),
        _rel('DimDate', 'date', 'CapacityWaterfall', 'month_date'),
        _rel('DimDate', 'date', 'ValueLeakage', 'month_date'),

        # Machine-grain operational facts use only DimMachine for the hierarchy path.
        _rel('DimMachine', 'machine_id', 'ProductionKPI', 'machine_id',
             rationale='Avoid direct active Plant/Line relationships to ProductionKPI.'),
        _rel('DimMachine', 'machine_id', 'Downtime', 'machine_id'),
        _rel('DimMachine', 'machine_id', 'QualityEvents', 'machine_id'),
        _rel('DimMachine', 'machine_id', 'Maintenance', 'machine_id'),
        _rel('DimMachine', 'machine_id', 'Reliability', 'machine_id'),
        _rel('DimMachine', 'machine_id', 'PredictiveMaintenanceScores', 'machine_id'),

        # Product / supplier / customer.
        _rel('DimProduct', 'product_id', 'ProductionKPI', 'product_id'),
        _rel('DimProduct', 'product_id', 'QualityEvents', 'product_id'),
        _rel('DimProduct', 'product_id', 'Orders', 'product_id'),
        _rel('DimSupplier', 'supplier_id', 'Supply', 'supplier_id'),
        _rel('DimCustomer', 'customer_id', 'Orders', 'customer_id'),
        _rel('DimCustomer', 'customer_id', 'Shipments', 'customer_id'),
        _rel('DimCustomer', 'customer_id', 'CustomerService', 'customer_id'),

        # Plant-grain facts/marts.
        _rel('DimPlant', 'plant_id', 'Workforce', 'plant_id'),
        _rel('DimPlant', 'plant_id', 'Recruitment', 'plant_id'),
        _rel('DimPlant', 'plant_id', 'QualityPChart', 'plant_id'),

        # Phase 12G approved workforce / warehouse promotion.
        _rel('DimPlant', 'plant_id', 'DimWarehouse', 'plant_id',
             rationale='Plant filters warehouse; geography remains role-specific attributes rather than a shared Region dimension.'),
        _rel('DimPlant', 'plant_id', 'EmployeeAssignment', 'plant_id',
             rationale='Current assignment snapshot uses one direct Plant path; no active Line relationship is admitted.'),
        _rel('DimShift', 'shift_id', 'EmployeeAssignment', 'shift_id',
             rationale='Shift filters the current assignment snapshot only; true shift production remains gated.'),
        _rel('DimEmployee', 'employee_id', 'EmployeeAssignment', 'employee_id',
             rationale='One current assignment per synthetic employee.'),
        _rel('DimDepartment', 'department_id', 'DimJobRole', 'department_id',
             rationale='Department filters Job Role as the only department route into EmployeeAssignment.'),
        _rel('DimJobRole', 'job_role_id', 'EmployeeAssignment', 'job_role_id',
             rationale='Job Role filters EmployeeAssignment; no direct Department→EmployeeAssignment relationship is active.'),

        # Optional inactive date roles on Shipments.
        _rel(
            'DimDate', 'date', 'Shipments', 'promised_date',
            active=False,
            relationship_class='optional_inactive_date_role',
            rationale='Activate only through USERELATIONSHIP in a measure that explicitly needs promised date.',
        ),
        _rel(
            'DimDate', 'date', 'Shipments', 'actual_delivery_date',
            active=False,
            relationship_class='optional_inactive_date_role',
            rationale='Activate only through USERELATIONSHIP in a measure that explicitly needs actual delivery date.',
        ),
    ]
    return pd.DataFrame(relationships)


def build_table_role_contract() -> pd.DataFrame:
    rows = []
    for table, role in CONNECTED_TABLES.items():
        rows.append({
            'table': table,
            'model_status': 'CONNECTED',
            'role': role,
            'filtering_rule': 'Only relationships in powerbi_semantic_relationships.csv are permitted.',
        })
    for table, role in DISCONNECTED_TABLES.items():
        rows.append({
            'table': table,
            'model_status': 'DISCONNECTED',
            'role': role,
            'filtering_rule': 'Must not filter operational facts; use only on dedicated evidence/presentation surfaces.',
        })
    return pd.DataFrame(rows).sort_values('table').reset_index(drop=True)


def _active_adjacency(relationships: pd.DataFrame):
    adjacency = defaultdict(list)
    for row in relationships.loc[relationships['active']].itertuples(index=False):
        adjacency[row.one_table].append(row.many_table)
    return adjacency


def _count_paths(adjacency, source: str, target: str, visited=None) -> int:
    if source == target:
        return 1
    visited = set() if visited is None else set(visited)
    if source in visited:
        return 0
    visited.add(source)
    total = 0
    for nxt in adjacency.get(source, []):
        total += _count_paths(adjacency, nxt, target, visited)
        if total > 1:
            return total
    return total


def validate_semantic_model_contract(exports: dict[str, pd.DataFrame]) -> tuple[pd.DataFrame, dict]:
    rel = build_relationship_contract()
    roles = build_table_role_contract()
    issues = []

    missing_exports = sorted(set(EXPECTED_EXPORTS).difference(exports))
    unexpected_exports = sorted(set(exports).difference(EXPECTED_EXPORTS))
    if missing_exports:
        issues.append(('missing_exports', '|'.join(missing_exports)))
    if unexpected_exports:
        issues.append(('unexpected_exports', '|'.join(unexpected_exports)))

    if not rel['cardinality'].eq('1:*').all():
        issues.append(('cardinality', 'Only 1:* relationships are permitted.'))
    if not rel['cross_filter_direction'].eq('single').all():
        issues.append(('cross_filter', 'Only single-direction relationships are permitted.'))

    disconnected = set(DISCONNECTED_TABLES)
    touching_disconnected = rel[
        rel['one_table'].isin(disconnected) | rel['many_table'].isin(disconnected)
    ]
    if not touching_disconnected.empty:
        issues.append(('disconnected_table_relationship', '|'.join(touching_disconnected['many_table'].astype(str))))

    for row in rel.itertuples(index=False):
        if row.one_table not in exports or row.many_table not in exports:
            continue
        one = exports[row.one_table]
        many = exports[row.many_table]
        if row.one_column not in one.columns:
            issues.append(('missing_one_column', f'{row.one_table}[{row.one_column}]'))
            continue
        if row.many_column not in many.columns:
            issues.append(('missing_many_column', f'{row.many_table}[{row.many_column}]'))
            continue

        one_key = one[row.one_column]
        if one_key.isna().any():
            issues.append(('one_side_null', f'{row.one_table}[{row.one_column}]'))
        if one_key.duplicated().any():
            issues.append(('one_side_duplicate', f'{row.one_table}[{row.one_column}]'))

        many_nonnull = many[row.many_column].dropna()
        if not many_nonnull.empty:
            if row.one_table == 'DimDate':
                one_values = set(pd.to_datetime(one_key).dt.normalize())
                many_values = set(pd.to_datetime(many_nonnull).dt.normalize())
            else:
                one_values = set(one_key.astype(str))
                many_values = set(many_nonnull.astype(str))
            orphan_values = many_values.difference(one_values)
            if orphan_values:
                issues.append((
                    'relationship_orphan',
                    f'{row.one_table}[{row.one_column}]→{row.many_table}[{row.many_column}] missing {len(orphan_values)} key values',
                ))

    active = rel.loc[rel['active']].copy()
    adjacency = _active_adjacency(rel)
    source_dimensions = ['DimDate', 'DimPlant', 'DimLine', 'DimMachine', 'DimProduct', 'DimSupplier', 'DimCustomer', 'DimEmployee', 'DimWarehouse', 'DimShift', 'DimDepartment', 'DimJobRole']
    targets = sorted(set(active['many_table']))
    for source in source_dimensions:
        for target in targets:
            if source == target:
                continue
            paths = _count_paths(adjacency, source, target)
            if paths > 1:
                issues.append(('ambiguous_active_paths', f'{source}→{target} has {paths} active paths'))

    issue_df = pd.DataFrame(issues, columns=['issue_type', 'detail'])
    summary = {
        'status': 'PASS' if issue_df.empty else 'FAIL',
        'expected_export_count': len(EXPECTED_EXPORTS),
        'actual_export_count': len(exports),
        'active_relationship_count': int(active.shape[0]),
        'inactive_relationship_count': int((~rel['active']).sum()),
        'disconnected_table_count': len(DISCONNECTED_TABLES),
        'issue_count': int(len(issue_df)),
        'model_rules': {
            'cardinality': '1:* only',
            'cross_filter': 'single direction only',
            'fact_to_fact': 'prohibited',
            'many_to_many': 'prohibited unless future documented bridge exists',
            'operations_hierarchy': 'DimPlant→DimLine→DimMachine→machine-grain facts',
            'workforce_hierarchy': 'DimDepartment→DimJobRole→EmployeeAssignment plus independent DimPlant/DimShift/DimEmployee filters',
            'geography': 'role-specific simulated geography attributes; no shared active DimRegion',
            'date_roles': 'one active date role per fact; optional alternate shipment dates inactive',
        },
    }
    return issue_df, summary


def build_headline_reconciliation_targets(exports: dict[str, pd.DataFrame]) -> pd.DataFrame:
    enterprise = exports['EnterpriseMonthly'].copy()
    enterprise['month_date'] = pd.to_datetime(enterprise['month_date'])
    latest_month = enterprise['month_date'].max()
    row = enterprise.loc[enterprise['month_date'] == latest_month].iloc[0]

    mori = exports['MORI'].copy()
    mori['month_date'] = pd.to_datetime(mori['month_date'])
    mori_row = mori.loc[mori['month_date'] == latest_month].iloc[0]

    specs = [
        ('Latest Revenue', 'EnterpriseMonthly', 'revenue', float(row['revenue']), 'SUM at latest visible month'),
        ('Latest Operating Cost', 'EnterpriseMonthly', 'operating_cost', float(row['operating_cost']), 'SUM at latest visible month'),
        ('Latest Operating Margin Proxy', 'EnterpriseMonthly', 'revenue-operating_cost', float(row['revenue'] - row['operating_cost']), 'Revenue minus Operating Cost'),
        ('Latest OEE', 'EnterpriseMonthly', 'oee', float(row['oee']), 'single monthly value / AVERAGE'),
        ('Latest OLI', 'EnterpriseMonthly', 'oli', float(row['oli']), 'single monthly value / AVERAGE'),
        ('Latest FPY', 'EnterpriseMonthly', 'fpy', float(row['fpy']), 'single monthly value / AVERAGE'),
        ('Latest Total Units', 'EnterpriseMonthly', 'total_units', float(row['total_units']), 'SUM at latest visible month'),
        ('Latest Good Units', 'EnterpriseMonthly', 'good_units', float(row['good_units']), 'SUM at latest visible month'),
        ('Latest Defect Units', 'EnterpriseMonthly', 'defect_units', float(row['defect_units']), 'SUM at latest visible month'),
        ('Latest Defect Rate', 'EnterpriseMonthly', 'defect_units/total_units', float(row['defect_units'] / row['total_units']), 'ratio of latest defect units to total units'),
        ('Latest On-Time Delivery', 'EnterpriseMonthly', 'on_time_delivery', float(row['on_time_delivery']), 'single monthly value / AVERAGE'),
        ('Latest Capacity Gap %', 'EnterpriseMonthly', 'capacity_gap_pct', float(row['capacity_gap_pct']), 'single monthly value / AVERAGE'),
        ('Latest Vacancies', 'EnterpriseMonthly', 'vacancies', float(row['vacancies']), 'SUM at latest visible month'),
        ('Latest Supplier Reliability', 'EnterpriseMonthly', 'supplier_reliability', float(row['supplier_reliability']), 'single monthly value / AVERAGE'),
        ('Latest Shortage Hours', 'EnterpriseMonthly', 'shortage_hours', float(row['shortage_hours']), 'SUM at latest visible month'),
        ('Latest Technology Downtime Minutes', 'EnterpriseMonthly', 'technology_downtime_min', float(row['technology_downtime_min']), 'SUM at latest visible month'),
        ('Latest Major Technology Incidents', 'EnterpriseMonthly', 'major_incidents', float(row['major_incidents']), 'SUM at latest visible month'),
        ('Latest MORI', 'MORI', 'mori_score', float(mori_row['mori_score']), 'MAX at latest visible month'),
    ]

    result = pd.DataFrame(
        specs,
        columns=['measure', 'source_table', 'source_field_or_formula', 'expected_numeric_value', 'reconciliation_rule'],
    )
    result['latest_month'] = latest_month.date().isoformat()
    result['pbix_status'] = 'TO_BE_RECONCILED_AFTER_USER_BUILDS_REPORT'
    result['tolerance'] = np.where(
        result['measure'].str.contains('%|OEE|OLI|FPY|Delivery|Reliability|Rate', regex=True),
        1e-9,
        0.01,
    )

    band_row = pd.DataFrame([{
        'measure': 'Latest MORI Band',
        'source_table': 'MORI',
        'source_field_or_formula': 'mori_band',
        'expected_numeric_value': np.nan,
        'reconciliation_rule': f"Expected text: {mori_row['mori_band']}",
        'latest_month': latest_month.date().isoformat(),
        'pbix_status': 'TO_BE_RECONCILED_AFTER_USER_BUILDS_REPORT',
        'tolerance': np.nan,
    }])
    return pd.concat([result, band_row], ignore_index=True)
