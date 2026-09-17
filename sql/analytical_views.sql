DROP VIEW IF EXISTS vw_enterprise_command_center;
CREATE VIEW vw_enterprise_command_center AS
SELECT
    e.month,
    e.revenue,
    e.operating_cost,
    e.gross_margin_proxy,
    e.oee,
    e.oli,
    e.fpy,
    e.capacity_gap_pct,
    e.on_time_delivery,
    e.shortage_hours,
    e.technology_downtime_min,
    m.mori_score,
    m.mori_band
FROM mart_enterprise_monthly e
LEFT JOIN mart_mori m ON e.month = m.month;

DROP VIEW IF EXISTS vw_quality_loss;
CREATE VIEW vw_quality_loss AS
SELECT
    product_id,
    SUM(total_count) AS total_units,
    SUM(defect_units) AS defect_units,
    SUM(scrap_units) AS scrap_units,
    CAST(SUM(defect_units) AS REAL) / NULLIF(SUM(total_count),0) AS defect_rate
FROM fact_production
GROUP BY product_id;

DROP VIEW IF EXISTS vw_machine_reliability;
CREATE VIEW vw_machine_reliability AS
SELECT
    machine_id,
    COUNT(*) AS downtime_events,
    SUM(duration_min) AS downtime_minutes,
    AVG(duration_min) AS avg_downtime_minutes
FROM fact_downtime
GROUP BY machine_id;

DROP VIEW IF EXISTS vw_supplier_risk;
CREATE VIEW vw_supplier_risk AS
SELECT
    supplier_id,
    AVG(supplier_reliability) AS avg_supplier_reliability,
    SUM(shortage_hours) AS shortage_hours,
    SUM(material_defects) AS material_defects
FROM fact_supply
GROUP BY supplier_id;


DROP VIEW IF EXISTS vw_production_reconciliation;
CREATE VIEW vw_production_reconciliation AS
SELECT
    COUNT(*) AS production_rows,
    SUM(total_count) AS total_units,
    SUM(good_count) AS good_units,
    SUM(scrap_units) AS scrap_units,
    SUM(defect_units) AS defect_units,
    SUM(rework_units) AS rework_units,
    SUM(total_count - good_count - scrap_units) AS final_output_identity_difference,
    SUM((total_count - defect_units) - (good_count - rework_units)) AS first_pass_identity_difference
FROM fact_production;

DROP VIEW IF EXISTS vw_quality_reconciliation;
CREATE VIEW vw_quality_reconciliation AS
WITH p AS (
    SELECT
        SUM(defect_units) AS production_defects,
        SUM(rework_units) AS production_rework,
        SUM(scrap_units) AS production_scrap
    FROM fact_production
),
q AS (
    SELECT
        SUM(defect_units) AS quality_defects,
        SUM(rework_units) AS quality_rework,
        SUM(scrap_units) AS quality_scrap
    FROM fact_quality
)
SELECT
    p.production_defects,
    q.quality_defects,
    p.production_defects - q.quality_defects AS defect_difference,
    p.production_rework,
    q.quality_rework,
    p.production_rework - q.quality_rework AS rework_difference,
    p.production_scrap,
    q.quality_scrap,
    p.production_scrap - q.quality_scrap AS scrap_difference
FROM p CROSS JOIN q;

DROP VIEW IF EXISTS vw_finance_reconciliation;
CREATE VIEW vw_finance_reconciliation AS
WITH order_month AS (
    SELECT
        substr(CAST(order_date AS TEXT),1,7) AS month,
        SUM(revenue) AS order_revenue
    FROM fact_orders
    GROUP BY substr(CAST(order_date AS TEXT),1,7)
),
finance_month AS (
    SELECT
        substr(CAST(month AS TEXT),1,7) AS month,
        revenue,
        operating_cost,
        material_cost + labor_cost + scrap_cost + logistics_cost
            + downtime_cost + technology_cost + overhead_cost AS reconstructed_operating_cost
    FROM fact_finance
)
SELECT
    f.month,
    f.revenue,
    o.order_revenue,
    f.revenue - o.order_revenue AS revenue_difference,
    f.operating_cost,
    f.reconstructed_operating_cost,
    f.operating_cost - f.reconstructed_operating_cost AS operating_cost_difference
FROM finance_month f
LEFT JOIN order_month o ON f.month = o.month;

DROP VIEW IF EXISTS vw_monthly_value_loss;
CREATE VIEW vw_monthly_value_loss AS
SELECT
    month,
    operating_cost,
    scrap_cost,
    downtime_cost,
    logistics_cost,
    technology_cost,
    cost_per_good_unit,
    known_internal_quality_cost_proxy,
    rework_cost,
    full_copq,
    rework_cost_status,
    copq_status,
    financial_basis
FROM mart_value_leakage;
