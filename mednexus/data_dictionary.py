from __future__ import annotations

import pandas as pd

from .quality import DATE_FIELDS, FOREIGN_KEYS, PRIMARY_KEYS


GRAINS = {
    'dim_plant': 'one row per plant',
    'dim_line': 'one row per production line',
    'dim_machine': 'one row per machine',
    'dim_product': 'one row per product',
    'dim_supplier': 'one row per supplier',
    'dim_customer': 'one row per healthcare customer',
    'dim_employee': 'one row per synthetic employee',
    'dim_warehouse': 'one row per simulated warehouse serving a MEDNEXUS plant',
    'dim_shift': 'one row per standard shift definition',
    'dim_department': 'one row per enterprise department',
    'dim_job_role': 'one row per department x job role',
    'fact_employee_assignment': 'one current synthetic assignment per employee',
    'fact_workforce': 'one row per month x plant',
    'fact_recruitment': 'one row per month x plant',
    'fact_production': 'one row per production order x machine x day',
    'fact_downtime': 'one row per downtime event',
    'fact_quality': 'one row per quality event',
    'fact_maintenance': 'one row per maintenance event',
    'fact_sensor': 'one row per day x machine',
    'fact_supply': 'one row per month x supplier',
    'fact_orders': 'one row per customer order',
    'fact_shipment': 'one row per shipment',
    'fact_customer_service': 'one row per customer-service event',
    'fact_technology_incident': 'one row per technology incident',
    'fact_saas_usage': 'one row per day x technology system',
    'fact_finance': 'one row per enterprise month',
}

BUSINESS_MEANING = {
    'dim_plant': 'Enterprise operating-site reference.',
    'dim_line': 'Manufacturing production-line reference.',
    'dim_machine': 'Manufacturing asset reference with age and hierarchy.',
    'dim_product': 'Product and product-family reference with synthetic unit economics.',
    'dim_supplier': 'Supplier reference with lead-time and quality attributes.',
    'dim_customer': 'Healthcare-customer reference without patient-identifiable information.',
    'dim_employee': 'Synthetic workforce reference connected only through the current employee-assignment snapshot.',
    'dim_warehouse': 'Synthetic plant-serving warehouse reference for map and future inventory drill paths.',
    'dim_shift': 'Standard synthetic shift reference for workforce segmentation.',
    'dim_department': 'Enterprise workforce department reference.',
    'dim_job_role': 'Department-scoped synthetic job-role reference with critical-role indicator.',
    'fact_employee_assignment': 'Current synthetic Employee→Department→Role→Plant→Shift assignment snapshot; line is informational and not an active Power BI relationship.',
    'fact_workforce': 'Monthly workforce requirement, capacity, absence, overtime and labor-cost facts.',
    'fact_recruitment': 'Monthly recruitment funnel and hiring-capacity facts.',
    'fact_production': 'Daily machine-level production, downtime and quality-count facts.',
    'fact_downtime': 'Operational downtime-event facts.',
    'fact_quality': 'Quality-event defects, rework, scrap and severity facts.',
    'fact_maintenance': 'Preventive/corrective maintenance-event facts.',
    'fact_sensor': 'Daily machine condition features and synthetic failure-risk target.',
    'fact_supply': 'Monthly supplier delivery, quality and shortage facts.',
    'fact_orders': 'Synthetic healthcare-customer order facts.',
    'fact_shipment': 'Shipment timing, delivery and logistics-cost facts.',
    'fact_customer_service': 'Customer-service issues linked to synthetic orders.',
    'fact_technology_incident': 'Enterprise technology incident facts.',
    'fact_saas_usage': 'Daily technology-system usage and adoption facts.',
    'fact_finance': 'Monthly enterprise synthetic financial reconciliation and illustrative cost proxies.',
}

