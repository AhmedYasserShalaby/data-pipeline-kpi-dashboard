SELECT
    o.order_id,
    o.order_date,
    o.order_month,
    o.status,
    c.customer_id,
    c.customer_name,
    c.segment,
    c.country,
    c.city,
    p.product_id,
    p.product_name,
    p.category,
    o.quantity,
    o.discount,
    o.unit_price,
    o.revenue,
    o.cost,
    o.gross_profit,
    o.margin
FROM stg_orders o
JOIN stg_customers c ON o.customer_id = c.customer_id
JOIN stg_products p ON o.product_id = p.product_id
