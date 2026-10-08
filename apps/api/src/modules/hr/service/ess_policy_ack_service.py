"""HR-owned policy publication reads + employee acknowledgements (consumed by ESS)."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from core.exceptions import NotFoundException
from modules.foundation.domain.value_objects import TenantContext
from modules.hr.models.ess_policy import HrEssPolicy, HrEssPolicyAck


class EssPolicyAckService:
    def __init__(self, db: Session) -> None:
        self._db = db

    def list_published(
        self, ctx: TenantContext, company_id: UUID, *, mandatory_only: bool = False
    ) -> list[HrEssPolicy]:
        stmt = select(HrEssPolicy).where(
            HrEssPolicy.tenant_id == ctx.tenant_id,
            HrEssPolicy.company_id == company_id,
            HrEssPolicy.is_deleted.is_(False),
            HrEssPolicy.status == "published",
        )
        if mandatory_only:
            stmt = stmt.where(HrEssPolicy.is_mandatory.is_(True))
        return list(
            self._db.scalars(stmt.order_by(HrEssPolicy.display_order, HrEssPolicy.title)).all()
        )

    def get_published(self, ctx: TenantContext, company_id: UUID, policy_id: UUID) -> HrEssPolicy:
        row = self._db.get(HrEssPolicy, policy_id)
        if (
            row is None
            or row.is_deleted
            or row.tenant_id != ctx.tenant_id
            or row.company_id != company_id
            or row.status != "published"
        ):
            raise NotFoundException("Policy not found")
        return row

    def acknowledged_versions(self, ctx: TenantContext, employee_id: UUID) -> dict[UUID, int]:
        rows = self._db.scalars(
            select(HrEssPolicyAck).where(
                HrEssPolicyAck.tenant_id == ctx.tenant_id,
                HrEssPolicyAck.employee_id == employee_id,
                HrEssPolicyAck.is_deleted.is_(False),
            )
        ).all()
        best: dict[UUID, int] = {}
        for row in rows:
            if row.policy_version > best.get(row.policy_id, 0):
                best[row.policy_id] = row.policy_version
        return best

    def acknowledge(
        self, ctx: TenantContext, *, company_id: UUID, employee_id: UUID, policy: HrEssPolicy
    ) -> tuple[UUID, datetime, bool]:
        """Record an acknowledgement. Returns (ack_id, acknowledged_at, created)."""
        existing = self._db.scalar(
            select(HrEssPolicyAck).where(
                HrEssPolicyAck.employee_id == employee_id,
                HrEssPolicyAck.policy_id == policy.id,
                HrEssPolicyAck.policy_version == policy.policy_version,
                HrEssPolicyAck.is_deleted.is_(False),
            )
        )
        if existing is not None:
            return existing.id, existing.acknowledged_at, False
        now = datetime.now(timezone.utc)
        ack = HrEssPolicyAck(
            id=uuid4(),
            tenant_id=ctx.tenant_id,
            company_id=company_id,
            policy_id=policy.id,
            employee_id=employee_id,
            policy_version=policy.policy_version,
            acknowledged_at=now,
            created_by=ctx.user_id,
            updated_by=ctx.user_id,
        )
        self._db.add(ack)
        self._db.flush()
        return ack.id, now, True
