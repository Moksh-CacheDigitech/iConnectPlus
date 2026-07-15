"""Unit tests for Integration Hub Celery task names."""

from modules.integration import tasks


def test_integration_task_names_registered():
    assert tasks.retry_processor.name == "integration.retry_processor"
    assert tasks.dead_letter_reprocessor.name == "integration.dead_letter_reprocessor"
    assert tasks.webhook_dispatcher.name == "integration.webhook_dispatcher"
    assert tasks.sync_scheduler.name == "integration.sync_scheduler"
    assert tasks.rate_limit_enforcer.name == "integration.rate_limit_enforcer"
    assert tasks.message_queue_poller.name == "integration.message_queue_poller"
