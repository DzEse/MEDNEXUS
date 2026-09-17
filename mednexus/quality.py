from __future__ import annotations

import hashlib
from typing import Iterable

import numpy as np
import pandas as pd


PRIMARY_KEYS = {
    'dim_plant': 'plant_id',
    'dim_line': 'line_id',
    'dim_machine': 'machine_id',
    'dim_product': 'product_id',
    'dim_supplier': 'supplier_id',
    'dim_customer': 'customer_id',
    'dim_employee': 'employee_id',
    'fact_production': 'production_order_id',
    'fact_downtime': 'downtime_event_id',
    'fact_quality': 'quality_event_id',
    'fact_maintenance': 'maintenance_event_id',
    'fact_orders': 'order_id',
    'fact_shipment': 'shipment_id',
    'fact_customer_service': 'service_event_id',
}

REQUIRED_COLUMNS = {
    'dim_plant': {'plant_id', 'plant_name', 'region'},
    'dim_line': {'line_id', 'plant_id', 'line_name'},
    'dim_machine': {'machine_id', 'line_id', 'plant_id', 'machine_name', 'machine_age_years'},
    'dim_product': {'product_id', 'product_family', 'unit_price', 'ideal_cycle_min', 'material_cost_per_unit'},
    'dim_supplier': {'supplier_id', 'supplier_name', 'base_lead_time_days', 'quality_rating'},
    'dim_customer': {'customer_id', 'customer_type', 'region'},
    'dim_employee': {'employee_id', 'department', 'plant_id', 'skill_level', 'hourly_cost', 'active_flag'},
    'fact_workforce': {'month', 'plant_id', 'required_headcount', 'actual_headcount', 'vacancies', 'absence_rate', 'overtime_hours_per_employee', 'capacity_gap_pct', 'labor_cost'},
    'fact_recruitment': {'month', 'plant_id', 'open_positions', 'applicants', 'screened', 'interviews', 'offers', 'accepted', 'avg_time_to_fill_days', 'cost_per_hire'},
    'fact_production': {'production_order_id', 'date', 'plant_id', 'line_id', 'machine_id', 'product_id', 'planned_production_min', 'planned_downtime_min', 'unplanned_downtime_min', 'run_time_min', 'total_count', 'good_count', 'defect_units', 'rework_units', 'scrap_units', 'ideal_cycle_min'},
    'fact_downtime': {'downtime_event_id', 'date', 'machine_id', 'line_id', 'plant_id', 'downtime_reason', 'duration_min'},
    'fact_quality': {'quality_event_id', 'date', 'machine_id', 'line_id', 'plant_id', 'product_id', 'defect_category', 'severity', 'defect_units', 'rework_units', 'scrap_units'},
    'fact_maintenance': {'maintenance_event_id', 'date', 'machine_id', 'maintenance_type', 'duration_min', 'failure_mode'},
    'fact_sensor': {'date', 'machine_id', 'plant_id', 'line_id', 'temperature_c', 'torque_nm', 'vibration_mm_s', 'tool_wear_index', 'failure_next_7d'},
    'fact_supply': {'month', 'supplier_id', 'ordered_qty', 'received_qty', 'material_defects', 'avg_late_days', 'supplier_reliability', 'shortage_hours'},
    'fact_orders': {'order_id', 'order_date', 'customer_id', 'product_id', 'quantity', 'unit_price', 'revenue', 'promised_date'},
    'fact_shipment': {'shipment_id', 'order_id', 'customer_id', 'ship_date', 'promised_date', 'actual_delivery_date', 'delay_days', 'on_time_flag', 'logistics_cost'},
    'fact_customer_service': {'service_event_id', 'order_id', 'customer_id', 'date', 'ticket_count', 'issue_type'},
    'fact_technology_incident': {'date', 'system_name', 'severity', 'duration_min', 'major_incident_flag', 'incident_type'},
    'fact_saas_usage': {'date', 'system_name', 'active_users', 'adoption_rate'},
    'fact_finance': {'month', 'revenue', 'material_cost', 'labor_cost', 'scrap_cost', 'logistics_cost', 'downtime_cost', 'technology_cost', 'overhead_cost', 'operating_cost', 'budget_operating_cost', 'gross_margin_proxy', 'operating_margin_proxy', 'budget_variance'},
}

