"""BOQ / SOW service levels on My Jobs attachment tasks.

Pre-sales must reply within ``RESPONSE_SLA`` whether they can submit (with a
reason when they cannot), and attach the document within ``ATTACH_SLA``.
A miss - or a "cannot submit" - goes to the assignee's reporting manager and
back to the salesperson who raised the request.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from core.exceptions import ConflictException, ForbiddenException
from modules.crm.models import CrmApprovalTask
from modules.crm.service.crm_module_admin import CrmModuleAdminService
from modules.crm.service.crm_notification_service import notify_crm_user, resolve_user_manager_user_id
from modules.foundation.domain.value_objects import TenantContext

SLA_ACTIONS = frozenset({"provide_boq_attachment", "provide_sow_attachment"})
RESPONSE_SLA = timedelta(hours=1)
ATTACH_SLA = timedelta(hours=6)

_LEVEL_RESPONSE_MISSED = 1
_LEVEL_ATTACH_MISSED = 2


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def sla_deadlines(action: str | None, created_at: datetime | None = None) -> dict[str, datetime]:
    if action not in SLA_ACTIONS:
        return {}
    start = created_at or _utcnow()
    return {"response_due_at": start + RESPONSE_SLA, "due_at": start + ATTACH_SLA}


def _doc_label(task: CrmApprovalTask) -> str:
    return "BOQ" if task.action == "provide_boq_attachment" else "SOW"


def _href(task: CrmApprovalTask) -> str:
    base = "leads" if task.entity_type == "lead" else "opportunities"
    return f"/crm/{base}/{task.entity_id}"


class BoqSowSlaService:
    def __init__(self, db: Session) -> None:
        self._db = db

    def _siblings(self, task: CrmApprovalTask) -> list[CrmApprovalTask]:
        stmt = select(CrmApprovalTask).where(
            CrmApprovalTask.tenant_id == task.tenant_id,
            CrmApprovalTask.entity_type == task.entity_type,
            CrmApprovalTask.entity_id == task.entity_id,
            CrmApprovalTask.action == task.action,
            CrmApprovalTask.status == "pending",
            CrmApprovalTask.is_deleted.is_(False),
        )
        return list(self._db.scalars(stmt).all())

    def respond(
        self,
        ctx: TenantContext,
        task: CrmApprovalTask,
        *,
        can_submit: bool,
        reason: str | None = None,
    ) -> CrmApprovalTask:
        if task.action not in SLA_ACTIONS:
            raise ConflictException("Only BOQ / SOW attachment tasks take a submit response")
        if task.status != "pending":
            raise ConflictException("This task is already closed")
        is_admin = CrmModuleAdminService(self._db).is_admin(ctx)
        if task.assigned_user_id != ctx.user_id and not is_admin:
            raise ForbiddenException("Only the assignee can respond to this task")
        text = (reason or "").strip()
        if not can_submit and not text:
            raise ConflictException("Say why the document cannot be submitted (call not aligned, questions open...)")
        if task.responded_at is not None:
            raise ConflictException("A response is already recorded for this request")

        now = _utcnow()
        response = "can_submit" if can_submit else "cannot_submit"
        for row in self._siblings(task):
            row.response = response
            row.response_reason = text or None
            row.responded_at = now
            row.updated_by = ctx.user_id
            row.updated_at = now
        self._db.flush()

        doc = _doc_label(task)
        late = task.response_due_at is not None and now > task.response_due_at
        if task.requested_by and task.requested_by != ctx.user_id:
            notify_crm_user(
                self._db,
                tenant_id=ctx.tenant_id,
                recipient_user_id=task.requested_by,
                event_type="crm.boq_sow.response",
                title=f"{doc} {'will be submitted' if can_submit else 'cannot be submitted'} - {task.title}",
                body=(
                    f"Pre-sales {'confirmed they can submit' if can_submit else 'cannot submit'} the {doc}"
                    f"{f': {text}' if text else '.'}"
                    + (" (response was past the 1-hour SLA)" if late else "")
                ),
                entity_type=task.entity_type,
                entity_id=task.entity_id,
                href=_href(task),
                created_by=ctx.user_id,
            )
        if not can_submit:
            manager = resolve_user_manager_user_id(self._db, ctx.tenant_id, task.assigned_user_id)
            if manager is not None:
                notify_crm_user(
                    self._db,
                    tenant_id=ctx.tenant_id,
                    recipient_user_id=manager,
                    event_type="crm.boq_sow.cannot_submit",
                    title=f"{doc} blocked - {task.title}",
                    body=f"Your team member cannot submit the {doc}: {text}. Review and route it back to Sales.",
                    entity_type=task.entity_type,
                    entity_id=task.entity_id,
                    href=_href(task),
                    created_by=ctx.user_id,
                )
        return task

    def escalate_breaches(self, *, now: datetime | None = None) -> dict[str, int]:
        now = now or _utcnow()
        stmt = select(CrmApprovalTask).where(
            CrmApprovalTask.is_deleted.is_(False),
            CrmApprovalTask.status == "pending",
            CrmApprovalTask.action.in_(tuple(SLA_ACTIONS)),
            CrmApprovalTask.escalation_level < _LEVEL_ATTACH_MISSED,
        )
        counts = {"response_escalations": 0, "attach_escalations": 0}
        for task in self._db.scalars(stmt).all():
            if task.assigned_role == "admin_copy":
                continue
            attach_missed = task.due_at is not None and now > task.due_at
            response_missed = (
                task.responded_at is None and task.response_due_at is not None and now > task.response_due_at
            )
            if attach_missed and task.escalation_level < _LEVEL_ATTACH_MISSED:
                self._escalate(task, level=_LEVEL_ATTACH_MISSED, now=now)
                counts["attach_escalations"] += 1
            elif response_missed and task.escalation_level < _LEVEL_RESPONSE_MISSED:
                self._escalate(task, level=_LEVEL_RESPONSE_MISSED, now=now)
                counts["response_escalations"] += 1
        self._db.flush()
        return counts

    def _escalate(self, task: CrmApprovalTask, *, level: int, now: datetime) -> None:
        doc = _doc_label(task)
        if level == _LEVEL_ATTACH_MISSED:
            title = f"{doc} overdue (6-hour SLA) - {task.title}"
            body = f"The {doc} was due by {task.due_at:%d %b %H:%M} and is still not attached."
        else:
            title = f"No response on {doc} request (1-hour SLA) - {task.title}"
            body = "Pre-sales has not confirmed whether they can submit within the 1-hour response window."
        if task.response_reason:
            body += f" Last response: {task.response_reason}"
        recipients: set[UUID] = set()
        manager = resolve_user_manager_user_id(self._db, task.tenant_id, task.assigned_user_id)
        if manager is not None:
            recipients.add(manager)
        if task.requested_by is not None:
            recipients.add(task.requested_by)
        if task.assigned_user_id is not None:
            recipients.add(task.assigned_user_id)
        for user_id in recipients:
            notify_crm_user(
                self._db,
                tenant_id=task.tenant_id,
                recipient_user_id=user_id,
                event_type="crm.boq_sow.sla_breach",
                title=title,
                body=body,
                entity_type=task.entity_type,
                entity_id=task.entity_id,
                href=_href(task),
                digest_key=f"{task.id}:sla:{level}",
            )
        task.escalation_level = level
        task.escalated_at = now
        task.priority = "high"
