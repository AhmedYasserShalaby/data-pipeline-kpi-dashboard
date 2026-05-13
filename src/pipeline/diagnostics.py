from __future__ import annotations

from pathlib import Path

import pandas as pd

from pipeline.config import ensure_parent, load_settings, project_path
from pipeline.markdown import dataframe_to_markdown
from pipeline.paths import PROJECT_ROOT


DIAGNOSIS_RULES = {
    "duplicate_key": {
        "severity": "Medium",
        "root_cause": "Source system or export process produced repeated business keys.",
        "remediation": "Deduplicate upstream exports, enforce unique constraints, and keep latest-record rules explicit.",
    },
    "missing_foreign_key": {
        "severity": "High",
        "root_cause": "Fact rows reference dimension records that are absent from the trusted dimension export.",
        "remediation": "Add referential-integrity checks before load and quarantine orphaned records for source-owner review.",
    },
    "numeric_below_min": {
        "severity": "High",
        "root_cause": "Operational values violated accepted business ranges.",
        "remediation": "Validate entry rules at source and block negative/zero quantities before analytics ingestion.",
    },
    "invalid_order_or_missing_dimension": {
        "severity": "High",
        "root_cause": "Order rows were not safe to load because key quantity or dimension checks failed.",
        "remediation": "Keep rejected rows visible, reconcile with order source owners, and reload corrected records incrementally.",
    },
    "invalid_return_or_missing_order": {
        "severity": "Medium",
        "root_cause": "Return records could not be matched to valid loaded orders.",
        "remediation": "Validate return/order relationships before finance reporting and investigate missing order references.",
    },
}


def build_quality_diagnosis(summary: pd.DataFrame, issues: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    if issues.empty:
        empty = pd.DataFrame(
            columns=["severity", "table_name", "issue_type", "issue_count", "root_cause", "remediation"]
        )
        return empty, empty

    grouped = issues.groupby(["table_name", "issue_type"]).size().reset_index(name="issue_count")
    rows = []
    for row in grouped.itertuples(index=False):
        rule = DIAGNOSIS_RULES.get(
            row.issue_type,
            {
                "severity": "Medium",
                "root_cause": "Data failed a configured validation or cleaning rule.",
                "remediation": "Review rejected-row sample and decide whether to correct, backfill, or update the contract.",
            },
        )
        rows.append(
            {
                "severity": rule["severity"],
                "table_name": row.table_name,
                "issue_type": row.issue_type,
                "issue_count": int(row.issue_count),
                "root_cause": rule["root_cause"],
                "remediation": rule["remediation"],
            }
        )
    diagnosis = pd.DataFrame(rows).sort_values(["severity", "issue_count"], ascending=[True, False])
    backlog = _build_remediation_backlog(summary, diagnosis)
    return diagnosis, backlog


def write_quality_diagnosis(
    summary: pd.DataFrame,
    issues: pd.DataFrame,
    output_path: Path = PROJECT_ROOT / "docs" / "quality_diagnosis.md",
) -> None:
    ensure_parent(output_path)
    diagnosis, backlog = build_quality_diagnosis(summary, issues)
    highest_risk_table = _highest_risk_table(summary)
    total_issues = int(len(issues))

    lines = [
        "# Quality Diagnosis And Remediation Plan",
        "",
        "This report translates validation failures into operational diagnosis and remediation actions.",
        "",
        "## Executive Diagnosis",
        "",
        f"- Total issues detected: **{total_issues}**.",
        f"- Highest-risk table: **{highest_risk_table}**.",
        "- Main risk: dashboard KPIs can become misleading if invalid orders or orphaned facts are silently loaded.",
        "- Control response: quarantine rejected rows, reconcile with source owners, and reload corrected records incrementally.",
        "",
        "## Issue Diagnosis",
        "",
        dataframe_to_markdown(diagnosis),
        "",
        "## Remediation Backlog",
        "",
        dataframe_to_markdown(backlog),
        "",
        "## Interview Talking Point",
        "",
        "I did not stop at detecting bad data. I added a diagnosis layer that explains root causes, severity, and remediation actions so the pipeline behaves more like an operational data product.",
        "",
    ]
    output_path.write_text("\n".join(lines), encoding="utf-8")


def diagnose_current_outputs() -> Path:
    settings = load_settings()
    summary = pd.read_csv(project_path(settings["exports"]["data_quality_summary"]))
    issues = pd.read_csv(project_path(settings["exports"]["data_quality_issues"]))
    output_path = PROJECT_ROOT / "docs" / "quality_diagnosis.md"
    write_quality_diagnosis(summary, issues, output_path)
    return output_path


def _highest_risk_table(summary: pd.DataFrame) -> str:
    if summary.empty:
        return "none"
    row = summary.sort_values(["quality_score", "validation_issues"], ascending=[True, False]).iloc[0]
    return str(row["table_name"])


def _build_remediation_backlog(summary: pd.DataFrame, diagnosis: pd.DataFrame) -> pd.DataFrame:
    if diagnosis.empty:
        return pd.DataFrame(columns=["priority", "owner", "action", "success_check"])
    highest_risk_table = _highest_risk_table(summary)
    return pd.DataFrame(
        [
            {
                "priority": "P1",
                "owner": "Data engineering",
                "action": f"Block or quarantine invalid rows from `{highest_risk_table}` before KPI export.",
                "success_check": "No rejected rows enter trusted warehouse tables.",
            },
            {
                "priority": "P1",
                "owner": "Source system owner",
                "action": "Fix missing dimension references and invalid quantities in source exports.",
                "success_check": "Foreign-key and numeric-range issue counts trend down.",
            },
            {
                "priority": "P2",
                "owner": "Analytics engineering",
                "action": "Add KPI reconciliation checks to every dashboard-facing mart.",
                "success_check": "Warehouse totals equal dashboard export totals.",
            },
            {
                "priority": "P3",
                "owner": "Data governance",
                "action": "Review data contracts monthly and add new accepted-value or freshness checks.",
                "success_check": "Contracts stay aligned with real source-system behavior.",
            },
        ]
    )