FOREIGN_KEYS = [
    ('dim_line', 'plant_id', 'dim_plant', 'plant_id'),
    ('dim_machine', 'line_id', 'dim_line', 'line_id'),
    ('dim_machine', 'plant_id', 'dim_plant', 'plant_id'),
    ('dim_employee', 'plant_id', 'dim_plant', 'plant_id'),
    ('fact_workforce', 'plant_id', 'dim_plant', 'plant_id'),
    ('fact_recruitment', 'plant_id', 'dim_plant', 'plant_id'),
    ('fact_production', 'plant_id', 'dim_plant', 'plant_id'),
    ('fact_production', 'line_id', 'dim_line', 'line_id'),
    ('fact_production', 'machine_id', 'dim_machine', 'machine_id'),
    ('fact_production', 'product_id', 'dim_product', 'product_id'),
    ('fact_downtime', 'plant_id', 'dim_plant', 'plant_id'),
    ('fact_downtime', 'line_id', 'dim_line', 'line_id'),
    ('fact_downtime', 'machine_id', 'dim_machine', 'machine_id'),
    ('fact_quality', 'plant_id', 'dim_plant', 'plant_id'),
    ('fact_quality', 'line_id', 'dim_line', 'line_id'),
    ('fact_quality', 'machine_id', 'dim_machine', 'machine_id'),
    ('fact_quality', 'product_id', 'dim_product', 'product_id'),
    ('fact_maintenance', 'machine_id', 'dim_machine', 'machine_id'),
    ('fact_sensor', 'plant_id', 'dim_plant', 'plant_id'),
    ('fact_sensor', 'line_id', 'dim_line', 'line_id'),
    ('fact_sensor', 'machine_id', 'dim_machine', 'machine_id'),
    ('fact_supply', 'supplier_id', 'dim_supplier', 'supplier_id'),
    ('fact_orders', 'customer_id', 'dim_customer', 'customer_id'),
    ('fact_orders', 'product_id', 'dim_product', 'product_id'),
    ('fact_shipment', 'order_id', 'fact_orders', 'order_id'),
    ('fact_shipment', 'customer_id', 'dim_customer', 'customer_id'),
    ('fact_customer_service', 'order_id', 'fact_orders', 'order_id'),
    ('fact_customer_service', 'customer_id', 'dim_customer', 'customer_id'),
]

DATE_FIELDS = {
    'fact_workforce': ('month', 'monthly'),
    'fact_recruitment': ('month', 'monthly'),
    'fact_production': ('date', 'daily'),
    'fact_downtime': ('date', 'event'),
    'fact_quality': ('date', 'event'),
    'fact_maintenance': ('date', 'event'),
    'fact_sensor': ('date', 'daily'),
    'fact_supply': ('month', 'monthly'),
    'fact_orders': ('order_date', 'daily'),
    'fact_shipment': ('ship_date', 'daily'),
    'fact_customer_service': ('date', 'event'),
    'fact_technology_incident': ('date', 'event'),
    'fact_saas_usage': ('date', 'daily'),
    'fact_finance': ('month', 'monthly'),
}

FRESHNESS_TOLERANCE_DAYS = {'daily': 2, 'event': 14, 'monthly': 35}


def _schema_signature(df: pd.DataFrame) -> str:
    payload = '|'.join(f'{column}:{df[column].dtype}' for column in df.columns)
    return hashlib.sha256(payload.encode('utf-8')).hexdigest()[:16]


def _all_nonnegative(df: pd.DataFrame, columns: Iterable[str]) -> bool:
    existing = [c for c in columns if c in df.columns]
    return bool((df[existing] >= 0).all().all()) if existing else False


