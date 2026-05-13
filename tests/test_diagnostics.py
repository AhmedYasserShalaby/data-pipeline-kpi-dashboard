from pathlib import Path

from pipeline.generate_data import generate_all
from pipeline.run import run_pipeline


def test_pipeline_writes_quality_diagnosis_and_lineage_docs():
    generate_all()
    run_pipeline(mode="full")

    diagnosis = Path("docs/quality_diagnosis.md")
    lineage = Path("docs/lineage.md")

    assert diagnosis.exists()
    assert "Remediation Backlog" in diagnosis.read_text(encoding="utf-8")
    assert "missing_foreign_key" in diagnosis.read_text(encoding="utf-8")
    assert lineage.exists()
    assert "flowchart LR" in lineage.read_text(encoding="utf-8")
