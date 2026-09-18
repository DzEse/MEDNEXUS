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
    technology_downtime_min,
    LAG(revenue) OVER (ORDER BY month) AS prior_month_revenue,
    revenue - LAG(revenue) OVER (ORDER BY month) AS revenue_change_vs_prior_month,
    AVG(oee) OVER (
        ORDER BY month
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ) AS oee_3_month_rolling_avg,
    CASE
        WHEN capacity_gap_pct >= 0.10 THEN 'High capacity pressure'
        WHEN capacity_gap_pct >= 0.05 THEN 'Moderate capacity pressure'
        ELSE 'Lower capacity pressure'
    END AS capacity_pressure_band
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


DROP VIEW IF EXISTS kpi_supplier_risk_ranked;
CREATE VIEW kpi_supplier_risk_ranked AS
WITH supplier_summary AS (
    SELECT
        supplier_id,
        AVG(supplier_reliability) AS avg_supplier_reliability,
        SUM(shortage_hours) AS total_shortage_hours,
        SUM(material_defects) AS total_material_defects
    FROM fact_supply
    GROUP BY supplier_id
)
SELECT
    supplier_id,
    avg_supplier_reliability,
    total_shortage_hours,
    total_material_defects,
    RANK() OVER (
        ORDER BY total_shortage_hours DESC, total_material_defects DESC
    ) AS shortage_risk_rank,
    CASE
        WHEN avg_supplier_reliability < 0.90 THEN 'High'
        WHEN avg_supplier_reliability < 0.95 THEN 'Watch'
        ELSE 'Stable'
    END AS reliability_band
FROM supplier_summary;
