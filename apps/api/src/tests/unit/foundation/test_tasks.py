"""Unit tests for Celery foundation tasks."""

from modules.foundation.tasks import workflow_escalation_stub


def test_workflow_escalation_stub() -> None:
    result = workflow_escalation_stub()
    assert result["status"] == "stub"
    assert result["escalated"] == 0
