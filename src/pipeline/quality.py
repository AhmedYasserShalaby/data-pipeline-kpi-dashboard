from __future__ import annotations

from pathlib import Path

import pandas as pd

from pipeline.config import ensure_parent
from pipeline.markdown import dataframe_to_markdown

ISSUE_COLUMNS = ["table_name", "issue_type", "row_reference", "column_name", "issue_detail", "issue_source"]


def normalize_issues(issues: pd.DataFrame, source: str) -> pd.DataFrame:
    frame = issues.copy()
    for column in ISSUE_COLUMNS:
        if column not in frame.columns:
            frame[column] = ""
    frame["issue_source"] = frame["issue_source"].replace("", source)
    return frame[ISSUE_COLUMNS]


def build_quality_summary(
    raw_counts: dict[str, int],
    clean_counts: dict[str, int],
    issues: pd.DataFrame,
) -> pd.DataFrame:
    rows = []
    for table_name, raw_count in raw_counts.items():
        issue_count = int((issues["table_name"] == table_name).sum()) if not issues.empty else 0
        clean_count = clean_counts[table_name]
        rejected_rows = raw_count - clean_count
        issue_rate = round(issue_count / raw_count, 4) if raw_count else 0
        rows.append(
            {
                "table_name": table_name,
                "raw_rows": raw_count,
                "clean_rows": clean_count,
                "rejected_rows": rejected_rows,
                "removed_or_flagged_rows": rejected_rows,
                "validation_issues": issue_count,
                "clean_rate": round(clean_count / raw_count, 4) if raw_count else 0,
                "issue_rate": issue_rate,
                "quality_score": round(max(0, 1 - issue_rate), 4),
            }
        )
    return pd.DataFrame(rows)


def write_quality_report(summary: pd.DataFrame, issues: pd.DataFrame, output_path: Path) -> None:
    ensure_parent(output_path)
    issue_breakdown = (
        issues.groupby(["table_name", "issue_source", "issue_type", "column_name"])
        .size()
        .reset_index(name="issue_count")
        if not issues.empty
        else pd.DataFrame(columns=["table_name", "issue_source", "issue_type", "column_name", "issue_count"])
    )
    overall_score = round(summary["quality_score"].mean() * 100, 1) if not summary.empty else 0

    lines = [
        "# Data Quality Report",
        "",
        "This report summarizes the validation checks applied during the retail KPI pipeline run.",
        "",
        f"Overall quality score: **{overall_score}%**",
        "",
        "## Row Summary",
        "",
        dataframe_to_markdown(summary),
        "",
        "## Issue Breakdown",
        "",
        dataframe_to_markdown(issue_breakdown),
        "",
        "## Interpretation",
        "",
        "- Contract issues come from YAML rules for schema, IDs, ranges, dates, allowed values, duplicate keys, and foreign keys.",
        "- Cleaning issues are rejected rows removed before loading trusted warehouse tables.",
        "- The pipeline keeps rejected-row details in `data_quality_issues.csv` so analysts can review data quality failures.",
        "- A clean rate below 100% is intentional because the raw exports simulate real operational data quality problems.",
        "",
    ]
    output_path.write_text("\n".join(lines), encoding="utf-8")
