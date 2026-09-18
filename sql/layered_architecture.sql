-- MEDNEXUS explicit layered analytical architecture.
-- These views expose staging validation, dimensional hierarchy, fact enrichment,
-- KPI presentation and reconciliation without duplicating persisted source data.

DROP VIEW IF EXISTS stg_production_validated;
CREATE VIEW stg_production_validated AS
SELECT *
FROM fact_production
WHERE total_count >= 0
  AND good_count >= 0
  AND defect_units >= 0
  AND rework_units >= 0
  AND scrap_units >= 0
  AND run_time_min > 0
  AND good_count + scrap_units = total_count;

DROP VIEW IF EXISTS dim_machine_hierarchy;
CREATE VIEW dim_machine_hierarchy AS
SELECT
    m.machine_id,
    m.machine_name,
    m.machine_age_years,
    l.line_id,
    l.line_name,
    p.plant_id,
    p.plant_name,
    p.region
FROM dim_machine m
JOIN dim_line l ON m.line_id = l.line_id
JOIN dim_plant p ON l.plant_id = p.plant_id;

DROP VIEW IF EXISTS fact_order_fulfillment_enriched;
CREATE VIEW fact_order_fulfillment_enriched AS
SELECT
    o.order_id,
    o.order_date,
    o.customer_id,
    o.product_id,
    o.quantity,
    o.revenue,
    s.shipment_id,
    s.ship_date,
    s.promised_date,
    s.actual_delivery_date,
    s.delay_days,
    s.on_time_flag,
    s.logistics_cost,
    CAST(julianday(s.ship_date) - julianday(o.order_date) AS INTEGER) AS order_to_ship_days,
    CAST(julianday(s.actual_delivery_date) - julianday(s.ship_date) AS INTEGER) AS ship_to_delivery_days,
    CAST(julianday(s.actual_delivery_date) - julianday(o.order_date) AS INTEGER) AS order_to_delivery_days
FROM fact_orders o
JOIN fact_shipment s ON o.order_id = s.order_id;

DROP VIEW IF EXISTS kpi_monthly_operations;
CREATE VIEW kpi_monthly_operations AS
SELECT
    month,
    revenue,
    operating_cost,
    oee,
    fpy,
    oli,
    capacity_gap_pct,
    on_time_delivery,
    shortage_hours,
    technology_downtime_min
FROM mart_enterprise_monthly;

DROP VIEW IF EXISTS val_order_fulfillment_grain;
CREATE VIEW val_order_fulfillment_grain AS
SELECT
    COUNT(*) AS row_count,
    COUNT(DISTINCT order_id) AS distinct_order_count,
    COUNT(*) - COUNT(DISTINCT order_id) AS duplicate_order_rows
FROM fact_order_fulfillment_enriched;

DROP VIEW IF EXISTS val_machine_hierarchy_grain;
CREATE VIEW val_machine_hierarchy_grain AS
SELECT
    COUNT(*) AS row_count,
    COUNT(DISTINCT machine_id) AS distinct_machine_count,
    COUNT(*) - COUNT(DISTINCT machine_id) AS duplicate_machine_rows
FROM dim_machine_hierarchy;
