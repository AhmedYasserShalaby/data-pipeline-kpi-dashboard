from __future__ import annotations

import random
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

from pipeline.config import ensure_parent, load_settings, project_path


SEGMENTS = ["Consumer", "Corporate", "Small Business"]
COUNTRIES = {
    "Egypt": ["Cairo", "Alexandria", "Giza", "Mansoura", "New Cairo"],
    "UAE": ["Dubai", "Abu Dhabi", "Sharjah"],
    "Saudi Arabia": ["Riyadh", "Jeddah", "Dammam"],
}
CATEGORIES = ["Electronics", "Office Supplies", "Home", "Sports", "Beauty", "Grocery"]
RETURN_REASONS = ["Damaged", "Late delivery", "Wrong item", "Changed mind", "Quality issue"]


def _random_date(start: date, end: date) -> date:
    days = (end - start).days
    return start + timedelta(days=random.randint(0, days))


def _messy_date(value: date, index: int) -> str:
    if index % 31 == 0:
        return value.strftime("%d/%m/%Y")
    if index % 47 == 0:
        return value.strftime("%Y/%m/%d")
    return value.isoformat()


def generate_customers(count: int) -> pd.DataFrame:
    rows = []
    for i in range(1, count + 1):
        country = random.choice(list(COUNTRIES))
        city = random.choice(COUNTRIES[country])
        rows.append(
            {
                "customer_id": f"c-{i:04d}" if i % 17 else f" C-{i:04d} ",
                "customer_name": f"Customer {i}",
                "segment": random.choice(SEGMENTS).lower() if i % 11 == 0 else random.choice(SEGMENTS),
                "country": country,
                "city": "" if i % 29 == 0 else city,
                "signup_date": _messy_date(_random_date(date(2023, 1, 1), date(2025, 12, 31)), i),
            }
        )
    frame = pd.DataFrame(rows)
    return pd.concat([frame, frame.iloc[[2]]], ignore_index=True)


def generate_products(count: int) -> pd.DataFrame:
    rows = []
    for i in range(1, count + 1):
        category = random.choice(CATEGORIES)
        unit_cost = round(random.uniform(25, 900), 2)
        unit_price = round(unit_cost * random.uniform(1.18, 1.95), 2)
        rows.append(
            {
                "product_id": f"P-{i:03d}",
                "product_name": f"{category} Product {i}",
                "category": category.upper() if i % 9 == 0 else category,
                "unit_cost": unit_cost,
                "unit_price": unit_price,
            }
        )
    return pd.DataFrame(rows)


def generate_orders(count: int, customers: pd.DataFrame, products: pd.DataFrame) -> pd.DataFrame:
    customer_ids = customers["customer_id"].str.strip().str.upper().drop_duplicates().tolist()
    product_ids = products["product_id"].tolist()
    product_prices = dict(zip(products["product_id"], products["unit_price"]))
    rows = []
    for i in range(1, count + 1):
        product_id = random.choice(product_ids)
        quantity = random.randint(1, 6)
        if i % 73 == 0:
            quantity = -1
        discount = random.choice([0, 0, 0, 0.05, 0.1, 0.15])
        unit_price = product_prices[product_id]
        status = random.choice(["Completed", "Completed", "Completed", "Completed", "Returned"])
        rows.append(
            {
                "order_id": f"O-{i:05d}",
                "order_date": _messy_date(_random_date(date(2025, 1, 1), date(2025, 12, 31)), i),
                "customer_id": random.choice(customer_ids) if i % 67 else "C-9999",
                "product_id": product_id,
                "quantity": quantity,
                "discount": discount,
                "unit_price": unit_price,
                "status": status,
            }
        )
    frame = pd.DataFrame(rows)
    return pd.concat([frame, frame.iloc[[4, 10]]], ignore_index=True)


def generate_returns(orders: pd.DataFrame) -> pd.DataFrame:
    returned = orders[orders["status"].str.lower().eq("returned")].head(75).copy()
    rows = []
    for i, row in enumerate(returned.itertuples(index=False), start=1):
        order_date = pd.to_datetime(row.order_date, format="mixed", dayfirst=False, errors="coerce")
        if pd.isna(order_date):
            order_date = pd.Timestamp("2025-01-01")
        return_date = order_date.date() + timedelta(days=random.randint(1, 21))
        rows.append(
            {
                "return_id": f"R-{i:04d}",
                "order_id": row.order_id,
                "return_date": _messy_date(return_date, i),
                "reason": random.choice(RETURN_REASONS),
                "refunded_amount": round(max(row.quantity, 1) * row.unit_price * (1 - row.discount), 2),
            }
        )
    return pd.DataFrame(rows)


def generate_all() -> dict[str, Path]:
    settings = load_settings()
    generator = settings["generator"]
    random.seed(generator["seed"])

    customers = generate_customers(generator["customers"])
    products = generate_products(generator["products"])
    orders = generate_orders(generator["orders"], customers, products)
    returns = generate_returns(orders)

    outputs = {
        "customers": project_path(settings["raw_data"]["customers"]),
        "products": project_path(settings["raw_data"]["products"]),
        "orders": project_path(settings["raw_data"]["orders"]),
        "returns": project_path(settings["raw_data"]["returns"]),
    }
    for name, frame in {
        "customers": customers,
        "products": products,
        "orders": orders,
        "returns": returns,
    }.items():
        ensure_parent(outputs[name])
        frame.to_csv(outputs[name], index=False)
    return outputs
