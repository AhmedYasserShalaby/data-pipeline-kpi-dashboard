import sqlite3
from contextlib import closing

import pandas as pd

from pipeline.config import load_settings, project_path
from pipeline.generate_data import generate_all
from pipeline.models import build_analytics_models
from pipeline.run import run_pipeline


def test_build_analytics_models_creates_dbt_style_views():
    generate_all()
    run_pipeline(mode="full")

    row_counts = build_analytics_models()

    assert row_counts["stg_orders"] > 0
    assert row_counts["int_order_lines"] == row_counts["stg_orders"]
    assert row_counts["mart_monthly_revenue"] > 0

    database_path = project_path(load_settings()["database"]["path"])
    with closing(sqlite3.connect(database_path)) as connection:
        views = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type = 'view'", connection)
        monthly_revenue = pd.read_sql_query(
            "SELECT ROUND(SUM(revenue), 2) AS revenue FROM mart_monthly_revenue", connection
        )
        order_revenue = pd.read_sql_query("SELECT ROUND(SUM(revenue), 2) AS revenue FROM orders", connection)

    assert {"stg_orders", "int_order_lines", "mart_monthly_revenue"}.issubset(set(views["name"]))
    assert float(monthly_revenue.loc[0, "revenue"]) == float(order_revenue.loc[0, "revenue"])
