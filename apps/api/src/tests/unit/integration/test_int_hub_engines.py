"""Unit tests for Integration Hub engines."""

from types import SimpleNamespace

from modules.integration.service.engines import (
    ConnectorEngine,
    DeadLetterEngine,
    SyncJobEngine,
    WebhookEngine,
)


def test_connector_lifecycle():
    row = SimpleNamespace(status="draft")
    eng = ConnectorEngine()
    eng.submit(row)
    assert row.status == "submitted"
    eng.approve(row)
    assert row.status == "approved"


def test_webhook_lifecycle():
    row = SimpleNamespace(status="draft", is_enabled=False)
    eng = WebhookEngine()
    eng.submit(row)
    eng.approve(row)
    eng.activate(row)
    assert row.status == "active"
    assert row.is_enabled is True


def test_sync_job_lifecycle_and_run():
    row = SimpleNamespace(status="draft")
    eng = SyncJobEngine()
    eng.submit(row)
    eng.approve(row)
    eng.run(row)
    assert row.status == "running"


def test_dead_letter_reprocess():
    row = SimpleNamespace(status="open")
    eng = DeadLetterEngine()
    eng.reprocess(row)
    assert row.status == "reprocessed"
