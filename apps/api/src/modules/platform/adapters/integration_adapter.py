"""IIntegrationGateway — enqueue outbound work via outbox (Hub seam)."""

from __future__ import annotations

import logging
from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from modules.platform.outbox.service import OutboxService

logger = logging.getLogger(__name__)


class IntegrationGatewayAdapter:
    """External I/O must enter through this gateway (C-03)."""

    def __init__(self, db: Session) -> None:
        self._db = db
        self._outbox = OutboxService(db)

    def dispatch_outbound(
        self,
        *,
        tenant_id: UUID,
        system_code: str,
        operation: str,
        payload: dict[str, Any],
        idempotency_key: str,
    ) -> dict[str, Any]:
        # When called from outbox dispatcher, execute; when called from domain,
        # enqueue to avoid coupling domain to external latency.
        if payload.get("_execute") is True:
            return self._execute(
                tenant_id=tenant_id,
                system_code=system_code,
                operation=operation,
                payload=payload,
                idempotency_key=idempotency_key,
            )

        message_id = self._outbox.enqueue(
            tenant_id=tenant_id,
            event_type="integration.dispatch",
            aggregate_type="integration",
            aggregate_id=tenant_id,
            payload={
                "system_code": system_code,
                "operation": operation,
                "payload": {**payload, "_execute": True},
                "idempotency_key": idempotency_key,
            },
            idempotency_key=idempotency_key,
        )
        return {"status": "queued", "outbox_id": str(message_id)}

    def _execute(
        self,
        *,
        tenant_id: UUID,
        system_code: str,
        operation: str,
        payload: dict[str, Any],
        idempotency_key: str,
    ) -> dict[str, Any]:
        """Execute via built-in connector adapters (Integration Hub module removed)."""
        from modules.platform.connectors.registry import execute_connector

        return execute_connector(
            system_code=system_code,
            operation=operation,
            payload=payload,
            tenant_id=tenant_id,
            idempotency_key=idempotency_key,
        )
