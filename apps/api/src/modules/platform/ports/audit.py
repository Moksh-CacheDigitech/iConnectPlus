"""Audit port — append-only entity / security events."""

from __future__ import annotations

from typing import Any, Protocol
from uuid import UUID

from modules.platform.dto import AuditIntent


class IAudit(Protocol):
    def log_entity_change(self, intent: AuditIntent) -> Any:
        ...

    def log_security_event(
        self,
        *,
        tenant_id: UUID | None,
        event_type: str,
        user_id: UUID | None,
        severity: str = "info",
        details: dict | None = None,
        ip_address: str | None = None,
    ) -> None:
        ...
