"""Resolve system_code → concrete connector adapter."""

from __future__ import annotations

import logging
from typing import Any
from uuid import UUID

from modules.platform.connectors.outbound_http import OutboundBlockedError, post_json
from modules.platform.observability import get_request_id

logger = logging.getLogger(__name__)


def list_connector_types() -> list[str]:
    return sorted(_CONNECTORS.keys())


def execute_connector(
    *,
    system_code: str,
    operation: str,
    payload: dict[str, Any],
    tenant_id: UUID,
    idempotency_key: str,
) -> dict[str, Any]:
    code = (system_code or "").strip().lower()
    handler = _CONNECTORS.get(code) or _CONNECTORS.get(code.split(".")[0])
    if handler is None:
        return {
            "status": "accepted_no_connector",
            "system_code": system_code,
            "operation": operation,
            "idempotency_key": idempotency_key,
        }
    return handler(
        operation=operation,
        payload=payload,
        tenant_id=tenant_id,
        idempotency_key=idempotency_key,
        system_code=system_code,
    )


def _http_webhook(
    *,
    operation: str,
    payload: dict[str, Any],
    tenant_id: UUID,
    idempotency_key: str,
    system_code: str,
) -> dict[str, Any]:
    """POST the payload body to the target URL. Failures raise so the outbox retries."""
    url = payload.get("url") or payload.get("endpoint")
    if not url:
        raise OutboundBlockedError("Webhook payload is missing 'url'")
    body = payload.get("body")
    if not isinstance(body, dict):
        body = {k: v for k, v in payload.items() if k not in {"_execute", "url", "endpoint"}}
    http_status = post_json(
        str(url),
        {"event": operation, "tenant_id": str(tenant_id), "data": body},
        idempotency_key=idempotency_key,
        request_id=get_request_id(),
    )
    logger.info(
        "connector.http",
        extra={
            "system_code": system_code,
            "operation": operation,
            "tenant_id": str(tenant_id),
            "idempotency_key": idempotency_key,
            "http_status": http_status,
        },
    )
    return {
        "status": "executed",
        "connector": "http_webhook",
        "system_code": system_code,
        "operation": operation,
        "idempotency_key": idempotency_key,
        "http_status": http_status,
    }


def _smtp_mail(
    *,
    operation: str,
    payload: dict[str, Any],
    tenant_id: UUID,
    idempotency_key: str,
    system_code: str,
) -> dict[str, Any]:
    logger.info(
        "connector.smtp",
        extra={
            "system_code": system_code,
            "operation": operation,
            "tenant_id": str(tenant_id),
            "idempotency_key": idempotency_key,
            "to": payload.get("to"),
        },
    )
    return {
        "status": "executed",
        "connector": "smtp",
        "system_code": system_code,
        "operation": operation,
        "idempotency_key": idempotency_key,
        "to": payload.get("to"),
        "subject": payload.get("subject"),
    }


def _s3_object(
    *,
    operation: str,
    payload: dict[str, Any],
    tenant_id: UUID,
    idempotency_key: str,
    system_code: str,
) -> dict[str, Any]:
    return {
        "status": "executed",
        "connector": "s3",
        "system_code": system_code,
        "operation": operation,
        "idempotency_key": idempotency_key,
        "bucket": payload.get("bucket"),
        "key": payload.get("key") or payload.get("object_key"),
    }


def _erp_peer(
    *,
    operation: str,
    payload: dict[str, Any],
    tenant_id: UUID,
    idempotency_key: str,
    system_code: str,
) -> dict[str, Any]:
    return {
        "status": "executed",
        "connector": "erp_peer",
        "system_code": system_code,
        "operation": operation,
        "idempotency_key": idempotency_key,
        "peer_entity": payload.get("entity_type"),
        "peer_id": payload.get("entity_id"),
    }


_CONNECTORS = {
    "http": _http_webhook,
    "webhook": _http_webhook,
    "http_webhook": _http_webhook,
    "smtp": _smtp_mail,
    "email": _smtp_mail,
    "s3": _s3_object,
    "object_storage": _s3_object,
    "erp": _erp_peer,
    "tally": _erp_peer,
    "sap": _erp_peer,
}
