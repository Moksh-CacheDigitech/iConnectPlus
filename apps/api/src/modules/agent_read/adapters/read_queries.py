"""Paginated SQL queries for agent read endpoints."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, or_, select

from modules.crm.models import CrmLead
from modules.crm.repository.base import CrmScopedRepository
from modules.foundation.domain.value_objects import TenantContext
from modules.master_data.models.party import MasterCustomer
from modules.master_data.models.product import MasterProduct
from modules.master_data.repository.base import MasterScopedRepository


class AgentLeadReadRepository(CrmScopedRepository):
    def search(
        self,
        ctx: TenantContext,
        company_id: UUID,
        *,
        q: str | None,
        status: str | None,
        limit: int,
        offset: int,
    ) -> tuple[list[CrmLead], int]:
        base = select(CrmLead).where(
            CrmLead.company_id == company_id,
            CrmLead.is_deleted.is_(False),
            CrmLead.blueprint_state != "converted",
            CrmLead.converted_opportunity_id.is_(None),
        )
        base = self.apply_crm_filter(base, CrmLead, ctx, branch_scoped=True)
        if status:
            base = base.where(CrmLead.status == status)
        if q:
            pattern = f"%{q.strip()}%"
            base = base.where(
                or_(
                    CrmLead.lead_code.ilike(pattern),
                    CrmLead.company_name.ilike(pattern),
                    CrmLead.email.ilike(pattern),
                    CrmLead.first_name.ilike(pattern),
                    CrmLead.last_name.ilike(pattern),
                    CrmLead.mobile.ilike(pattern),
                )
            )
        count_stmt = select(func.count()).select_from(base.subquery())
        total = int(self.db.scalar(count_stmt) or 0)
        rows = list(
            self.db.scalars(
                base.order_by(CrmLead.created_at.desc()).limit(limit).offset(offset)
            ).all()
        )
        return rows, total


class AgentCustomerReadRepository(MasterScopedRepository):
    def search(
        self,
        ctx: TenantContext,
        *,
        q: str | None,
        status: str | None,
        limit: int,
        offset: int,
    ) -> tuple[list[MasterCustomer], int]:
        base = select(MasterCustomer).where(MasterCustomer.is_deleted.is_(False))
        base = self.apply_master_filter(base, MasterCustomer, ctx, branch_scoped=True)
        if status:
            base = base.where(MasterCustomer.status == status)
        if q:
            pattern = f"%{q.strip()}%"
            base = base.where(
                or_(
                    MasterCustomer.customer_code.ilike(pattern),
                    MasterCustomer.customer_name.ilike(pattern),
                    MasterCustomer.email.ilike(pattern),
                    MasterCustomer.mobile.ilike(pattern),
                )
            )
        count_stmt = select(func.count()).select_from(base.subquery())
        total = int(self.db.scalar(count_stmt) or 0)
        rows = list(
            self.db.scalars(
                base.order_by(MasterCustomer.customer_name.asc()).limit(limit).offset(offset)
            ).all()
        )
        return rows, total

    def get(self, ctx: TenantContext, customer_id: UUID) -> MasterCustomer | None:
        stmt = select(MasterCustomer).where(
            MasterCustomer.id == customer_id,
            MasterCustomer.tenant_id == ctx.tenant_id,
            MasterCustomer.is_deleted.is_(False),
        )
        return self.db.scalar(stmt)


class AgentProductReadRepository(MasterScopedRepository):
    def search(
        self,
        ctx: TenantContext,
        *,
        q: str | None,
        status: str | None,
        limit: int,
        offset: int,
    ) -> tuple[list[MasterProduct], int]:
        base = select(MasterProduct).where(MasterProduct.is_deleted.is_(False))
        base = self.apply_master_filter(base, MasterProduct, ctx, branch_scoped=True)
        if status:
            base = base.where(MasterProduct.status == status)
        if q:
            pattern = f"%{q.strip()}%"
            base = base.where(
                or_(
                    MasterProduct.product_code.ilike(pattern),
                    MasterProduct.product_name.ilike(pattern),
                )
            )
        count_stmt = select(func.count()).select_from(base.subquery())
        total = int(self.db.scalar(count_stmt) or 0)
        rows = list(
            self.db.scalars(
                base.order_by(MasterProduct.product_name.asc()).limit(limit).offset(offset)
            ).all()
        )
        return rows, total

    def get(self, ctx: TenantContext, product_id: UUID) -> MasterProduct | None:
        stmt = select(MasterProduct).where(
            MasterProduct.id == product_id,
            MasterProduct.tenant_id == ctx.tenant_id,
            MasterProduct.is_deleted.is_(False),
        )
        return self.db.scalar(stmt)
