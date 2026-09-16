# Data Model and Grain Register

| Table | Grain | Primary key | Main relationships |
|---|---|---|---|
| dim_plant | one row per plant | plant_id | line, machine, workforce |
| dim_line | one row per production line | line_id | plant_id |
| dim_machine | one row per machine | machine_id | line_id, plant_id |
| dim_product | one row per product | product_id | production, orders, quality |
| dim_supplier | one row per supplier | supplier_id | supply |
| dim_customer | one row per healthcare customer | customer_id | orders, shipment, service |
| dim_employee | one row per employee | employee_id | department, plant |
| fact_finance | one row per month | month (natural period) | enterprise time |
| fact_workforce | one row per month × plant | composite | plant_id |
| fact_recruitment | one row per month × plant | composite | plant_id |
| fact_production | one row per production order/machine/day | production_order_id | plant, line, machine, product |
| fact_quality | one row per quality event | quality_event_id | machine, line, product |
| fact_downtime | one row per downtime event | downtime_event_id | machine, line, plant |
| fact_maintenance | one row per maintenance event | maintenance_event_id | machine |
| fact_sensor | one row per day × machine | composite | machine, line, plant |
| fact_supply | one row per month × supplier | composite | supplier_id |
| fact_orders | one row per customer order | order_id | customer, product |
| fact_shipment | one row per shipment | shipment_id | order, customer |
| fact_customer_service | one row per service event | service_event_id | order, customer |
| fact_technology_incident | one row per incident | composite | system, date |
| fact_saas_usage | one row per day × system | composite | system, date |

Mixed-grain facts are intentionally avoided. Cross-domain analysis is performed through conformed date/plant/entity keys or at compatible aggregate grain.
