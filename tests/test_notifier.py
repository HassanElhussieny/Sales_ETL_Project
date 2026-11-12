"""main/notifier.py: email content and sending, without any network access."""
import importlib
import sys

import pytest


@pytest.fixture
def notifier(monkeypatch, tmp_path):
    for var in ("EMAIL_SENDER", "EMAIL_PASSWORD", "EMAIL_RECEIVER"):
        monkeypatch.delenv(var, raising=False)
    # Write test logs to a temp folder, not the project's logs/.
    settings = importlib.import_module("config.settings")
    monkeypatch.setattr(settings, "LOGS_DIR", tmp_path)
    monkeypatch.setattr(settings, "LOG_FILE", tmp_path / "pipeline.log")
    for name in ("main.logger", "main.notifier"):
        monkeypatch.delitem(sys.modules, name, raising=False)
    module = importlib.import_module("main.notifier")

    sent = []
    module.real_send_email = module._send_email
    monkeypatch.setattr(module, "_send_email", lambda subject, body: sent.append((subject, body)) or True)
    module.sent = sent
    return module


def test_failure_email_is_actually_sent(notifier):
    notifier.notify_failure("Traceback: boom")
    assert len(notifier.sent) == 1
    subject, body = notifier.sent[0]
    assert "FAILED" in subject
    assert "Traceback: boom" in body


def test_failure_email_points_to_the_real_log_file(notifier):
    notifier.notify_failure("x")
    _, body = notifier.sent[0]
    assert str(notifier.LOG_FILE) in body
    assert "Data_Analytics_project" not in body


def test_success_email_is_sent(notifier):
    notifier.notify_success(rows_extracted=10, rows_loaded=9, rows_dropped=1, total_time=0.5)
    assert len(notifier.sent) == 1
    assert "Completed Successfully" in notifier.sent[0][0]


def test_missing_credentials_skip_sending_without_network(notifier, monkeypatch):
    module = notifier
    monkeypatch.setattr(module, "EMAIL_SENDER", "")
    monkeypatch.setattr(module, "EMAIL_PASSWORD", "")
    monkeypatch.setattr(module, "EMAIL_RECEIVER", "")

    def no_network(*args, **kwargs):
        raise AssertionError("SMTP must not be contacted without credentials")

    monkeypatch.setattr(module.smtplib, "SMTP", no_network)
    assert module.real_send_email("subject", "body") is False
