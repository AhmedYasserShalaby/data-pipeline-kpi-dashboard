SELECT
    order_month,
    ROUND(SUM(revenue), 2) AS revenue,
    COUNT(DISTINCT order_id) AS orders,
    COUNT(DISTINCT customer_id) AS customers,
    ROUND(SUM(revenue) / NULLIF(COUNT(DISTINCT order_id), 0), 2) AS average_order_value,
    ROUND(SUM(gross_profit) / NULLIF(SUM(revenue), 0), 4) AS gross_margin
FROM int_order_lines
GROUP BY order_month
