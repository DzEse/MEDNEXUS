from __future__ import annotations

import pandas as pd


ALLOWED_ORDER_FULFILLMENT_ACTIVITIES = (
    'Order Created',
    'Shipped',
    'Delivered',
    'Service Issue',
)

PROHIBITED_UNLINKED_ACTIVITIES = (
    'Production',
    'Inspection',
    'Rework',
    'Release',
)


def build_order_fulfillment_event_log(frames) -> pd.DataFrame:
    orders = frames['fact_orders'].copy()
    shipments = frames['fact_shipment'].copy()
    service = frames['fact_customer_service'].copy()

    order_required = {'order_id', 'order_date', 'customer_id', 'product_id'}
    ship_required = {'shipment_id', 'order_id', 'ship_date', 'actual_delivery_date'}
    service_required = {'service_event_id', 'order_id', 'date'}

    for name, frame, required in [
        ('fact_orders', orders, order_required),
        ('fact_shipment', shipments, ship_required),
        ('fact_customer_service', service, service_required),
    ]:
        missing = required.difference(frame.columns)
        if missing:
            raise ValueError(f'{name} missing process-analytics fields: {sorted(missing)}')

    if orders['order_id'].duplicated().any():
        raise ValueError('Order process cases are not unique by order_id.')
    if shipments['order_id'].duplicated().any():
        raise ValueError('Order process has more than one shipment row per order.')

    rows = []
    for row in orders.itertuples(index=False):
        rows.append(
            {
                'event_id': f'{row.order_id}::01',
                'case_id': row.order_id,
                'activity': 'Order Created',
                'event_date': pd.Timestamp(row.order_date),
                'event_sequence': 1,
                'source_table': 'fact_orders',
                'source_record_id': row.order_id,
                'event_semantics': 'OBSERVED_SYNTHETIC_SOURCE_EVENT',
            }
        )

    for row in shipments.itertuples(index=False):
        rows.extend(
            [
                {
                    'event_id': f'{row.order_id}::02',
                    'case_id': row.order_id,
                    'activity': 'Shipped',
                    'event_date': pd.Timestamp(row.ship_date),
                    'event_sequence': 2,
                    'source_table': 'fact_shipment',
                    'source_record_id': row.shipment_id,
                    'event_semantics': 'OBSERVED_SYNTHETIC_SOURCE_EVENT',
                },
                {
                    'event_id': f'{row.order_id}::03',
                    'case_id': row.order_id,
                    'activity': 'Delivered',
                    'event_date': pd.Timestamp(row.actual_delivery_date),
                    'event_sequence': 3,
                    'source_table': 'fact_shipment',
                    'source_record_id': row.shipment_id,
                    'event_semantics': 'OBSERVED_SYNTHETIC_SOURCE_EVENT',
                },
            ]
        )

    for row in service.itertuples(index=False):
        rows.append(
            {
                'event_id': f'{row.order_id}::04::{row.service_event_id}',
                'case_id': row.order_id,
                'activity': 'Service Issue',
                'event_date': pd.Timestamp(row.date),
                'event_sequence': 4,
                'source_table': 'fact_customer_service',
                'source_record_id': row.service_event_id,
                'event_semantics': 'OBSERVED_SYNTHETIC_SOURCE_EVENT',
            }
        )

    event_log = pd.DataFrame(rows)
    if event_log['event_id'].duplicated().any():
        raise RuntimeError('Order-fulfillment event IDs are not unique.')

    invalid = set(event_log['activity']).difference(ALLOWED_ORDER_FULFILLMENT_ACTIVITIES)
    if invalid:
        raise RuntimeError(f'Unsupported process events were introduced: {sorted(invalid)}')

    event_log = event_log.sort_values(
        ['case_id', 'event_date', 'event_sequence', 'event_id']
    ).reset_index(drop=True)

    for case_id, group in event_log.groupby('case_id', sort=False):
        dates = group['event_date']
        if not dates.is_monotonic_increasing:
            raise RuntimeError(f'Event chronology is invalid for case {case_id}.')

    return event_log


def build_order_fulfillment_cases(frames) -> pd.DataFrame:
    orders = frames['fact_orders'].copy()
    shipments = frames['fact_shipment'].copy()
    service = frames['fact_customer_service'].copy()
    customers = frames['dim_customer'][['customer_id', 'customer_type', 'region']].copy()
    products = frames['dim_product'][['product_id', 'product_family']].copy()

    cases = orders[
        ['order_id', 'order_date', 'customer_id', 'product_id', 'promised_date', 'quantity']
    ].merge(
        shipments[
            [
                'order_id',
                'shipment_id',
                'ship_date',
                'actual_delivery_date',
                'delay_days',
                'on_time_flag',
            ]
        ],
        on='order_id',
        how='left',
        validate='one_to_one',
    )

    if cases['shipment_id'].isna().any():
        raise RuntimeError('Order-fulfillment analytics require one shipment for every order.')

    cases = cases.merge(customers, on='customer_id', how='left', validate='many_to_one')
    cases = cases.merge(products, on='product_id', how='left', validate='many_to_one')

    service_counts = (
        service.groupby('order_id', as_index=False)
        .agg(
            service_event_count=('service_event_id', 'count'),
            service_ticket_count=('ticket_count', 'sum'),
        )
    )
    cases = cases.merge(service_counts, on='order_id', how='left', validate='one_to_one')
    cases[['service_event_count', 'service_ticket_count']] = (
        cases[['service_event_count', 'service_ticket_count']].fillna(0).astype(int)
    )

    for column in ['order_date', 'ship_date', 'actual_delivery_date', 'promised_date']:
        cases[column] = pd.to_datetime(cases[column])

    cases['order_to_ship_days'] = (
        cases['ship_date'] - cases['order_date']
    ).dt.days
    cases['ship_to_delivery_days'] = (
        cases['actual_delivery_date'] - cases['ship_date']
    ).dt.days
    cases['order_to_delivery_days'] = (
        cases['actual_delivery_date'] - cases['order_date']
    ).dt.days
    cases['promised_lead_days'] = (
        cases['promised_date'] - cases['order_date']
    ).dt.days
    cases['delivery_vs_promise_days'] = (
        cases['actual_delivery_date'] - cases['promised_date']
    ).dt.days

    duration_fields = [
        'order_to_ship_days',
        'ship_to_delivery_days',
        'order_to_delivery_days',
        'promised_lead_days',
    ]
    if (cases[duration_fields] < 0).any().any():
        raise RuntimeError('Negative order-fulfillment cycle time detected.')

    cases['process_scope'] = 'ORDER_FULFILLMENT_ONLY'
    cases['mining_status'] = 'SUPPORTED_PARTIAL_EVENT_LOG'
    return cases


