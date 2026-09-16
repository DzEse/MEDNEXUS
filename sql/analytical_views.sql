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
