from __future__ import annotations

from pathlib import Path

import pandas as pd

from pipeline.cleaning import clean_customers, clean_orders, clean_products, clean_returns
from pipeline.config import ensure_parent, load_settings, project_path
from pipeline.contracts import load_contracts, validate_contracts
from pipeline.diagnostics import write_quality_diagnosis
from pipeline.health import assert_pipeline_outputs
from pipeline.kpis import export_kpis
from pipeline.lineage import write_lineage
from pipeline.load import load_sqlite, record_pipeline_run
from pipeline.observability import build_run_summary, build_table_counts, utc_now, write_run_summary
from pipeline.paths import PROJECT_ROOT
from pipeline.quality import build_quality_summary, normalize_issues, write_quality_report


def run_pipeline(mode: str = "full") -> dict[str, Path]:
    if mode not in {"full", "incremental"}:
        raise ValueError("mode must be 'full' or 'incremental'")

    started_at = utc_now()
    settings = load_settings()

    raw_paths = {name: project_path(path) for name, path in settings["raw_data"].items()}
    processed_paths = {name: project_path(path) for name, path in settings["processed_data"].items()}
    database_path = project_path(settings["database"]["path"])
    schema_path = PROJECT_ROOT / "sql" / "schema.sql"
    export_paths = {name: project_path(path) for name, path in settings["exports"].items() if name != "directory"}
    exports_directory = project_path(settings["exports"]["directory"])
    exports_directory_label = Path(settings["exports"]["directory"])
    contracts = load_contracts(project_path(settings["validation"]["contracts"]))

    raw_customers = pd.read_csv(raw_paths["customers"])
    raw_products = pd.read_csv(raw_paths["products"])
    raw_orders = pd.read_csv(raw_paths["orders"])
    raw_returns = pd.read_csv(raw_paths["returns"])
    raw_tables = {
        "customers": raw_customers,
        "products": raw_products,
        "orders": raw_orders,
        "returns": raw_returns,
    }
    raw_counts = {
        "customers": len(raw_customers),
        "products": len(raw_products),
        "orders": len(raw_orders),
        "returns": len(raw_returns),
    }
    contract_issues = normalize_issues(validate_contracts(raw_tables, contracts), "contract")

    customers, customer_issues = clean_customers(raw_customers)
    products, product_issues = clean_products(raw_products)
    orders, order_issues = clean_orders(raw_orders, customers, products)
    returns, return_issues = clean_returns(raw_returns, orders)
    cleaning_issues = normalize_issues(
        pd.concat([customer_issues, product_issues, order_issues, return_issues], ignore_index=True),
        "cleaning",
    )
    issues = pd.concat([contract_issues, cleaning_issues], ignore_index=True)

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

    loaded_counts = load_sqlite(database_path, schema_path, tables, mode=mode)
    export_kpis(database_path, export_paths, issues)
    quality_summary = build_quality_summary(raw_counts, clean_counts, issues)
    quality_summary.to_csv(export_paths["data_quality_summary"], index=False)
    write_quality_report(quality_summary, issues, PROJECT_ROOT / "docs" / "data_quality_report.md")
    write_quality_diagnosis(quality_summary, issues)
    write_lineage()
    finished_at = utc_now()
    table_counts = build_table_counts(raw_counts, clean_counts, loaded_counts)
    run_summary = build_run_summary(
        mode,
        started_at,
        finished_at,
        raw_counts,
        clean_counts,
        loaded_counts,
        issues,
        exports_directory_label,
    )
    write_run_summary(
        run_summary, table_counts, export_paths["pipeline_run_summary"], PROJECT_ROOT / "docs" / "run_summary.md"
    )
    record_pipeline_run(database_path, run_summary)
    assert_pipeline_outputs(settings)
    return {
        "database": database_path,
        "exports": exports_directory,
        "run_summary": export_paths["pipeline_run_summary"],
    }
