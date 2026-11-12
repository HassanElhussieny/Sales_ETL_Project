"""Shared test setup.

Tests never touch PostgreSQL, Gmail or the real data folder: the ETL steps
and notifier are replaced with in-memory fakes.
"""
import importlib.util
import logging
import sys
import types
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# config/settings.py imports python-dotenv. If it is not installed in the
# test environment, provide a no-op stand-in so settings can be imported.
# It also guarantees no real config/.env credentials are loaded in tests.
if importlib.util.find_spec("dotenv") is None:
    sys.modules["dotenv"] = types.SimpleNamespace(load_dotenv=lambda **kwargs: None)


class FakeFrame:
    """Minimal stand-in for a pandas DataFrame (only len() and .empty are used)."""

    def __init__(self, rows: int):
        self.rows = rows

    def __len__(self):
        return self.rows

    @property
    def empty(self):
        return self.rows == 0


class FakeETL:
    """Configurable fake ETL steps plus a record of notifier calls."""

    def __init__(self):
        self.extract_result = FakeFrame(10)
        self.transform_result = FakeFrame(9)
        self.load_result = True
        self.extract_error = None
        self.notify_failure_error = None
        self.success_calls = []
        self.failure_calls = []

    def extract_all(self):
        if self.extract_error:
            raise self.extract_error
        return self.extract_result

    def transform(self, df):
        return self.transform_result

    def load(self, df):
        return self.load_result

    def notify_success(self, **kwargs):
        self.success_calls.append(kwargs)

    def notify_failure(self, error_message):
        self.failure_calls.append(error_message)
        if self.notify_failure_error:
            raise self.notify_failure_error


@pytest.fixture
def fake_etl(monkeypatch):
    """Install fake main.* modules so scripts/pipeline.py runs fully offline."""
    etl = FakeETL()

    def module(name, **attrs):
        mod = types.ModuleType(name)
        mod.__dict__.update(attrs)
        monkeypatch.setitem(sys.modules, name, mod)

    module("main.extract", extract_all=lambda: etl.extract_all())
    module("main.transform", transform=lambda df: etl.transform(df))
    module("main.load", load=lambda df: etl.load(df))
    module("main.logger", get_logger=logging.getLogger)
    module(
        "main.notifier",
        notify_success=lambda **kw: etl.notify_success(**kw),
        notify_failure=lambda msg: etl.notify_failure(msg),
    )
    # Force a fresh import of the pipeline against the fakes.
    monkeypatch.delitem(sys.modules, "scripts.pipeline", raising=False)
    return etl
