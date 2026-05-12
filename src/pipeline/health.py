from __future__ import annotations

import sqlite3
from contextlib import closing
from pathlib import Path
from typing import Any

import pandas as pd

from pipeline.config import load_settings, project_path


def required_export_paths(settings: dict[str, Any] | None = None) -> dict[str, Path]:
    settings = settings or load_settings()
    return {name: project_path(path) for name, path in settings["exports"].items() if name != "directory"}


def missing_exports(settings: dict[str, Any] | None = None) -> list[Path]:
    return [path for path in required_export_paths(settings).values() if not path.exists()]


def verify_pipeline_outputs(settings: dict[str, Any] | None = None) -> list[str]:
    settings = settings or load_settings()
    failures = []
    failures.extend(f"Missing export: {path}" for path in missing_exports(settings))
    failures.extend(_quality_failures(settings))
    failures.extend(_kpi_total_failures(settings))
    return failures


def assert_pipeline_outputs(settings: dict[str, Any] | None = None) -> None:
    failures = verify_pipeline_outputs(settings)
    if failures:
        raise RuntimeError("Pipeline health checks failed:\n- " + "\n- ".join(failures))


def _quality_failures(settings: dict[str, Any]) -> list[str]:
    quality_path = project_path(settings["exports"]["data_quality_summary"])
    if not quality_path.exists():
        return []
    quality = pd.read_csv(quality_path)
    threshold = float(settings.get("quality", {}).get("minimum_quality_score", 0.9))
    low_quality = quality[quality["quality_score"] < threshold]
    return [
        f"{row.table_name} quality score {row.quality_score:.2%} below {threshold:.0%}"
        for row in low_quality.itertuples(index=False)
    ]


def _kpi_total_failures(settings: dict[str, Any]) -> list[str]:
    overview_path = project_path(settings["exports"]["executive_overview"])
    database_path = project_path(settings["database"]["path"])
    if not overview_path.exists() or not database_path.exists():
        return []
    overview = pd.read_csv(overview_path).iloc[0]
    with closing(sqlite3.connect(database_path)) as connection:
        database_totals = pd.read_sql_query(
            """
            SELECT
                ROUND(SUM(revenue), 2) AS total_revenue,
                COUNT(DISTINCT order_id) AS total_orders
            FROM orders
            """,
            connection,
        ).iloc[0]
    failures = []
    if round(float(overview["total_revenue"]), 2) != round(float(database_totals["total_revenue"]), 2):
        failures.append("Executive overview revenue does not match SQLite orders")
    if int(overview["total_orders"]) != int(database_totals["total_orders"]):
        failures.append("Executive overview order count does not match SQLite orders")
    return failures
