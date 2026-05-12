import os
import subprocess
import sys

from pipeline.generate_data import generate_all
from pipeline.cli import main


def test_validate_contracts_cli_reports_expected_issues():
    generate_all()
    environment = os.environ.copy()
    environment["PYTHONPATH"] = "src"

    result = subprocess.run(
        [sys.executable, "-m", "pipeline.cli", "validate-contracts"],
        check=True,
        capture_output=True,
        env=environment,
        text=True,
    )

    assert "Validated 4 raw tables" in result.stdout
    assert "Contract issues found:" in result.stdout
    assert "duplicate_key" in result.stdout


def test_cli_main_runs_pipeline_and_exports_kpis(monkeypatch, capsys):
    monkeypatch.setattr("sys.argv", ["retail-kpi", "generate-data"])
    main()
    assert "Generated raw files" in capsys.readouterr().out

    monkeypatch.setattr("sys.argv", ["retail-kpi", "run-pipeline", "--mode", "full"])
    main()
    assert "Run summary" in capsys.readouterr().out

    monkeypatch.setattr("sys.argv", ["retail-kpi", "run-kpis"])
    main()
    assert "Exported KPI files" in capsys.readouterr().out

    monkeypatch.setattr("sys.argv", ["retail-kpi", "validate-contracts"])
    main()
    assert "Contract issues found" in capsys.readouterr().out
