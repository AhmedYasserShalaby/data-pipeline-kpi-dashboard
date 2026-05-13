SELECT
    order_id,
    DATE(order_date) AS order_date,
    order_month,
    customer_id,
    product_id,
    quantity,
    discount,
    unit_price,
    revenue,
    cost,
    gross_profit,
    margin,
    status
FROM orders
