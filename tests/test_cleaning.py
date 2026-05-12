import pandas as pd

from pipeline.cleaning import clean_customers, clean_orders, clean_products, parse_dates


def test_parse_dates_handles_mixed_formats():
    result = parse_dates(pd.Series(["2025-01-15", "20/02/2025", "2025/03/10"]))
    assert result.tolist() == ["2025-01-15", "2025-02-20", "2025-03-10"]


def test_clean_customers_removes_duplicate_customer_ids():
    raw = pd.DataFrame(
        [
            {
                "customer_id": " c-001 ",
                "customer_name": "alice",
                "segment": "consumer",
                "country": "egypt",
                "city": "cairo",
                "signup_date": "2025-01-01",
            },
            {
                "customer_id": "C-001",
                "customer_name": "alice duplicate",
                "segment": "consumer",
                "country": "egypt",
                "city": "cairo",
                "signup_date": "2025-01-01",
            },
        ]
    )
    clean, issues = clean_customers(raw)
    assert len(clean) == 1
    assert clean.loc[0, "customer_id"] == "C-001"
    assert issues.empty


def test_clean_orders_calculates_revenue_and_flags_invalid_rows():
    customers = pd.DataFrame([{"customer_id": "C-001"}])
    products = pd.DataFrame([{"product_id": "P-001", "unit_cost": 40.0}])
    raw = pd.DataFrame(
        [
            {
                "order_id": "O-001",
                "order_date": "2025-01-01",
                "customer_id": "C-001",
                "product_id": "P-001",
                "quantity": 2,
                "discount": 0.1,
                "unit_price": 100.0,
                "status": "completed",
            },
            {
                "order_id": "O-002",
                "order_date": "2025-01-02",
                "customer_id": "C-999",
                "product_id": "P-001",
                "quantity": 1,
                "discount": 0,
                "unit_price": 100.0,
                "status": "completed",
            },
            {
                "order_id": "O-003",
                "order_date": "2025-01-03",
                "customer_id": "C-001",
                "product_id": "P-001",
                "quantity": -1,
                "discount": 0,
                "unit_price": 100.0,
                "status": "completed",
            },
        ]
    )
    clean, issues = clean_orders(raw, customers, products)
    assert len(clean) == 1
    assert clean.loc[0, "revenue"] == 180.0
    assert clean.loc[0, "gross_profit"] == 100.0
    assert len(issues) == 2


def test_clean_products_standardizes_categories():
    raw = pd.DataFrame(
        [
            {
                "product_id": "p-001",
                "product_name": "keyboard",
                "category": "ELECTRONICS",
                "unit_cost": "50",
                "unit_price": "80",
            }
        ]
    )
    clean, issues = clean_products(raw)
    assert clean.loc[0, "product_id"] == "P-001"
    assert clean.loc[0, "category"] == "Electronics"
    assert issues.empty
