SELECT
    product_id,
    product_name,
    category,
    SUM(quantity) AS units_sold,
    ROUND(SUM(revenue), 2) AS revenue,
    ROUND(SUM(gross_profit), 2) AS gross_profit,
    ROUND(SUM(gross_profit) / NULLIF(SUM(revenue), 0), 4) AS gross_margin
FROM int_order_lines
GROUP BY product_id, product_name, category
