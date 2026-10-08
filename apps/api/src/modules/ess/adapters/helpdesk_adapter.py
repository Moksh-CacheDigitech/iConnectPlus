"""Helpdesk port for ESS support tickets."""

from __future__ import annotations

from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from modules.foundation.domain.value_objects import TenantContext
from modules.helpdesk.models.ticket import HdTicket
from modules.helpdesk.models.ticket_category import HdTicketCategory
from modules.helpdesk.models.ticket_comment import HdTicketComment
from modules.helpdesk.models.ticket_priority import HdTicketPriority


class EssHelpdeskAdapter:
    def __init__(self, db: Session) -> None:
        self._db = db

    def list_requester_tickets(
        self, ctx: TenantContext, *, company_id: UUID, employee_id: UUID, limit: int = 100
    ) -> list[HdTicket]:
        return list(
            self._db.scalars(
                select(HdTicket)
                .where(
                    HdTicket.tenant_id == ctx.tenant_id,
                    HdTicket.company_id == company_id,
                    HdTicket.requester_employee_id == employee_id,
                    HdTicket.is_deleted.is_(False),
                )
                .order_by(HdTicket.created_at.desc())
                .limit(limit)
            ).all()
        )

    def get_ticket(self, ticket_id: UUID) -> HdTicket | None:
        return self._db.get(HdTicket, ticket_id)

    def list_comments(self, ticket_id: UUID) -> list[HdTicketComment]:
        return list(
            self._db.scalars(
                select(HdTicketComment)
                .where(
                    HdTicketComment.ticket_id == ticket_id,
                    HdTicketComment.is_deleted.is_(False),
                    HdTicketComment.status == "active",
                )
                .order_by(HdTicketComment.commented_at.asc())
            ).all()
        )

    def resolve_or_create_category(
        self,
        ctx: TenantContext,
        *,
        company_id: UUID,
        category_code: str,
        category_name: str,
    ) -> HdTicketCategory:
        cat = self._db.scalar(
            select(HdTicketCategory).where(
                HdTicketCategory.tenant_id == ctx.tenant_id,
                HdTicketCategory.company_id == company_id,
                HdTicketCategory.category_code == category_code,
                HdTicketCategory.is_deleted.is_(False),
            )
        )
        if cat is not None:
            return cat
        cat = HdTicketCategory(
            id=uuid4(),
            tenant_id=ctx.tenant_id,
            company_id=company_id,
            category_code=category_code,
            category_name=category_name,
            status="active",
            created_by=ctx.user_id,
            updated_by=ctx.user_id,
        )
        self._db.add(cat)
        self._db.flush()
        return cat

    def resolve_or_create_priority(
        self,
        ctx: TenantContext,
        *,
        company_id: UUID,
        priority_code: str = "ESS_MEDIUM",
        priority_name: str = "Medium",
        rank_order: int = 2,
    ) -> HdTicketPriority:
        pri = self._db.scalar(
            select(HdTicketPriority).where(
                HdTicketPriority.tenant_id == ctx.tenant_id,
                HdTicketPriority.company_id == company_id,
                HdTicketPriority.priority_code == priority_code,
                HdTicketPriority.is_deleted.is_(False),
            )
        )
        if pri is not None:
            return pri
        pri = HdTicketPriority(
            id=uuid4(),
            tenant_id=ctx.tenant_id,
            company_id=company_id,
            priority_code=priority_code,
            priority_name=priority_name,
            rank_order=rank_order,
            status="active",
            created_by=ctx.user_id,
            updated_by=ctx.user_id,
        )
        self._db.add(pri)
        self._db.flush()
        return pri
