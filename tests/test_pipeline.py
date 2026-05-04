import sqlite3
from pathlib import Path

import pandas as pd

from pipeline.generate_data import generate_all
from pipeline.run import run_pipeline
from pipeline.config import load_settings, project_path


def test_pipeline_creates_sqlite_tables_and_kpi_exports():
    generate_all()
    outputs = run_pipeline()

    database_path = outputs["database"]
    export_dir = outputs["exports"]
    assert database_path.exists()
    assert export_dir.exists()

    with sqlite3.connect(database_path) as connection:
        tables = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type = 'table'", connection)
        assert {"customers", "products", "orders", "returns"}.issubset(set(tables["name"]))
        order_count = pd.read_sql_query("SELECT COUNT(*) AS count FROM orders", connection).loc[0, "count"]
        revenue = pd.read_sql_query("SELECT ROUND(SUM(revenue), 2) AS revenue FROM orders", connection).loc[0, "revenue"]

    settings = load_settings()
    overview_path = project_path(settings["exports"]["executive_overview"])
    overview = pd.read_csv(overview_path)
    assert order_count > 0
    assert revenue > 0
    assert round(float(overview.loc[0, "total_revenue"]), 2) == round(float(revenue), 2)

    required_exports = [
        "executive_overview.csv",
        "monthly_revenue.csv",
        "product_performance.csv",
        "customer_analysis.csv",
        "returns_quality.csv",
        "data_quality_issues.csv",
    ]
    for filename in required_exports:
        assert (Path(export_dir) / filename).exists()