def evaluate(frames):
    results = []
    for name, df in frames.items():
        rows = len(df)
        total_cells = int(df.shape[0] * df.shape[1])
        null_cells = int(df.isna().sum().sum())
        duplicate_rows = int(df.duplicated().sum())
        pk = PRIMARY_KEYS.get(name)
        duplicate_keys = int(df[pk].duplicated().sum()) if pk and pk in df else 0
        required = REQUIRED_COLUMNS.get(name, set())
        missing_required = sorted(required.difference(df.columns))
        status = 'PASS' if duplicate_keys == 0 and duplicate_rows == 0 and not missing_required else 'FAIL'
        results.append({
            'table': name,
            'row_count': rows,
            'column_count': int(df.shape[1]),
            'total_cells': total_cells,
            'null_cells': null_cells,
            'null_rate': (null_cells / total_cells) if total_cells else 0.0,
            'duplicate_rows': duplicate_rows,
            'duplicate_keys': duplicate_keys,
            'required_columns_missing': len(missing_required),
            'missing_required_columns': '|'.join(missing_required),
            'schema_signature': _schema_signature(df),
            'status': status,
        })
    table_quality = pd.DataFrame(results)

    checks = []
    prod = frames['fact_production']
    checks.extend([
        ('production_counts_nonnegative', _all_nonnegative(prod, ['total_count', 'good_count', 'defect_units', 'rework_units', 'scrap_units']), 'validity'),
        ('good_count_not_above_total', bool((prod['good_count'] <= prod['total_count']).all()), 'validity'),
        ('runtime_positive', bool((prod['run_time_min'] > 0).all()), 'validity'),
        ('planned_downtime_within_planned_time', bool((prod['planned_downtime_min'] <= prod['planned_production_min']).all()), 'validity'),
        ('production_identity_consistent', bool((prod['good_count'] + prod['scrap_units'] == prod['total_count']).all()), 'consistency'),
    ])

    ship = frames['fact_shipment']
    checks.extend([
        ('shipment_delay_nonnegative', bool((ship['delay_days'] >= 0).all()), 'validity'),
        ('shipment_on_time_flag_binary', bool(ship['on_time_flag'].isin([0, 1]).all()), 'validity'),
        ('shipment_date_ordering', bool((pd.to_datetime(ship['actual_delivery_date']) >= pd.to_datetime(ship['ship_date'])).all()), 'consistency'),
        ('shipment_delay_flag_consistent', bool((ship['on_time_flag'] == (ship['delay_days'] == 0).astype(int)).all()), 'consistency'),
    ])

    finance = frames['fact_finance']
    checks.extend([
        ('finance_revenue_nonnegative', bool((finance['revenue'] >= 0).all()), 'validity'),
        ('finance_operating_cost_nonnegative', bool((finance['operating_cost'] >= 0).all()), 'validity'),
        ('finance_margin_reconciles', bool(np.allclose(finance['operating_margin_proxy'], finance['revenue'] - finance['operating_cost'])), 'consistency'),
    ])

    workforce = frames['fact_workforce']
    checks.extend([
        ('workforce_headcount_nonnegative', _all_nonnegative(workforce, ['required_headcount', 'actual_headcount', 'vacancies']), 'validity'),
        ('workforce_vacancy_identity', bool((workforce['vacancies'] == (workforce['required_headcount'] - workforce['actual_headcount']).clip(lower=0)).all()), 'consistency'),
        ('workforce_rates_in_range', bool(workforce['absence_rate'].between(0, 1).all() and workforce['capacity_gap_pct'].between(0, 1).all()), 'validity'),
    ])

    recruitment = frames['fact_recruitment']
    funnel_ok = (
        (recruitment['screened'] <= recruitment['applicants']) &
        (recruitment['interviews'] <= recruitment['screened']) &
        (recruitment['offers'] <= recruitment['interviews']) &
        (recruitment['accepted'] <= recruitment['offers'])
    ).all()
    checks.append(('recruitment_funnel_monotonic', bool(funnel_ok), 'consistency'))

    supply = frames['fact_supply']
    checks.extend([
        ('supplier_reliability_in_range', bool(supply['supplier_reliability'].between(0, 1).all()), 'validity'),
        ('supply_quantities_nonnegative', _all_nonnegative(supply, ['ordered_qty', 'received_qty', 'material_defects', 'avg_late_days', 'shortage_hours']), 'validity'),
    ])

    tech = frames['fact_saas_usage']
    checks.append(('saas_adoption_in_range', bool(tech['adoption_rate'].between(0, 1).all()), 'validity'))

    sensor = frames['fact_sensor']
    checks.append(('failure_target_binary', bool(sensor['failure_next_7d'].isin([0, 1]).all()), 'validity'))

    business = pd.DataFrame(checks, columns=['check', 'passed', 'dimension'])
    business['status'] = np.where(business['passed'], 'PASS', 'FAIL')
    return table_quality, business


