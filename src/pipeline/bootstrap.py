from __future__ import annotations

from pipeline.generate_data import generate_all
from pipeline.health import assert_pipeline_outputs, missing_exports
from pipeline.run import run_pipeline


def ensure_demo_outputs() -> bool:
    if not missing_exports():
        assert_pipeline_outputs()
        return False
    generate_all()
    run_pipeline(mode="full")
    assert_pipeline_outputs()
    return True
