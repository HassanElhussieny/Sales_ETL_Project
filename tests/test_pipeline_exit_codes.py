"""Exit codes of scripts/pipeline.py (what Windows Task Scheduler sees)."""
import importlib
import logging
import runpy

import pytest

from conftest import PROJECT_ROOT, FakeFrame

PIPELINE_SCRIPT = PROJECT_ROOT / "scripts" / "pipeline.py"


def run_as_script():
    """Run pipeline.py exactly like `python scripts\\pipeline.py`; return its exit code."""
    with pytest.raises(SystemExit) as exit_info:
        runpy.run_path(str(PIPELINE_SCRIPT), run_name="__main__")
    return exit_info.value.code


# ── success ─────────────────────────────────────────────────

def test_success_exits_with_zero(fake_etl):
    assert run_as_script() == 0
    assert len(fake_etl.success_calls) == 1
    assert fake_etl.failure_calls == []


def test_main_returns_zero_on_success(fake_etl):
    pipeline = importlib.import_module("scripts.pipeline")
    assert pipeline.main() == 0


# ── failures handled inside run_pipeline ────────────────────

def test_load_failure_exits_non_zero(fake_etl):
    fake_etl.load_result = False
    assert run_as_script() != 0
    assert len(fake_etl.failure_calls) == 1
    assert "Load to PostgreSQL failed" in fake_etl.failure_calls[0]
    assert fake_etl.success_calls == []


def test_empty_extract_exits_non_zero(fake_etl):
    fake_etl.extract_result = FakeFrame(0)
    assert run_as_script() != 0
    assert "No data extracted" in fake_etl.failure_calls[0]


def test_empty_transform_exits_non_zero(fake_etl):
    fake_etl.transform_result = FakeFrame(0)
    assert run_as_script() != 0
    assert "No rows survived transformation" in fake_etl.failure_calls[0]


def test_exception_is_logged_and_reported_not_hidden(fake_etl, caplog):
    fake_etl.extract_error = RuntimeError("database unreachable")
    with caplog.at_level(logging.ERROR):
        assert run_as_script() != 0
    # The failure email receives the full traceback...
    assert "RuntimeError: database unreachable" in fake_etl.failure_calls[0]
    assert "Traceback" in fake_etl.failure_calls[0]
    # ...and the existing error log lines are still written.
    assert "ETL PIPELINE FAILED" in caplog.text
    assert "database unreachable" in caplog.text


# ── exceptions outside run_pipeline's handler ───────────────

def test_exception_in_failure_handler_propagates(fake_etl):
    """If even the failure notification crashes, the error must surface
    (Python then exits non-zero with a traceback) instead of being swallowed."""
    fake_etl.extract_error = RuntimeError("extract broke")
    fake_etl.notify_failure_error = OSError("notifier broke")
    with pytest.raises(OSError, match="notifier broke"):
        runpy.run_path(str(PIPELINE_SCRIPT), run_name="__main__")