def evaluate_referential_integrity(frames):
    rows = []
    for child_table, child_key, parent_table, parent_key in FOREIGN_KEYS:
        child = frames[child_table]
        parent = frames[parent_table]
        nonnull = child[child_key].dropna()
        orphan_mask = ~nonnull.isin(parent[parent_key].dropna())
        orphan_count = int(orphan_mask.sum())
        rows.append({
            'check_type': 'referential_integrity',
            'child_table': child_table,
            'child_key': child_key,
            'parent_table': parent_table,
            'parent_key': parent_key,
            'rows_checked': int(len(nonnull)),
            'failure_count': orphan_count,
            'passed': orphan_count == 0,
        })

    # Cross-key hierarchy consistency: IDs may all exist independently yet still point to incompatible parents.
    line_map = frames['dim_line'].set_index('line_id')['plant_id']
    machine_map = frames['dim_machine'].set_index('machine_id')[['line_id', 'plant_id']]

    for table_name in ['fact_production', 'fact_downtime', 'fact_quality', 'fact_sensor']:
        df = frames[table_name]
        if {'machine_id', 'line_id', 'plant_id'}.issubset(df.columns):
            expected = df[['machine_id']].join(machine_map, on='machine_id', rsuffix='_expected')
            failures = (
                (df['line_id'].astype(str).to_numpy() != expected['line_id'].astype(str).to_numpy()) |
                (df['plant_id'].astype(str).to_numpy() != expected['plant_id'].astype(str).to_numpy())
            )
            rows.append({
                'check_type': 'consistency',
                'child_table': table_name,
                'child_key': 'machine_id+line_id+plant_id',
                'parent_table': 'dim_machine',
                'parent_key': 'machine_id+line_id+plant_id',
                'rows_checked': int(len(df)),
                'failure_count': int(failures.sum()),
                'passed': int(failures.sum()) == 0,
            })

    machine_lines = frames['dim_machine']['line_id'].map(line_map)
    mismatch = (machine_lines.astype(str).to_numpy() != frames['dim_machine']['plant_id'].astype(str).to_numpy())
    rows.append({
        'check_type': 'consistency',
        'child_table': 'dim_machine',
        'child_key': 'line_id+plant_id',
        'parent_table': 'dim_line',
        'parent_key': 'line_id+plant_id',
        'rows_checked': int(len(frames['dim_machine'])),
        'failure_count': int(mismatch.sum()),
        'passed': int(mismatch.sum()) == 0,
    })

    result = pd.DataFrame(rows)
    result['status'] = np.where(result['passed'], 'PASS', 'FAIL')
    return result


def build_observability(frames):
    reference_date = pd.to_datetime(frames['fact_production']['date'], errors='coerce').max()
    rows = []

    for name, df in frames.items():
        date_field, cadence = DATE_FIELDS.get(name, (None, None))
        min_date = pd.NaT
        max_date = pd.NaT
        parse_failures = 0
        freshness_lag_days = np.nan
        freshness_tolerance_days = np.nan
        freshness_passed = True
        timeliness_passed = True

        if date_field and date_field in df.columns:
            parsed = pd.to_datetime(df[date_field], errors='coerce')
            parse_failures = int(parsed.isna().sum() - df[date_field].isna().sum())
            min_date = parsed.min()
            max_date = parsed.max()
            tolerance = FRESHNESS_TOLERANCE_DAYS[cadence]
            freshness_tolerance_days = tolerance
            if pd.notna(max_date) and pd.notna(reference_date):
                freshness_lag_days = max(0, int((reference_date.normalize() - max_date.normalize()).days))
                freshness_passed = freshness_lag_days <= tolerance
                # Synthetic shipment/service dates may extend beyond the simulation cutoff; 45 days is a fail-closed anomaly guard.
                timeliness_cutoff = pd.Timestamp(reference_date).normalize() + pd.DateOffset(days=45)
                timeliness_passed = parse_failures == 0 and pd.Timestamp(max_date) <= timeliness_cutoff
            else:
                freshness_passed = False
                timeliness_passed = False

        rows.append({
            'table': name,
            'row_count': int(len(df)),
            'column_count': int(df.shape[1]),
            'schema_signature': _schema_signature(df),
            'date_field': date_field or '',
            'cadence': cadence or '',
            'min_date': '' if pd.isna(min_date) else min_date.date().isoformat(),
            'max_date': '' if pd.isna(max_date) else max_date.date().isoformat(),
            'date_parse_failures': parse_failures,
            'freshness_lag_days': freshness_lag_days,
            'freshness_tolerance_days': freshness_tolerance_days,
            'freshness_passed': bool(freshness_passed),
            'timeliness_passed': bool(timeliness_passed),
            'status': 'PASS' if freshness_passed and timeliness_passed else 'FAIL',
        })

    return pd.DataFrame(rows)


