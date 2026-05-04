from __future__ import annotations

from pathlib import Path

import pandas as pd

from pipeline.config import ensure_parent


def build_quality_summary(
    raw_counts: dict[str, int],
    clean_counts: dict[str, int],
    issues: pd.DataFrame,
) -> pd.DataFrame:
    rows = []
    for table_name, raw_count in raw_counts.items():
        issue_count = int((issues["table_name"] == table_name).sum()) if not issues.empty else 0
        clean_count = clean_counts[table_name]
        rows.append(
            {
                "table_name": table_name,
                "raw_rows": raw_count,
                "clean_rows": clean_count,
                "removed_or_flagged_rows": raw_count - clean_count,
                "validation_issues": issue_count,
                "clean_rate": round(clean_count / raw_count, 4) if raw_count else 0,
            }
        )
    return pd.DataFrame(rows)


def write_quality_report(summary: pd.DataFrame, issues: pd.DataFrame, output_path: Path) -> None:
    ensure_parent(output_path)
    issue_breakdown = (
        issues.groupby(["table_name", "issue_type"]).size().reset_index(name="issue_count")
        if not issues.empty
        else pd.DataFrame(columns=["table_name", "issue_type", "issue_count"])
    )

    lines = [
        "# Data Quality Report",
        "",
        "This report summarizes the validation checks applied during the retail KPI pipeline run.",
        "",
        "## Row Summary",
        "",
        summary.to_markdown(index=False),
        "",
        "## Issue Breakdown",
        "",
        issue_breakdown.to_markdown(index=False),
        "",
        "## Interpretation",
        "",
        "- Rows can be removed when they fail business rules such as invalid quantities, missing dimension links, or invalid dates.",
        "- The pipeline keeps issue details in `data_quality_issues.csv` so analysts can review rejected records.",
        "- A clean rate below 100% is intentional in this project because the raw exports simulate real operational data quality problems.",
        "",
    ]
    output_path.write_text("\n".join(lines), encoding="utf-8")
