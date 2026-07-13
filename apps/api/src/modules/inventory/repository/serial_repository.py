"""Inventory serial repository."""

from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from modules.foundation.domain.value_objects import TenantContext
from modules.inventory.models.serial import InvSerial
from modules.inventory.repository.base import InvScopedRepository, utcnow


class SerialRepository(InvScopedRepository):
    def __init__(self, db: Session) -> None:
        super().__init__(db)

    def get(self, ctx: TenantContext, serial_id: UUID) -> InvSerial | None:
        stmt = select(InvSerial).where(InvSerial.id == serial_id, InvSerial.is_deleted.is_(False))
        stmt = self.apply_inv_filter(stmt, InvSerial, ctx)
        return self.db.scalar(stmt)

    def list_serials(self, ctx: TenantContext, company_id: UUID, product_id: UUID | None = None):
        stmt = select(InvSerial).where(
            InvSerial.company_id == company_id, InvSerial.is_deleted.is_(False)
        )
        if product_id:
            stmt = stmt.where(InvSerial.product_id == product_id)
        stmt = self.apply_inv_filter(stmt, InvSerial, ctx)
        return list(self.db.scalars(stmt).all())

    def create(self, ctx: TenantContext, **fields) -> InvSerial:
        row = InvSerial(
            id=uuid4(), tenant_id=ctx.tenant_id,
            created_by=ctx.user_id, updated_by=ctx.user_id, **fields
        )
        self.db.add(row)
        self.db.flush()
        return row

    def update(self, ctx: TenantContext, serial_id: UUID, **fields) -> InvSerial | None:
        row = self.get(ctx, serial_id)
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
