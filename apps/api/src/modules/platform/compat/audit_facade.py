"""AuditService-compatible facade over IAudit / AuditAdapter."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import Session

from modules.platform.adapters.audit_adapter import AuditAdapter
from modules.platform.dto import AuditIntent


class PlatformAuditFacade:
    """Drop-in replacement for foundation.AuditService."""

    def __init__(self, db: Session) -> None:
        self._audit = AuditAdapter(db)

    def log_entity_change(
        self,
        *,
        tenant_id: UUID | None,
        entity_name: str,
        entity_id: UUID,
        operation: str,
        performed_by: UUID | None,
        old_value: dict | None = None,
        new_value: dict | None = None,
        ip_address: str | None = None,
        request_id: str | None = None,
    ):
        return self._audit.log_entity_change(
            AuditIntent(
                tenant_id=tenant_id,
                entity_name=entity_name,
                entity_id=entity_id,
                operation=operation,
                performed_by=performed_by,
                old_value=old_value,
                new_value=new_value,
                ip_address=ip_address,
                request_id=request_id,
            )
        )

    def log_security_event(
        self,
        *,
        tenant_id: UUID | None,
        event_type: str,
        user_id: UUID | None,
        severity: str = "info",
        details_json: dict | None = None,
        ip_address: str | None = None,
    ) -> None:
        self._audit.log_security_event(
            tenant_id=tenant_id,
            event_type=event_type,
            user_id=user_id,
            severity=severity,
            details=details_json,
            ip_address=ip_address,
        )

    def list_logs_for_entity(self, *, tenant_id: UUID | None, entity_name: str, entity_id: UUID):
        return self._audit.list_logs_for_entity(
            tenant_id=tenant_id, entity_name=entity_name, entity_id=entity_id
        )
