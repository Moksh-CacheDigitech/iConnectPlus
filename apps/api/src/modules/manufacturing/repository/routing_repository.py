"""Manufacturing routing repository."""

from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from modules.foundation.domain.value_objects import TenantContext
from modules.manufacturing.models import MfgRouting, MfgRoutingOperation
from modules.manufacturing.repository.base import MfgScopedRepository, utcnow


class RoutingRepository(MfgScopedRepository):
    def __init__(self, db: Session) -> None:
        super().__init__(db)

    def get(self, ctx: TenantContext, routing_id: UUID) -> MfgRouting | None:
        stmt = (
            select(MfgRouting)
            .options(selectinload(MfgRouting.operations))
            .where(MfgRouting.id == routing_id, MfgRouting.is_deleted.is_(False))
        )
        stmt = self.apply_mfg_filter(stmt, MfgRouting, ctx)
        return self.db.scalar(stmt)

    def list_routings(self, ctx: TenantContext, company_id: UUID):
        stmt = (
            select(MfgRouting)
            .options(selectinload(MfgRouting.operations))
            .where(MfgRouting.company_id == company_id, MfgRouting.is_deleted.is_(False))
        )
        stmt = self.apply_mfg_filter(stmt, MfgRouting, ctx)
        return list(self.db.scalars(stmt).all())

    def create(self, ctx: TenantContext, **fields) -> MfgRouting:
        row = MfgRouting(
            id=uuid4(),
            tenant_id=ctx.tenant_id,
            created_by=ctx.user_id,
            updated_by=ctx.user_id,
            **fields,
        )
        self.db.add(row)
        self.db.flush()
        return row

    def add_operation(self, ctx: TenantContext, routing: MfgRouting, **fields) -> MfgRoutingOperation:
        op = MfgRoutingOperation(
            id=uuid4(),
            tenant_id=ctx.tenant_id,
            company_id=routing.company_id,
            branch_id=routing.branch_id,
            routing_id=routing.id,
            created_by=ctx.user_id,
            updated_by=ctx.user_id,
            **fields,
        )
        self.db.add(op)
        self.db.flush()
        return op

    def update(self, ctx: TenantContext, routing_id: UUID, **fields) -> MfgRouting | None:
        row = self.get(ctx, routing_id)
        if row is None:
            return None
        for k, v in fields.items():
            if v is not None:
                setattr(row, k, v)
        row.updated_at = utcnow()
        row.updated_by = ctx.user_id
        row.version = int(row.version or 1) + 1
        self.db.flush()
        return row
