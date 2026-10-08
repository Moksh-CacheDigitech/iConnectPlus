"""Unit tests for outbox enqueue idempotency (no DB — repository mocked)."""

from __future__ import annotations

from unittest.mock import MagicMock
from uuid import uuid4

from modules.platform.outbox.service import OutboxService


def test_outbox_enqueue_returns_message_id() -> None:
    repo = MagicMock()
    msg = MagicMock()
    msg.id = uuid4()
    repo.enqueue.return_value = msg

    svc = OutboxService(MagicMock())
    svc._repo = repo  # noqa: SLF001 — unit seam

    tenant = uuid4()
    aggregate = uuid4()
    result = svc.enqueue(
        tenant_id=tenant,
        event_type="notify.order",
        aggregate_type="sales_order",
        aggregate_id=aggregate,
        payload={"x": 1},
        idempotency_key="k1",
    )
    assert result == msg.id
    repo.enqueue.assert_called_once()


def test_get_platform_ports_builds_all_seams() -> None:
    from modules.platform.container import get_platform_ports

    db = MagicMock()
    ports = get_platform_ports(db)
    assert ports.finance is not None
    assert ports.inventory is not None
    assert ports.master_data is not None
    assert ports.workflow is not None
    assert ports.notify is not None
    assert ports.audit is not None
    assert ports.numbering is not None
    assert ports.outbox is not None
    assert ports.integration is not None