def build_transition_summary(cases: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for from_activity, to_activity, duration_field in [
        ('Order Created', 'Shipped', 'order_to_ship_days'),
        ('Shipped', 'Delivered', 'ship_to_delivery_days'),
    ]:
        duration = cases[duration_field].astype(float)
        rows.append(
            {
                'from_activity': from_activity,
                'to_activity': to_activity,
                'cases': int(len(cases)),
                'mean_duration_days': float(duration.mean()),
                'median_duration_days': float(duration.median()),
                'p90_duration_days': float(duration.quantile(0.90)),
                'max_duration_days': float(duration.max()),
                'transition_status': 'SUPPORTED_BY_LINKED_SOURCE_EVENTS',
            }
        )

    out = pd.DataFrame(rows)
    out['bottleneck_rank'] = out['median_duration_days'].rank(
        method='dense', ascending=False
    ).astype(int)
    out['interpretation'] = (
        'Cycle-time bottleneck indicator for the supported order-fulfillment process; '
        'not a full manufacturing-process-mining result.'
    )
    return out.sort_values('bottleneck_rank').reset_index(drop=True)


def process_mining_gate() -> dict:
    return {
        'full_process_mining_status': 'NOT_ADMITTED_MISSING_END_TO_END_CASE_LINKAGE',
        'partial_process_analytics_status': 'SUPPORTED_ORDER_FULFILLMENT_ONLY',
        'desired_process': [
            'Order',
            'Production',
            'Inspection',
            'Rework',
            'Release',
            'Shipment',
        ],
        'supported_linked_process': [
            'Order Created',
            'Shipped',
            'Delivered',
            'Service Issue (optional)',
        ],
        'prohibited_fabricated_events': list(PROHIBITED_UNLINKED_ACTIVITIES),
        'missing_required_linkage': [
            'customer order_id to production_order_id',
            'production_order_id to quality/inspection events',
            'case-linked rework event timestamps',
            'case-linked release event timestamps',
            'end-to-end order/manufacturing/shipment case identifier',
        ],
        'decision': (
            'Use supported order-fulfillment cycle-time/transition analytics only. '
            'Do not run full manufacturing process mining until defensible case linkage exists.'
        ),
    }


def experimentation_gate() -> dict:
    return {
        'experimentation_status': 'NOT_ADMITTED_NO_EXECUTED_INTERVENTION_OR_TREATMENT_ASSIGNMENT',
        'causal_effect_estimated': False,
        'experiment_executed': False,
        'current_evidence': (
            'Scenario assumptions and prospective monitoring plans exist, but no treatment assignment '
            'or observed post-intervention outcome data exist.'
        ),
        'future_design_hierarchy': [
            'Randomized controlled intervention where operationally feasible',
            'Matched treatment/control or difference-in-differences when assignment is non-random but defensible',
            'Interrupted time series / pre-post only with sufficient history and explicit causal limitations',
        ],
        'minimum_future_fields': [
            'intervention_id',
            'entity_id',
            'intervention_type',
            'intervention_start_date',
            'treatment_flag',
            'pre_period_start',
            'post_period_end',
            'primary_outcome',
            'observed_outcome_value',
            'comparison_group_id_or_rule',
        ],
        'admission_rule': (
            'Estimate intervention effects only after a documented design, treatment/comparison definition, '
            'pre-intervention evidence, post-intervention observations and assumption checks exist.'
        ),
        'decision': 'Keep experimentation as a prospective validation framework; calculate no treatment effect now.',
    }


def run_process_and_experiment_gates(frames):
    event_log = build_order_fulfillment_event_log(frames)
    cases = build_order_fulfillment_cases(frames)
    transitions = build_transition_summary(cases)
    process_gate = process_mining_gate()
    experiment_gate = experimentation_gate()

    methodology = {
        'process_scope': 'ORDER_FULFILLMENT_ONLY',
        'case_id': 'order_id',
        'event_count': int(len(event_log)),
        'case_count': int(cases['order_id'].nunique()),
        'supported_activity_count': int(event_log['activity'].nunique()),
        'full_process_mining_admitted': False,
        'experimentation_admitted': False,
        'anti_fabrication_rule': (
            'No Production, Inspection, Rework or Release event is created because those source facts '
            'lack defensible order-level case linkage.'
        ),
    }

    return {
        'event_log': event_log,
        'cases': cases,
        'transition_summary': transitions,
        'process_gate': process_gate,
        'experiment_gate': experiment_gate,
        'methodology': methodology,
    }
