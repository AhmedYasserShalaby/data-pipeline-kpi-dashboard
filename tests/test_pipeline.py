import sqlite3
from contextlib import closing
from pathlib import Path

import pandas as pd

from pipeline.contracts import load_contracts, validate_contracts
from pipeline.generate_data import generate_all
from pipeline.run import run_pipeline
from pipeline.config import load_settings, project_path


def test_pipeline_creates_sqlite_tables_and_kpi_exports():
    generate_all()
    outputs = run_pipeline(mode="full")

    database_path = outputs["database"]
    export_dir = outputs["exports"]
    assert database_path.exists()
    assert export_dir.exists()

    with closing(sqlite3.connect(database_path)) as connection:
        tables = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type = 'table'", connection)
        assert {"customers", "products", "orders", "returns", "pipeline_runs"}.issubset(set(tables["name"]))
        order_count = pd.read_sql_query("SELECT COUNT(*) AS count FROM orders", connection).loc[0, "count"]
        revenue = pd.read_sql_query("SELECT ROUND(SUM(revenue), 2) AS revenue FROM orders", connection).loc[
            0, "revenue"
        ]
        pipeline_runs = pd.read_sql_query("SELECT COUNT(*) AS count FROM pipeline_runs", connection).loc[0, "count"]

    settings = load_settings()
    overview_path = project_path(settings["exports"]["executive_overview"])
    overview = pd.read_csv(overview_path)
    assert order_count > 0
    assert revenue > 0
    assert pipeline_runs == 1
    assert round(float(overview.loc[0, "total_revenue"]), 2) == round(float(revenue), 2)

    required_exports = [
        "executive_overview.csv",
        "monthly_revenue.csv",
        "product_performance.csv",
        "customer_analysis.csv",
        "returns_quality.csv",
        "data_quality_issues.csv",
        "data_quality_summary.csv",
        "pipeline_run_summary.csv",
    ]
    for filename in required_exports:
        assert (Path(export_dir) / filename).exists()

    assert Path("docs/data_quality_report.md").exists()
    assert Path("docs/run_summary.md").exists()


def test_contract_validation_reports_invalid_rows():
    raw_tables = {name: pd.read_csv(path) for name, path in generate_all().items()}
    contracts = load_contracts(project_path("config/data_contracts.yaml"))

    issues = validate_contracts(raw_tables, contracts)

    assert not issues.empty
    assert {"duplicate_key", "numeric_below_min", "missing_foreign_key"}.issubset(set(issues["issue_type"]))


def test_incremental_pipeline_does_not_double_count_existing_orders():
    generate_all()
    run_pipeline(mode="full")

    database_path = project_path(load_settings()["database"]["path"])
    with closing(sqlite3.connect(database_path)) as connection:
        before = pd.read_sql_query(
            "SELECT COUNT(*) AS orders, ROUND(SUM(revenue), 2) AS revenue FROM orders", connection
        ).iloc[0]

    run_pipeline(mode="incremental")

    with closing(sqlite3.connect(database_path)) as connection:
        after = pd.read_sql_query(
            "SELECT COUNT(*) AS orders, ROUND(SUM(revenue), 2) AS revenue FROM orders", connection
        ).iloc[0]
        loaded_rows = pd.read_sql_query(
            "SELECT loaded_rows FROM pipeline_runs ORDER BY started_at_utc DESC LIMIT 1",
            connection,
        ).loc[0, "loaded_rows"]

    assert int(after["orders"]) == int(before["orders"])
    assert float(after["revenue"]) == float(before["revenue"])
    assert loaded_rows == 0


def test_incremental_pipeline_loads_only_new_records():
    generate_all()
    run_pipeline(mode="full")

    settings = load_settings()
    database_path = project_path(settings["database"]["path"])
    orders_path = project_path(settings["raw_data"]["orders"])
    orders = pd.read_csv(orders_path)
    new_order = orders.iloc[0].copy()
    new_order["order_id"] = "O-99999"
    orders = pd.concat([orders, pd.DataFrame([new_order])], ignore_index=True)
    orders.to_csv(orders_path, index=False)

    with closing(sqlite3.connect(database_path)) as connection:
        before_count = pd.read_sql_query("SELECT COUNT(*) AS count FROM orders", connection).loc[0, "count"]

    run_pipeline(mode="incremental")

    with closing(sqlite3.connect(database_path)) as connection:
        after_count = pd.read_sql_query("SELECT COUNT(*) AS count FROM orders", connection).loc[0, "count"]
        loaded_rows = pd.read_sql_query(
            "SELECT loaded_rows FROM pipeline_runs ORDER BY started_at_utc DESC LIMIT 1",
            connection,
        ).loc[0, "loaded_rows"]

    assert after_count == before_count + 1
    assert loaded_rows == 1
