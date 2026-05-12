from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from pipeline.config import ensure_parent
from pipeline.markdown import dataframe_to_markdown


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def build_run_summary(
    mode: str,
    started_at: datetime,
    finished_at: datetime,
    raw_counts: dict[str, int],
    clean_counts: dict[str, int],
    loaded_counts: dict[str, int],
    issues: pd.DataFrame,
    exports_directory: Path,
) -> dict[str, Any]:
    run_id = started_at.strftime("%Y%m%dT%H%M%S%fZ")
    rows_read = sum(raw_counts.values())
    rows_cleaned = sum(clean_counts.values())
    return {
        "run_id": run_id,
        "mode": mode,
        "started_at_utc": started_at.isoformat(),
        "finished_at_utc": finished_at.isoformat(),
        "duration_seconds": round((finished_at - started_at).total_seconds(), 3),
        "status": "success",
        "rows_read": rows_read,
        "rows_cleaned": rows_cleaned,
        "rows_rejected": rows_read - rows_cleaned,
        "validation_issues": len(issues),
        "loaded_rows": sum(loaded_counts.values()),
        "exports_directory": str(exports_directory),
    }


def write_run_summary(
    summary: dict[str, Any],
    table_counts: pd.DataFrame,
    export_path: Path,
    docs_path: Path,
) -> None:
    ensure_parent(export_path)
    pd.DataFrame([summary]).to_csv(export_path, index=False)
    ensure_parent(docs_path)
    lines = [
        "# Pipeline Run Summary",
        "",
        f"Run ID: `{summary['run_id']}`",
        f"Mode: `{summary['mode']}`",
        f"Status: `{summary['status']}`",
        f"Started UTC: `{summary['started_at_utc']}`",
        f"Finished UTC: `{summary['finished_at_utc']}`",
        f"Duration seconds: `{summary['duration_seconds']}`",
        "",
        "## Run Totals",
        "",
        dataframe_to_markdown(pd.DataFrame([summary])),
        "",
        "## Table Counts",
        "",
        dataframe_to_markdown(table_counts),
        "",
        "## Output",
        "",
        f"- Dashboard exports: `{summary['exports_directory']}`",
        "- Quality report: `docs/data_quality_report.md`",
        "- Latest run summary CSV: `data/processed/dashboard_exports/pipeline_run_summary.csv`",
        "",
    ]
    docs_path.write_text("\n".join(lines), encoding="utf-8")


def build_table_counts(
    raw_counts: dict[str, int], clean_counts: dict[str, int], loaded_counts: dict[str, int]
) -> pd.DataFrame:
    rows = []
    for table_name, raw_count in raw_counts.items():
        rows.append(
            {
                "table_name": table_name,
                "raw_rows": raw_count,
                "clean_rows": clean_counts[table_name],
                "rejected_rows": raw_count - clean_counts[table_name],
                "loaded_rows": loaded_counts.get(table_name, 0),
            }
        )
    return pd.DataFrame(rows)
