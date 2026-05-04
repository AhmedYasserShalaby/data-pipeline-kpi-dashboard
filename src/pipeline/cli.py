from __future__ import annotations

import argparse

from pipeline.generate_data import generate_all
from pipeline.kpis import export_kpis
from pipeline.config import load_settings, project_path
from pipeline.run import run_pipeline


def main() -> None:
    parser = argparse.ArgumentParser(description="Retail KPI data pipeline")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("generate-data", help="Generate synthetic raw retail CSV files")
    subparsers.add_parser("run-pipeline", help="Clean raw data, load SQLite, and export dashboard files")
    subparsers.add_parser("run-kpis", help="Re-export KPI CSVs from the current SQLite database")
    args = parser.parse_args()

    if args.command == "generate-data":
        outputs = generate_all()
        print("Generated raw files:")
        for name, path in outputs.items():
            print(f"- {name}: {path}")
    elif args.command == "run-pipeline":
        outputs = run_pipeline()
        print(f"SQLite database: {outputs['database']}")
        print(f"Dashboard exports: {outputs['exports']}")
        print("Data quality report: docs/data_quality_report.md")
    elif args.command == "run-kpis":
        settings = load_settings()
        database_path = project_path(settings["database"]["path"])
        exports = {name: project_path(path) for name, path in settings["exports"].items() if name != "directory"}
        outputs = export_kpis(database_path, exports)
        print("Exported KPI files:")
        for name in outputs:
            print(f"- {name}")


if __name__ == "__main__":
    main()
