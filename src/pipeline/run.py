from __future__ import annotations

from pathlib import Path

import pandas as pd

from pipeline.cleaning import clean_customers, clean_orders, clean_products, clean_returns
from pipeline.config import ensure_parent, load_settings, project_path
from pipeline.kpis import export_kpis
from pipeline.load import load_sqlite
from pipeline.paths import PROJECT_ROOT
from pipeline.quality import build_quality_summary, write_quality_report


def run_pipeline() -> dict[str, Path]:
    settings = load_settings()

    raw_paths = {name: project_path(path) for name, path in settings["raw_data"].items()}
    processed_paths = {name: project_path(path) for name, path in settings["processed_data"].items()}
    database_path = project_path(settings["database"]["path"])
    schema_path = PROJECT_ROOT / "sql" / "schema.sql"
    export_paths = {name: project_path(path) for name, path in settings["exports"].items() if name != "directory"}

    raw_customers = pd.read_csv(raw_paths["customers"])
    raw_products = pd.read_csv(raw_paths["products"])
    raw_orders = pd.read_csv(raw_paths["orders"])
    raw_returns = pd.read_csv(raw_paths["returns"])
    raw_counts = {
        "customers": len(raw_customers),
        "products": len(raw_products),
        "orders": len(raw_orders),
        "returns": len(raw_returns),
    }

    customers, customer_issues = clean_customers(raw_customers)
    products, product_issues = clean_products(raw_products)
    orders, order_issues = clean_orders(raw_orders, customers, products)
    returns, return_issues = clean_returns(raw_returns, orders)
    issues = pd.concat([customer_issues, product_issues, order_issues, return_issues], ignore_index=True)

    tables = {
        "customers": customers,
        "products": products,
        "orders": orders,
        "returns": returns,
    }
    clean_counts = {name: len(frame) for name, frame in tables.items()}
    for name, frame in tables.items():
        ensure_parent(processed_paths[name])
        frame.to_csv(processed_paths[name], index=False)

    load_sqlite(database_path, schema_path, tables)
    export_kpis(database_path, export_paths, issues)
    quality_summary = build_quality_summary(raw_counts, clean_counts, issues)
    quality_summary.to_csv(project_path("data/processed/dashboard_exports/data_quality_summary.csv"), index=False)
    write_quality_report(quality_summary, issues, PROJECT_ROOT / "docs" / "data_quality_report.md")
    return {
        "database": database_path,
        "exports": project_path(settings["exports"]["directory"]),
    }
