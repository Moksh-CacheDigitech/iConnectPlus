"""Inventory reservation repository."""

from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from modules.foundation.domain.value_objects import TenantContext
from modules.inventory.models.reservation import InvReservation
from modules.inventory.repository.base import InvScopedRepository, utcnow


class ReservationRepository(InvScopedRepository):
    def __init__(self, db: Session) -> None:
        super().__init__(db)

    def get(self, ctx: TenantContext, reservation_id: UUID) -> InvReservation | None:
        stmt = select(InvReservation).where(
            InvReservation.id == reservation_id, InvReservation.is_deleted.is_(False)
        )
        stmt = self.apply_inv_filter(stmt, InvReservation, ctx, branch_scoped=True)
        return self.db.scalar(stmt)

    def get_for_update(self, ctx: TenantContext, reservation_id: UUID) -> InvReservation | None:
        stmt = (
            select(InvReservation)
            .where(InvReservation.id == reservation_id, InvReservation.is_deleted.is_(False))
            .with_for_update()
        )
        stmt = self.apply_tenant_filter(stmt, InvReservation, ctx)
        return self.db.scalar(stmt)

    def list_reservations(self, ctx: TenantContext, company_id: UUID, status: str | None = None):
        stmt = select(InvReservation).where(
            InvReservation.company_id == company_id, InvReservation.is_deleted.is_(False)
        )
        if status:
            stmt = stmt.where(InvReservation.status == status)
        stmt = self.apply_inv_filter(stmt, InvReservation, ctx, branch_scoped=True)
        return list(self.db.scalars(stmt).all())

    def list_by_source(
        self,
        ctx: TenantContext,
        *,
        source_module: str,
        source_document_type: str,
        source_document_id: UUID,
    ) -> list[InvReservation]:
        stmt = select(InvReservation).where(
            InvReservation.source_module == source_module,
            InvReservation.source_document_type == source_document_type,
            InvReservation.source_document_id == source_document_id,
            InvReservation.is_deleted.is_(False),
        )
        stmt = self.apply_tenant_filter(stmt, InvReservation, ctx)
        return list(self.db.scalars(stmt).all())

    def list_stale_active(self, ctx: TenantContext, *, older_than):
        stmt = select(InvReservation).where(
            InvReservation.is_deleted.is_(False),
            InvReservation.status.in_(["active", "partially_issued"]),
            InvReservation.reserved_at.is_not(None),
            InvReservation.reserved_at < older_than,
        )
        stmt = self.apply_tenant_filter(stmt, InvReservation, ctx)
        return list(self.db.scalars(stmt).all())

    def create(self, ctx: TenantContext, **fields) -> InvReservation:
        row = InvReservation(
            id=uuid4(),
            tenant_id=ctx.tenant_id,
            created_by=ctx.user_id,
            updated_by=ctx.user_id,
            reserved_at=utcnow(),
            **fields,
        )
        self.db.add(row)
        self.db.flush()
        return row

    def touch(self, row: InvReservation, ctx: TenantContext) -> None:
        row.updated_at = utcnow()
        row.updated_by = ctx.user_id
        row.version = int(row.version or 1) + 1
