"""Publish registered domain events to RabbitMQ (maturity path beyond outbox log)."""

from __future__ import annotations

import json
import logging
from typing import Any
from uuid import UUID

logger = logging.getLogger(__name__)


def publish_domain_event(
    *,
    event_type: str,
    tenant_id: UUID,
    aggregate_type: str,
    aggregate_id: UUID,
    payload: dict[str, Any],
) -> bool:
    """Best-effort publish to RabbitMQ exchange `erp.domain.events`.

    Returns True when published; False when broker unavailable (outbox already
    persisted the event for retry).
    """
    body = {
        "event_type": event_type,
        "tenant_id": str(tenant_id),
        "aggregate_type": aggregate_type,
        "aggregate_id": str(aggregate_id),
        "payload": payload,
    }
    try:
        from core.config import settings
        from kombu import Connection, Exchange, Producer

        exchange = Exchange("erp.domain.events", type="topic", durable=True)
        with Connection(settings.celery_broker_url) as conn:
            producer = Producer(conn)
            producer.publish(
                json.dumps(body),
                exchange=exchange,
                routing_key=event_type,
                content_type="application/json",
                declare=[exchange],
                retry=True,
            )
        return True
    except Exception:
        logger.exception("Failed to publish domain event %s", event_type)
        return False
