"""IAudit → Foundation AuditService."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import Session

from modules.foundation.service.audit_service import AuditService
from modules.platform.dto import AuditIntent


class AuditAdapter:
    def __init__(self, db: Session) -> None:
        self._audit = AuditService(db)

    def log_entity_change(self, intent: AuditIntent):
        return self._audit.log_entity_change(
            tenant_id=intent.tenant_id,
            entity_name=intent.entity_name,
            entity_id=intent.entity_id,
            operation=intent.operation,
            performed_by=intent.performed_by,
            old_value=intent.old_value,
            new_value=intent.new_value,
            ip_address=intent.ip_address,
            request_id=intent.request_id,
        )

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
        self._audit.log_security_event(
            tenant_id=tenant_id,
            event_type=event_type,
            user_id=user_id,
            severity=severity,
            details_json=details,
            ip_address=ip_address,
        )

    def list_logs_for_entity(self, *, tenant_id: UUID | None, entity_name: str, entity_id: UUID):
        return self._audit.list_logs_for_entity(
            tenant_id=tenant_id, entity_name=entity_name, entity_id=entity_id
        )
