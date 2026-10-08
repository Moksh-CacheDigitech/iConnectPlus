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
        """Prefer built-in connector adapters; fall back to Integration Hub registry."""
        from modules.platform.connectors.registry import execute_connector

        built_in = execute_connector(
            system_code=system_code,
            operation=operation,
            payload=payload,
            tenant_id=tenant_id,
            idempotency_key=idempotency_key,
        )
        if built_in.get("status") == "executed":
            return built_in

        try:
            from modules.integration.service.external_system_service import ExternalSystemService

            match = None
            svc = ExternalSystemService(self._db)
            list_fn = getattr(svc, "list_systems", None) or getattr(svc, "list", None)
            systems = []
            if callable(list_fn):
                try:
                    systems = list_fn(tenant_id)  # type: ignore[misc]
                except TypeError:
                    systems = []
            for row in systems or []:
                code = getattr(row, "system_code", None) or getattr(row, "code", None)
                if code == system_code:
                    match = row
                    break

            logger.info(
                "integration.execute",
                extra={
                    "tenant_id": str(tenant_id),
                    "system_code": system_code,
                    "operation": operation,
                    "connector_found": match is not None,
                    "idempotency_key": idempotency_key,
                },
            )
            return {
                **built_in,
                "status": "executed" if match is not None else built_in.get("status"),
                "system_code": system_code,
                "operation": operation,
                "idempotency_key": idempotency_key,
                "connector_id": str(getattr(match, "id", "")) if match is not None else None,
                "request_payload_keys": sorted(k for k in payload.keys() if k != "_execute"),
            }
        except Exception as exc:
            logger.exception("Integration execute fallback")
            return {
                **built_in,
                "status": built_in.get("status") or "accepted",
                "system_code": system_code,
                "operation": operation,
                "idempotency_key": idempotency_key,
                "warning": str(exc),
            }
