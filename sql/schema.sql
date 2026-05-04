DROP TABLE IF EXISTS kpi_executive_overview;
DROP TABLE IF EXISTS returns;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS customers;

CREATE TABLE customers (
    customer_id TEXT PRIMARY KEY,
    customer_name TEXT NOT NULL,
    segment TEXT NOT NULL,
    country TEXT NOT NULL,
    city TEXT NOT NULL,
    signup_date TEXT NOT NULL
);

CREATE TABLE products (
    product_id TEXT PRIMARY KEY,
    product_name TEXT NOT NULL,
    category TEXT NOT NULL,
    unit_cost REAL NOT NULL,
    unit_price REAL NOT NULL
);

CREATE TABLE orders (
    order_id TEXT PRIMARY KEY,
    order_date TEXT NOT NULL,
    order_month TEXT NOT NULL,
    customer_id TEXT NOT NULL,
    product_id TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    discount REAL NOT NULL,
    unit_price REAL NOT NULL,
    revenue REAL NOT NULL,
    cost REAL NOT NULL,
    gross_profit REAL NOT NULL,
    margin REAL NOT NULL,
    status TEXT NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

CREATE TABLE returns (
    return_id TEXT PRIMARY KEY,
    order_id TEXT NOT NULL,
    return_date TEXT NOT NULL,
    reason TEXT NOT NULL,
    refunded_amount REAL NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
);
