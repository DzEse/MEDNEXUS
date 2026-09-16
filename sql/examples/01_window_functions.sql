-- Grain: one row per month.
WITH monthly AS (
    SELECT month, revenue, operating_cost
    FROM fact_finance
), calc AS (
    SELECT
        month,
        revenue,
        operating_cost,
        revenue - operating_cost AS operating_margin_proxy,
        AVG(revenue) OVER (ORDER BY month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS rolling_3m_revenue
    FROM monthly
)
SELECT * FROM calc ORDER BY month;
