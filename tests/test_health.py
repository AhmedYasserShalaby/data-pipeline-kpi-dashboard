import pandas as pd
import pytest

from pipeline.bootstrap import ensure_demo_outputs
from pipeline.generate_data import generate_all
from pipeline.health import missing_exports, required_export_paths, verify_pipeline_outputs
from pipeline.run import run_pipeline


def test_dashboard_bootstrap_generates_missing_exports():
    for path in required_export_paths().values():
        path.unlink(missing_ok=True)

    assert missing_exports()
    generated = ensure_demo_outputs()

    assert generated is True
    assert not missing_exports()
    assert verify_pipeline_outputs() == []


def test_health_checks_detect_kpi_total_mismatch():
    generate_all()
    run_pipeline(mode="full")
    overview_path = required_export_paths()["executive_overview"]
    overview = pd.read_csv(overview_path)
    overview.loc[0, "total_revenue"] = 1
    try:
        overview.to_csv(overview_path, index=False)
        failures = verify_pipeline_outputs()
        assert "Executive overview revenue does not match SQLite orders" in failures
    finally:
        run_pipeline(mode="full")


def test_bootstrap_fails_when_quality_threshold_is_too_high(monkeypatch):
    from pipeline import health

    generate_all()
    run_pipeline(mode="full")

    settings = health.load_settings()
    settings["quality"]["minimum_quality_score"] = 0.99
    monkeypatch.setattr(health, "load_settings", lambda: settings)

    with pytest.raises(RuntimeError, match="quality score"):
        health.assert_pipeline_outputs()
