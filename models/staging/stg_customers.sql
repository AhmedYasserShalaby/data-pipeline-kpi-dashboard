SELECT
    customer_id,
    customer_name,
    segment,
    country,
    city,
    DATE(signup_date) AS signup_date
FROM customers
