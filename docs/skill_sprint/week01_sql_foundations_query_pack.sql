-- Week 01 — SQL foundations (SQLite)
-- Target DB: data/processed/kpi_dashboard.sqlite
-- Tables: stg_customers, stg_products, stg_orders, stg_returns + marts

-- 0) Quick schema peek helpers (optional)
-- .tables
-- .schema stg_orders

-- 1) Basic select + LIMIT
SELECT * FROM stg_orders LIMIT 10;

-- 2) Count rows per table
SELECT 'stg_customers' AS table_name, COUNT(*) AS row_count FROM stg_customers
UNION ALL
SELECT 'stg_products', COUNT(*) FROM stg_products
UNION ALL
SELECT 'stg_orders', COUNT(*) FROM stg_orders
UNION ALL
SELECT 'stg_returns', COUNT(*) FROM stg_returns;

-- 3) Distinct customer count
SELECT COUNT(DISTINCT customer_id) AS distinct_customers FROM stg_orders;

-- 4) Orders with NULLs in key columns (NULL handling)
SELECT COUNT(*) AS bad_rows
FROM stg_orders
WHERE order_id IS NULL OR customer_id IS NULL OR product_id IS NULL;

-- 5) Daily orders trend (aggregation)
SELECT order_date, COUNT(*) AS orders
FROM stg_orders
GROUP BY order_date
ORDER BY order_date;

-- 6) Revenue by day (aggregation)
SELECT order_date, ROUND(SUM(net_revenue), 2) AS net_revenue
FROM stg_orders
GROUP BY order_date
ORDER BY order_date;

-- 7) Top 10 products by net revenue (GROUP BY + ORDER BY)
SELECT product_id, ROUND(SUM(net_revenue), 2) AS net_revenue
FROM stg_orders
GROUP BY product_id
ORDER BY net_revenue DESC
LIMIT 10;

-- 8) JOIN orders -> products (INNER JOIN)
SELECT
  o.order_id,
  o.order_date,
  o.product_id,
  p.product_name,
  o.quantity,
  o.net_revenue
FROM stg_orders o
JOIN stg_products p
  ON o.product_id = p.product_id
LIMIT 25;

-- 9) LEFT JOIN to find orders with missing product dimension
SELECT COUNT(*) AS missing_product_dim_rows
FROM stg_orders o
LEFT JOIN stg_products p
  ON o.product_id = p.product_id
WHERE p.product_id IS NULL;

-- 10) Customer order counts (JOIN + aggregation)
SELECT
  o.customer_id,
  c.customer_name,
  COUNT(DISTINCT o.order_id) AS orders
FROM stg_orders o
JOIN stg_customers c
  ON o.customer_id = c.customer_id
GROUP BY o.customer_id, c.customer_name
ORDER BY orders DESC
LIMIT 20;

-- 11) Average order value by customer (AOV)
WITH customer_orders AS (
  SELECT customer_id, order_id, SUM(net_revenue) AS order_value
  FROM stg_orders
  GROUP BY customer_id, order_id
)
SELECT
  customer_id,
  ROUND(AVG(order_value), 2) AS avg_order_value,
  COUNT(*) AS orders
FROM customer_orders
GROUP BY customer_id
ORDER BY avg_order_value DESC
LIMIT 20;

-- 12) Revenue by category (JOIN + GROUP BY)
SELECT
  p.category,
  ROUND(SUM(o.net_revenue), 2) AS net_revenue
FROM stg_orders o
JOIN stg_products p
  ON o.product_id = p.product_id
GROUP BY p.category
ORDER BY net_revenue DESC;

-- 13) Gross margin by category (uses stg_orders.margin if exists)
SELECT
  p.category,
  ROUND(SUM(o.gross_margin), 2) AS gross_margin
FROM stg_orders o
JOIN stg_products p
  ON o.product_id = p.product_id
GROUP BY p.category
ORDER BY gross_margin DESC;

-- 14) Find negative or zero quantities (data quality)
SELECT COUNT(*) AS non_positive_qty
FROM stg_orders
WHERE quantity <= 0;

-- 15) Find suspicious negative net revenue (returns/discounts)
SELECT COUNT(*) AS negative_net_revenue_rows
FROM stg_orders
WHERE net_revenue < 0;

-- 16) Returns rate by product (JOIN + NULL-safe division)
WITH product_sales AS (
  SELECT product_id, SUM(quantity) AS sold_qty
  FROM stg_orders
  GROUP BY product_id
),
product_returns AS (
  SELECT product_id, SUM(return_quantity) AS returned_qty
  FROM stg_returns
  GROUP BY product_id
)
SELECT
  s.product_id,
  ROUND(COALESCE(r.returned_qty, 0) * 1.0 / NULLIF(s.sold_qty, 0), 4) AS return_rate_qty
FROM product_sales s
LEFT JOIN product_returns r
  ON s.product_id = r.product_id
ORDER BY return_rate_qty DESC
LIMIT 20;

-- 17) Customers with no orders (LEFT JOIN anti-join)
SELECT c.customer_id, c.customer_name
FROM stg_customers c
LEFT JOIN stg_orders o
  ON c.customer_id = o.customer_id
WHERE o.customer_id IS NULL
LIMIT 50;

-- 18) Products with no sales (LEFT JOIN anti-join)
SELECT p.product_id, p.product_name
FROM stg_products p
LEFT JOIN stg_orders o
  ON p.product_id = o.product_id
WHERE o.product_id IS NULL
LIMIT 50;

