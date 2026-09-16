-- Reconcile production totals against quality-event totals.
SELECT
    (SELECT SUM(defect_units) FROM fact_production) AS production_defect_units,
    (SELECT SUM(defect_units) FROM fact_quality) AS quality_event_defect_units,
    (SELECT SUM(scrap_units) FROM fact_production) AS production_scrap_units,
    (SELECT SUM(scrap_units) FROM fact_quality) AS quality_event_scrap_units;
