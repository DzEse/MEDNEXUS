-- Grain: one row per defect category.
SELECT
    defect_category,
    SUM(defect_units) AS defect_units,
    SUM(rework_units) AS rework_units,
    SUM(scrap_units) AS scrap_units,
    RANK() OVER (ORDER BY SUM(defect_units) DESC) AS defect_rank
FROM fact_quality
GROUP BY defect_category
ORDER BY defect_units DESC;