COLUMN_DESCRIPTIONS = {
    'plant_id': 'Stable synthetic plant identifier.',
    'line_id': 'Stable synthetic production-line identifier.',
    'machine_id': 'Stable synthetic machine identifier.',
    'product_id': 'Stable synthetic product identifier.',
    'supplier_id': 'Stable synthetic supplier identifier.',
    'customer_id': 'Stable synthetic healthcare-customer identifier.',
    'employee_id': 'Stable synthetic employee identifier.',
    'warehouse_id': 'Stable synthetic warehouse identifier.',
    'shift_id': 'Stable synthetic shift identifier.',
    'department_id': 'Stable synthetic department identifier.',
    'job_role_id': 'Stable synthetic job-role identifier.',
    'assignment_id': 'Stable synthetic current-assignment identifier.',
    'order_id': 'Stable synthetic customer-order identifier.',
    'shipment_id': 'Stable synthetic shipment identifier.',
    'production_order_id': 'Stable synthetic production-order identifier.',
    'quality_event_id': 'Stable synthetic quality-event identifier.',
    'downtime_event_id': 'Stable synthetic downtime-event identifier.',
    'maintenance_event_id': 'Stable synthetic maintenance-event identifier.',
    'service_event_id': 'Stable synthetic service-event identifier.',
    'month': 'Month-start date for the observation period.',
    'date': 'Calendar date for the observation or event.',
    'revenue': 'Synthetic order-derived revenue for the period.',
    'operating_cost': 'Synthetic operating cost reconciled from operational costs and documented assumptions.',
    'budget_operating_cost': 'Illustrative synthetic operating-cost budget comparator.',
    'gross_margin_proxy': 'Derived gross-margin proxy; not an audited accounting measure.',
    'operating_margin_proxy': 'Derived revenue minus operating-cost proxy.',
    'budget_variance': 'Derived operating cost minus synthetic budget operating cost.',
    'downtime_cost': 'Illustrative financial assumption derived from unplanned downtime minutes.',
    'technology_cost': 'Illustrative technology-cost proxy.',
    'failure_next_7d': 'Synthetic binary modeling target indicating simulated near-term failure risk.',
    'adoption_rate': 'Synthetic 0-1 technology adoption rate.',
    'capacity_gap_pct': 'Derived required-versus-actual workforce capacity gap rate.',
    'supplier_reliability': 'Synthetic supplier reliability rate.',
    'on_time_flag': 'Binary indicator equal to 1 when delivery delay is zero.',
    'delay_days': 'Nonnegative days between promised and actual delivery date.',
    'geography_region': 'Role-specific simulated geographic region used for mapping; not a shared active Region dimension.',
    'geography_status': 'Explicit label identifying simulated enterprise geography.',
    'latitude': 'Simulated latitude used only for enterprise map analysis.',
    'longitude': 'Simulated longitude used only for enterprise map analysis.',
    'assignment_status': 'Current synthetic canonical assignment status.',
}


def _humanize(column: str) -> str:
    return column.replace('_', ' ').strip().capitalize() + '.'


def _foreign_key_target(table: str, column: str) -> str:
    targets = [
        f'{parent_table}.{parent_key}'
        for child_table, child_key, parent_table, parent_key in FOREIGN_KEYS
        if child_table == table and child_key == column
    ]
    return '|'.join(targets)


def _semantic_role(table: str, column: str, series: pd.Series) -> str:
    if PRIMARY_KEYS.get(table) == column:
        return 'primary_key'
    if _foreign_key_target(table, column):
        return 'foreign_key'
    if table in DATE_FIELDS and DATE_FIELDS[table][0] == column:
        return 'date'
    if column.endswith('_id'):
        return 'identifier'
    if pd.api.types.is_numeric_dtype(series):
        return 'measure'
    return 'attribute'


def build_data_dictionary(frames) -> pd.DataFrame:
    rows = []
    for table, df in frames.items():
        for column in df.columns:
            series = df[column]
            nonnull = series.dropna()
            example = '' if nonnull.empty else str(nonnull.iloc[0])
            rows.append({
                'table': table,
                'column': column,
                'dtype': str(series.dtype),
                'semantic_role': _semantic_role(table, column, series),
                'description': COLUMN_DESCRIPTIONS.get(column, _humanize(column)),
                'foreign_key_target': _foreign_key_target(table, column),
                'observed_nullable': bool(series.isna().any()),
                'observed_null_count': int(series.isna().sum()),
                'observed_unique_count': int(series.nunique(dropna=True)),
                'example_value': example,
                'data_classification': 'synthetic',
            })
    return pd.DataFrame(rows)


def build_table_register(frames) -> pd.DataFrame:
    rows = []
    for table, df in frames.items():
        fk_targets = [
            f'{child_key}->{parent_table}.{parent_key}'
            for child_table, child_key, parent_table, parent_key in FOREIGN_KEYS
            if child_table == table
        ]
        date_field, cadence = DATE_FIELDS.get(table, ('', 'reference'))
        rows.append({
            'table': table,
            'grain': GRAINS.get(table, 'document before production use'),
            'primary_key': PRIMARY_KEYS.get(table, 'composite/none documented'),
            'foreign_keys': '|'.join(fk_targets),
            'row_count': int(len(df)),
            'expected_cardinality': 'dimension' if table.startswith('dim_') else 'fact',
            'refresh_logic': f'regenerated deterministically; {cadence} analytical cadence',
            'date_field': date_field,
            'business_meaning': BUSINESS_MEANING.get(table, 'Synthetic MEDNEXUS analytical table.'),
            'source_classification': 'synthetic',
        })
    return pd.DataFrame(rows)
