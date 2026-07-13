"""Audit router (read-only)."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.session import get_db
from modules.foundation.dependencies import require_permission
from modules.foundation.domain.value_objects import TenantContext
from modules.foundation.schemas import AuditLogResponse
from modules.foundation.service.audit_service import AuditService
from shared.schemas import APIResponse

router = APIRouter(prefix="/audit", tags=["Audit"])


@router.get("/logs", response_model=APIResponse[list[AuditLogResponse]])
def list_logs(
    ctx: Annotated[TenantContext, Depends(require_permission("foundation.audit:read"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[list[AuditLogResponse]]:
    logs = AuditService(db).list_logs(tenant_id=ctx.tenant_id)
    return APIResponse(
        message="Audit logs retrieved",
        data=[AuditLogResponse(**log.__dict__) for log in logs],
    )


@router.get("/logs/{log_id}", response_model=APIResponse[AuditLogResponse])
def get_log(
    log_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("foundation.audit:read"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[AuditLogResponse]:
    log = AuditService(db).get_log(log_id)
    if log is None or (log.tenant_id and log.tenant_id != ctx.tenant_id):
        from core.exceptions import NotFoundException

        raise NotFoundException("Audit log not found")
    return APIResponse(message="Audit log retrieved", data=AuditLogResponse(**log.__dict__))


@router.get("/events", response_model=APIResponse[list])
def list_events(
    ctx: Annotated[TenantContext, Depends(require_permission("foundation.audit:read"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[list]:
    events = AuditService(db).list_events(tenant_id=ctx.tenant_id)
    return APIResponse(
        message="Audit events retrieved",
        data=[
            {
                "id": str(e.id),
                "event_type": e.event_type,
                "severity": e.severity,
                "performed_at": e.performed_at.isoformat(),
            }
            for e in events
        ],
    )
