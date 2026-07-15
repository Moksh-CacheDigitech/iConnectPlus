"""E-Commerce EcSalesChannel repository."""

from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from modules.ecommerce.models import EcSalesChannel
from modules.ecommerce.repository.base import EcommerceScopedRepository, utcnow
from modules.foundation.domain.value_objects import TenantContext


class SalesChannelRepository(EcommerceScopedRepository):
    def __init__(self, db: Session) -> None:
        super().__init__(db)

    def get(self, ctx: TenantContext, row_id: UUID) -> EcSalesChannel | None:
        stmt = select(EcSalesChannel).where(EcSalesChannel.id == row_id, EcSalesChannel.is_deleted.is_(False))
        stmt = self.apply_ecommerce_filter(stmt, EcSalesChannel, ctx, branch_scoped=False)
        return self.db.scalar(stmt)

    def list_rows(self, ctx: TenantContext, company_id: UUID):
        stmt = select(EcSalesChannel).where(
            EcSalesChannel.company_id == company_id,
            EcSalesChannel.is_deleted.is_(False),
        )
        stmt = self.apply_ecommerce_filter(stmt, EcSalesChannel, ctx, branch_scoped=False)
        return list(self.db.scalars(stmt).all())

    def create(self, ctx: TenantContext, **fields) -> EcSalesChannel:
        row = EcSalesChannel(
            id=uuid4(),
            tenant_id=ctx.tenant_id,
            created_by=ctx.user_id,
            updated_by=ctx.user_id,
            **fields,
        )
        self.db.add(row)
        self.db.flush()
        return row

    def update(self, ctx: TenantContext, row_id: UUID, **fields) -> EcSalesChannel | None:
        row = self.get(ctx, row_id)
        if row is None:
            return None
        for k, v in fields.items():
            if v is not None:
                setattr(row, k, v)
        row.updated_at = utcnow()
        row.updated_by = ctx.user_id
        if hasattr(row, "version"):
            row.version = int(row.version or 1) + 1
        self.db.flush()
        return row
