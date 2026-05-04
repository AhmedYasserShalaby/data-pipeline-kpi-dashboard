-- Executive overview
SELECT
    ROUND(SUM(revenue), 2) AS total_revenue,
    COUNT(DISTINCT order_id) AS total_orders,
    COUNT(DISTINCT customer_id) AS total_customers,
    ROUND(SUM(revenue) / COUNT(DISTINCT order_id), 2) AS average_order_value,
    ROUND(SUM(gross_profit), 2) AS gross_profit,
    ROUND(SUM(gross_profit) / NULLIF(SUM(revenue), 0), 4) AS gross_margin,
    ROUND((SELECT SUM(refunded_amount) FROM returns), 2) AS refunded_amount,
    ROUND((SELECT COUNT(*) FROM returns) * 1.0 / COUNT(DISTINCT order_id), 4) AS return_rate
FROM orders;

-- Monthly revenue and growth
SELECT
    order_month,
    ROUND(SUM(revenue), 2) AS revenue,
    COUNT(DISTINCT order_id) AS orders,
    ROUND(SUM(revenue) / COUNT(DISTINCT order_id), 2) AS average_order_value,
    ROUND(
        (SUM(revenue) - LAG(SUM(revenue)) OVER (ORDER BY order_month))
        / NULLIF(LAG(SUM(revenue)) OVER (ORDER BY order_month), 0),
        4
    ) AS monthly_growth
FROM orders
GROUP BY order_month
ORDER BY order_month;

-- Product performance
SELECT
    p.product_id,
    p.product_name,
    p.category,
    SUM(o.quantity) AS units_sold,
    ROUND(SUM(o.revenue), 2) AS revenue,
    ROUND(SUM(o.gross_profit), 2) AS gross_profit,
    ROUND(SUM(o.gross_profit) / NULLIF(SUM(o.revenue), 0), 4) AS gross_margin
FROM orders o
JOIN products p ON o.product_id = p.product_id
GROUP BY p.product_id, p.product_name, p.category
ORDER BY revenue DESC;

-- Customer analysis
SELECT
    c.customer_id,
    c.customer_name,
    c.segment,
    c.country,
    c.city,
    COUNT(DISTINCT o.order_id) AS orders,
    ROUND(SUM(o.revenue), 2) AS revenue,
    ROUND(SUM(o.revenue) / COUNT(DISTINCT o.order_id), 2) AS average_order_value,
    CASE WHEN COUNT(DISTINCT o.order_id) > 1 THEN 1 ELSE 0 END AS repeat_customer
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.customer_name, c.segment, c.country, c.city
ORDER BY revenue DESC;

-- Returns and quality
SELECT
    p.category,
    r.reason,
    COUNT(*) AS returns,
    ROUND(SUM(r.refunded_amount), 2) AS refunded_amount
FROM returns r
JOIN orders o ON r.order_id = o.order_id
JOIN products p ON o.product_id = p.product_id
GROUP BY p.category, r.reason
ORDER BY refunded_amount DESC;