-- 19) Month-level revenue (date bucketing)
SELECT
  substr(order_date, 1, 7) AS month,
  ROUND(SUM(net_revenue), 2) AS net_revenue
FROM stg_orders
GROUP BY substr(order_date, 1, 7)
ORDER BY month;

-- 20) Month-over-month revenue growth (CTE self-join)
WITH monthly AS (
  SELECT substr(order_date, 1, 7) AS month, SUM(net_revenue) AS revenue
  FROM stg_orders
  GROUP BY substr(order_date, 1, 7)
),
shifted AS (
  SELECT
    m1.month,
    m1.revenue,
    m2.revenue AS prev_revenue
  FROM monthly m1
  LEFT JOIN monthly m2
    ON m2.month = (
      SELECT substr(date(m1.month || '-01', '-1 month'), 1, 7)
    )
)
SELECT
  month,
  ROUND(revenue, 2) AS revenue,
  ROUND(prev_revenue, 2) AS prev_revenue,
  ROUND((revenue - prev_revenue) * 1.0 / NULLIF(prev_revenue, 0), 4) AS mom_growth
FROM shifted
ORDER BY month;

-- 21) Validate marts: monthly revenue matches stg_orders monthly sum
WITH stg_monthly AS (
  SELECT substr(order_date, 1, 7) AS month, ROUND(SUM(net_revenue), 2) AS revenue
  FROM stg_orders
  GROUP BY substr(order_date, 1, 7)
),
mart_monthly AS (
  SELECT month, ROUND(net_revenue, 2) AS revenue
  FROM mart_monthly_revenue
)
SELECT
  s.month,
  s.revenue AS stg_revenue,
  m.revenue AS mart_revenue,
  ROUND(s.revenue - m.revenue, 2) AS diff
FROM stg_monthly s
LEFT JOIN mart_monthly m
  ON s.month = m.month
ORDER BY s.month;

-- 22) Top customers by revenue (CTE)
WITH customer_rev AS (
  SELECT customer_id, SUM(net_revenue) AS revenue
  FROM stg_orders
  GROUP BY customer_id
)
SELECT customer_id, ROUND(revenue, 2) AS revenue
FROM customer_rev
ORDER BY revenue DESC
LIMIT 20;

-- 23) Customer segments sanity check
SELECT segment, COUNT(*) AS customers
FROM mart_customer_segments
GROUP BY segment
ORDER BY customers DESC;

-- 24) Compare mart product performance vs recompute from stg_orders
WITH stg_prod AS (
  SELECT product_id,
         ROUND(SUM(net_revenue), 2) AS net_revenue,
         ROUND(SUM(gross_margin), 2) AS gross_margin,
         SUM(quantity) AS units
  FROM stg_orders
  GROUP BY product_id
)
SELECT
  s.product_id,
  s.net_revenue AS stg_net_revenue,
  ROUND(m.net_revenue, 2) AS mart_net_revenue,
  ROUND(s.net_revenue - m.net_revenue, 2) AS diff_net_revenue,
  s.units AS stg_units,
  m.units_sold AS mart_units
FROM stg_prod s
LEFT JOIN mart_product_performance m
  ON s.product_id = m.product_id
ORDER BY ABS(diff_net_revenue) DESC
LIMIT 25;

-- 25) Find duplicated IDs in dimensions (should be 0)
SELECT 'stg_customers' AS table_name, COUNT(*) - COUNT(DISTINCT customer_id) AS dupes FROM stg_customers
UNION ALL
SELECT 'stg_products', COUNT(*) - COUNT(DISTINCT product_id) FROM stg_products;

-- 26) Orders per customer distribution (bucket)
WITH orders_per_customer AS (
  SELECT customer_id, COUNT(DISTINCT order_id) AS orders
  FROM stg_orders
  GROUP BY customer_id
)
SELECT
  CASE
    WHEN orders = 1 THEN '1'
    WHEN orders BETWEEN 2 AND 3 THEN '2-3'
    WHEN orders BETWEEN 4 AND 6 THEN '4-6'
    ELSE '7+'
  END AS bucket,
  COUNT(*) AS customers
FROM orders_per_customer
GROUP BY bucket
ORDER BY customers DESC;

-- 27) Top 10 days by revenue
SELECT order_date, ROUND(SUM(net_revenue), 2) AS revenue
FROM stg_orders
GROUP BY order_date
ORDER BY revenue DESC
LIMIT 10;

-- 28) Revenue share by category (CTE + percent)
WITH cat_rev AS (
  SELECT p.category, SUM(o.net_revenue) AS revenue
  FROM stg_orders o
  JOIN stg_products p ON o.product_id = p.product_id
  GROUP BY p.category
),
tot AS (
  SELECT SUM(revenue) AS total_revenue FROM cat_rev
)
SELECT
  c.category,
  ROUND(c.revenue, 2) AS revenue,
  ROUND(c.revenue * 1.0 / NULLIF(t.total_revenue, 0), 4) AS revenue_share
FROM cat_rev c
CROSS JOIN tot t
ORDER BY revenue DESC;

-- 29) Find customers with multiple names (should be 0; checks key correctness)
SELECT customer_id, COUNT(DISTINCT customer_name) AS names
FROM stg_customers
GROUP BY customer_id
HAVING COUNT(DISTINCT customer_name) > 1;

-- 30) Anti-join: returns with missing order/product references
SELECT COUNT(*) AS returns_missing_product
FROM stg_returns r
LEFT JOIN stg_products p
  ON r.product_id = p.product_id
WHERE p.product_id IS NULL;

