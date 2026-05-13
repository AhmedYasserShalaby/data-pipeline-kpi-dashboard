from __future__ import annotations

import sqlite3
from contextlib import closing
from pathlib import Path

import pandas as pd

from pipeline.config import load_settings, project_path
from pipeline.paths import PROJECT_ROOT


MODEL_PATHS = [
    PROJECT_ROOT / "models" / "staging" / "stg_customers.sql",
    PROJECT_ROOT / "models" / "staging" / "stg_products.sql",
    PROJECT_ROOT / "models" / "staging" / "stg_orders.sql",
    PROJECT_ROOT / "models" / "staging" / "stg_returns.sql",
    PROJECT_ROOT / "models" / "intermediate" / "int_order_lines.sql",
    PROJECT_ROOT / "models" / "marts" / "mart_monthly_revenue.sql",
    PROJECT_ROOT / "models" / "marts" / "mart_product_performance.sql",
    PROJECT_ROOT / "models" / "marts" / "mart_customer_segments.sql",
]


def build_analytics_models(database_path: Path | None = None) -> dict[str, int]:
    settings = load_settings()
    database_path = database_path or project_path(settings["database"]["path"])
    row_counts = {}
    with closing(sqlite3.connect(database_path)) as connection:
        for model_path in MODEL_PATHS:
            model_name = model_path.stem
            _validate_identifier(model_name)
            sql = model_path.read_text(encoding="utf-8").strip().rstrip(";")
            connection.execute(f"DROP VIEW IF EXISTS {model_name}")
            connection.execute(f"CREATE VIEW {model_name} AS {sql}")
            row_counts[model_name] = int(
                pd.read_sql_query(f"SELECT COUNT(*) AS row_count FROM {model_name}", connection).loc[0, "row_count"]
            )
        connection.commit()
    return row_counts


def _validate_identifier(identifier: str) -> None:
    if not identifier.replace("_", "").isalnum():
        raise ValueError(f"Unsafe SQL identifier: {identifier}")
