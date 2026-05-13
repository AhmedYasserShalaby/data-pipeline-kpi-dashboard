from __future__ import annotations

import argparse

import pandas as pd

from pipeline.config import load_settings, project_path
from pipeline.contracts import load_contracts, validate_contracts
from pipeline.diagnostics import diagnose_current_outputs
from pipeline.generate_data import generate_all
from pipeline.kpis import export_kpis
from pipeline.lineage import write_lineage
from pipeline.models import build_analytics_models
from pipeline.run import run_pipeline


def main() -> None:
    parser = argparse.ArgumentParser(description="Retail KPI data pipeline")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("generate-data", help="Generate synthetic raw retail CSV files")
    run_parser = subparsers.add_parser("run-pipeline", help="Clean raw data, load SQLite, and export dashboard files")
    run_parser.add_argument("--mode", choices=["full", "incremental"], default="full", help="Load mode")
    subparsers.add_parser("run-kpis", help="Re-export KPI CSVs from the current SQLite database")
    subparsers.add_parser("run-models", help="Build dbt-style staging, intermediate, and mart views")
    subparsers.add_parser("diagnose-quality", help="Write root-cause and remediation report from quality outputs")
    subparsers.add_parser("export-lineage", help="Write data lineage documentation")
    subparsers.add_parser("validate-contracts", help="Validate raw files against YAML data contracts")
    args = parser.parse_args()

    if args.command == "generate-data":
        outputs = generate_all()
        print("Generated raw files:")
        for name, path in outputs.items():
            print(f"- {name}: {path}")
    elif args.command == "run-pipeline":
        outputs = run_pipeline(mode=args.mode)
        print(f"SQLite database: {outputs['database']}")
        print(f"Dashboard exports: {outputs['exports']}")
        print("Data quality report: docs/data_quality_report.md")
        print("Run summary: docs/run_summary.md")
    elif args.command == "run-kpis":
        settings = load_settings()
        database_path = project_path(settings["database"]["path"])
        exports = {name: project_path(path) for name, path in settings["exports"].items() if name != "directory"}
        outputs = export_kpis(database_path, exports)
        print("Exported KPI files:")
        for name in outputs:
            print(f"- {name}")
    elif args.command == "run-models":
        row_counts = build_analytics_models()
        print("Built analytics model views:")
        for name, row_count in row_counts.items():
            print(f"- {name}: {row_count} rows")
    elif args.command == "diagnose-quality":
        output_path = diagnose_current_outputs()
        print(f"Quality diagnosis: {output_path}")
    elif args.command == "export-lineage":
        output_path = write_lineage()
        print(f"Lineage doc: {output_path}")
    elif args.command == "validate-contracts":
        settings = load_settings()
        raw_tables = {name: pd.read_csv(project_path(path)) for name, path in settings["raw_data"].items()}
        contracts = load_contracts(project_path(settings["validation"]["contracts"]))
        issues = validate_contracts(raw_tables, contracts)
        print(f"Validated {len(raw_tables)} raw tables against {len(contracts)} data contracts.")
        print(f"Contract issues found: {len(issues)}")
        if not issues.empty:
            issue_counts = issues.groupby(["table_name", "issue_type"]).size().reset_index(name="issue_count")
            print(issue_counts.to_string(index=False))


if __name__ == "__main__":
    main()
