"""Shared HR in-app notification helpers."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import Session

from modules.foundation.models.security import SecUser
from modules.foundation.service.notification_href import sanitize_inbox_href
from modules.master_data.published import EmployeeRead
from modules.platform.compat.notify_facade import PlatformNotifyFacade
from security.rbac import RBACEngine


def _send_in_app(
    db: Session,
    *,
    tenant_id: UUID,
    recipient_user_id: UUID | None,
    recipient_address: str | None,
    template_code: str,
    template_name: str,
    event_type: str,
    title: str,
    body: str,
    kind: str,
    extra: dict | None = None,
) -> bool:
    _ = template_name
    if recipient_user_id is None and not recipient_address:
        return False
    payload = {"title": title, "body": body, "kind": kind}
    if extra:
        payload.update(extra)
    href = sanitize_inbox_href(payload.get("href"), kind=kind)
    if href:
        payload["href"] = href
    PlatformNotifyFacade(db).send(
        tenant_id=tenant_id,
        template_code=template_code,
        event_type=event_type,
        recipient_user_id=recipient_user_id,
        recipient_address=recipient_address,
        payload_json=payload,
        channel="in_app",
        idempotency_key=(
            f"hr:{event_type}:{recipient_user_id or recipient_address}:"
            f"{payload.get('employee_id') or payload.get('href') or kind}"
        ),
    )
    return True


def notify_employee(
    db: Session,
    *,
    tenant_id: UUID,
    employee_id: UUID,
    template_code: str,
    template_name: str,
    event_type: str,
    title: str,
    body: str,
    kind: str,
    extra: dict | None = None,
    cc_reporting_manager: bool = True,
) -> bool:
    emp = db.get(EmployeeRead, employee_id)
    if emp is None:
        return False
    sent = _send_in_app(
        db,
        tenant_id=tenant_id,
        recipient_user_id=emp.user_id,
        recipient_address=emp.email,
        template_code=template_code,
        template_name=template_name,
        event_type=event_type,
        title=title,
        body=body,
        kind=kind,
        extra={**(extra or {}), "employee_id": str(employee_id)},
    )
    if cc_reporting_manager and emp.reporting_manager_id:
        mgr = db.get(EmployeeRead, emp.reporting_manager_id)
        if mgr is not None:
            manager_extra = {**(extra or {}), "employee_id": str(employee_id)}
            if kind == "leave":
                manager_extra["href"] = "/hr/ess-inbox"
            _send_in_app(
                db,
                tenant_id=tenant_id,
                recipient_user_id=mgr.user_id,
                recipient_address=mgr.email,
                template_code=template_code,
                template_name=template_name,
                event_type=event_type,
                title=f"[Manager] {title}",
                body=body,
                kind=kind,
                extra=manager_extra,
            )
    return sent


def notify_users_with_permission(
    db: Session,
    *,
    tenant_id: UUID,
    permission_code: str,
    template_code: str,
    template_name: str,
    event_type: str,
    title: str,
    body: str,
    kind: str,
    extra: dict | None = None,
    exclude_user_ids: set[UUID] | None = None,
) -> int:
    """Notify every active user with the given permission (e.g. HR on manager approval)."""
    exclude = exclude_user_ids or set()
    user_ids = RBACEngine(db).list_user_ids_with_permission(tenant_id, permission_code)
    count = 0
    for uid in user_ids:
        if uid in exclude:
            continue
        user = db.get(SecUser, uid)
        if user is None or getattr(user, "is_deleted", False) or user.status != "active":
            continue
        if _send_in_app(
            db,
            tenant_id=tenant_id,
            recipient_user_id=user.id,
            recipient_address=user.email,
            template_code=template_code,
            template_name=template_name,
            event_type=event_type,
            title=title,
            body=body,
            kind=kind,
            extra=extra,
        ):
            count += 1
    return count