def model_input_profile(frames):
    sensor = frames['fact_sensor']
    features = ['temperature_c', 'torque_nm', 'vibration_mm_s', 'tool_wear_index']
    rows = []
    for feature in features:
        series = sensor[feature]
        rows.append({
            'field': feature,
            'role': 'feature',
            'row_count': int(len(series)),
            'missing_count': int(series.isna().sum()),
            'missing_rate': float(series.isna().mean()),
            'unique_count': int(series.nunique(dropna=True)),
            'zero_variance': bool(series.nunique(dropna=True) <= 1),
            'positive_rate': np.nan,
        })
    target = sensor['failure_next_7d']
    rows.append({
        'field': 'failure_next_7d',
        'role': 'target',
        'row_count': int(len(target)),
        'missing_count': int(target.isna().sum()),
        'missing_rate': float(target.isna().mean()),
        'unique_count': int(target.nunique(dropna=True)),
        'zero_variance': bool(target.nunique(dropna=True) <= 1),
        'positive_rate': float(target.mean()),
    })
    return pd.DataFrame(rows)


def data_trust_score(
    table_quality: pd.DataFrame,
    business_checks: pd.DataFrame,
    referential_checks: pd.DataFrame | None = None,
    observability: pd.DataFrame | None = None,
):
    """Project-defined 0-100 composite. This is not an external industry standard."""
    total_cells = max(1, int(table_quality['total_cells'].sum()))
    completeness = 1 - min(1.0, float(table_quality['null_cells'].sum()) / total_cells)

    primary_uniqueness = float((table_quality['duplicate_keys'] == 0).mean()) if len(table_quality) else 0.0
    row_uniqueness = float((table_quality['duplicate_rows'] == 0).mean()) if len(table_quality) else 0.0
    uniqueness = (primary_uniqueness + row_uniqueness) / 2

    validity_rows = business_checks[business_checks['dimension'] == 'validity']
    consistency_rows = business_checks[business_checks['dimension'] == 'consistency']
    validity = float(validity_rows['passed'].mean()) if len(validity_rows) else 0.0
    business_consistency = float(consistency_rows['passed'].mean()) if len(consistency_rows) else 0.0

    schema_consistency = float((table_quality['required_columns_missing'] == 0).mean()) if len(table_quality) else 0.0

    if referential_checks is not None and len(referential_checks):
        ri_rows = referential_checks[referential_checks['check_type'] == 'referential_integrity']
        cross_rows = referential_checks[referential_checks['check_type'] == 'consistency']
        referential_integrity = float(ri_rows['passed'].mean()) if len(ri_rows) else 0.0
        cross_consistency = float(cross_rows['passed'].mean()) if len(cross_rows) else 0.0
        consistency = (business_consistency + cross_consistency) / 2
    else:
        referential_integrity = 1.0
        consistency = business_consistency

    if observability is not None and len(observability):
        dated = observability[observability['date_field'] != '']
        freshness = float(dated['freshness_passed'].mean()) if len(dated) else 0.0
        timeliness = float(dated['timeliness_passed'].mean()) if len(dated) else 0.0
    else:
        freshness = 1.0
        timeliness = 1.0

    components = {
        'completeness': completeness,
        'validity': validity,
        'consistency': consistency,
        'uniqueness': uniqueness,
        'timeliness': timeliness,
        'referential_integrity': referential_integrity,
        'schema_consistency': schema_consistency,
        'freshness': freshness,
    }
    score = 100 * sum(components.values()) / len(components)
    return round(score, 2), components
