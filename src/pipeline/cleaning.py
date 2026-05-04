from __future__ import annotations

import pandas as pd


def normalize_id(series: pd.Series) -> pd.Series:
    return series.astype(str).str.strip().str.upper()


def parse_dates(series: pd.Series) -> pd.Series:
    parsed = pd.to_datetime(series, errors="coerce", format="mixed", dayfirst=False)
    fallback = pd.to_datetime(series, errors="coerce", format="mixed", dayfirst=True)
    return parsed.fillna(fallback).dt.date.astype("string")


def title_text(series: pd.Series, fallback: str = "Unknown") -> pd.Series:
    cleaned = series.fillna("").astype(str).str.strip()
    cleaned = cleaned.mask(cleaned.eq(""), fallback)
    return cleaned.str.title()


def clean_customers(raw: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    frame = raw.copy()
    frame["customer_id"] = normalize_id(frame["customer_id"])
    frame["customer_name"] = title_text(frame["customer_name"], "Unknown Customer")
    frame["segment"] = title_text(frame["segment"], "Unknown")
    frame["country"] = title_text(frame["country"], "Unknown")
    frame["city"] = title_text(frame["city"], "Unknown")
    frame["signup_date"] = parse_dates(frame["signup_date"])

    issues = _issue_rows(frame[frame["signup_date"].isna()], "customers", "invalid_signup_date")
    frame = frame.dropna(subset=["signup_date"])
    frame = frame.drop_duplicates(subset=["customer_id"], keep="first")
    return frame.reset_index(drop=True), issues


def clean_products(raw: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    frame = raw.copy()
    frame["product_id"] = normalize_id(frame["product_id"])
    frame["product_name"] = title_text(frame["product_name"], "Unknown Product")
    frame["category"] = title_text(frame["category"], "Uncategorized")
    frame["unit_cost"] = pd.to_numeric(frame["unit_cost"], errors="coerce")
    frame["unit_price"] = pd.to_numeric(frame["unit_price"], errors="coerce")

    invalid = frame["unit_cost"].isna() | frame["unit_price"].isna() | (frame["unit_price"] <= 0)
    issues = _issue_rows(frame[invalid], "products", "invalid_price_or_cost")
    frame = frame[~invalid].drop_duplicates(subset=["product_id"], keep="first")
    return frame.reset_index(drop=True), issues


def clean_orders(raw: pd.DataFrame, customers: pd.DataFrame, products: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    frame = raw.copy()
    frame["order_id"] = normalize_id(frame["order_id"])
    frame["customer_id"] = normalize_id(frame["customer_id"])
    frame["product_id"] = normalize_id(frame["product_id"])
    frame["order_date"] = parse_dates(frame["order_date"])
    frame["quantity"] = pd.to_numeric(frame["quantity"], errors="coerce")
    frame["discount"] = pd.to_numeric(frame["discount"], errors="coerce").fillna(0)
    frame["unit_price"] = pd.to_numeric(frame["unit_price"], errors="coerce")
    frame["status"] = title_text(frame["status"], "Completed")

    customer_ids = set(customers["customer_id"])
    product_ids = set(products["product_id"])
    invalid = (
        frame["order_date"].isna()
        | frame["quantity"].isna()
        | (frame["quantity"] <= 0)
        | frame["unit_price"].isna()
        | ~frame["customer_id"].isin(customer_ids)
        | ~frame["product_id"].isin(product_ids)
    )
    issues = _issue_rows(frame[invalid], "orders", "invalid_order_or_missing_dimension")
    frame = frame[~invalid].drop_duplicates(subset=["order_id"], keep="first")

    costs = products.set_index("product_id")["unit_cost"]
    frame["cost"] = frame["product_id"].map(costs) * frame["quantity"]
    frame["revenue"] = frame["quantity"] * frame["unit_price"] * (1 - frame["discount"])
    frame["gross_profit"] = frame["revenue"] - frame["cost"]
    frame["margin"] = frame["gross_profit"] / frame["revenue"]
    frame["order_month"] = frame["order_date"].str.slice(0, 7)

    money_columns = ["unit_price", "revenue", "cost", "gross_profit", "margin"]
    frame[money_columns] = frame[money_columns].round(4)
    ordered = [
        "order_id",
        "order_date",
        "order_month",
        "customer_id",
        "product_id",
        "quantity",
        "discount",
        "unit_price",
        "revenue",
        "cost",
        "gross_profit",
        "margin",
        "status",
    ]
    return frame[ordered].reset_index(drop=True), issues


def clean_returns(raw: pd.DataFrame, orders: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    frame = raw.copy()
    frame["return_id"] = normalize_id(frame["return_id"])
    frame["order_id"] = normalize_id(frame["order_id"])
    frame["return_date"] = parse_dates(frame["return_date"])
    frame["reason"] = title_text(frame["reason"], "Unknown")
    frame["refunded_amount"] = pd.to_numeric(frame["refunded_amount"], errors="coerce")

    order_ids = set(orders["order_id"])
    invalid = frame["return_date"].isna() | frame["refunded_amount"].isna() | ~frame["order_id"].isin(order_ids)
    issues = _issue_rows(frame[invalid], "returns", "invalid_return_or_missing_order")
    frame = frame[~invalid].drop_duplicates(subset=["return_id"], keep="first")
    return frame.reset_index(drop=True), issues


def _issue_rows(frame: pd.DataFrame, table: str, issue_type: str) -> pd.DataFrame:
    if frame.empty:
        return pd.DataFrame(columns=["table_name", "issue_type", "row_reference"])
    id_column = next((column for column in frame.columns if column.endswith("_id")), None)
    references = frame[id_column].astype(str) if id_column else frame.index.astype(str)
    return pd.DataFrame(
        {
            "table_name": table,
            "issue_type": issue_type,
            "row_reference": references,
        }
    )

