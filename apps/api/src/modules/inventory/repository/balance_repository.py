"""Inventory stock balance repository."""

from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from modules.foundation.domain.value_objects import TenantContext
from modules.inventory.models.balance import InvStockBalance
from modules.inventory.repository.base import InvScopedRepository, utcnow


class BalanceRepository(InvScopedRepository):
    def __init__(self, db: Session) -> None:
        super().__init__(db)

    def get(self, ctx: TenantContext, balance_id: UUID) -> InvStockBalance | None:
        stmt = select(InvStockBalance).where(
            InvStockBalance.id == balance_id,
            InvStockBalance.is_deleted.is_(False),
        )
        stmt = self.apply_inv_filter(stmt, InvStockBalance, ctx, branch_scoped=True)
        return self.db.scalar(stmt)

    def list_balances(
        self,
        ctx: TenantContext,
        company_id: UUID,
        *,
        warehouse_id: UUID | None = None,
        product_id: UUID | None = None,
    ) -> list[InvStockBalance]:
        stmt = select(InvStockBalance).where(
            InvStockBalance.company_id == company_id,
            InvStockBalance.is_deleted.is_(False),
        )
        if warehouse_id:
            stmt = stmt.where(InvStockBalance.warehouse_id == warehouse_id)
        if product_id:
            stmt = stmt.where(InvStockBalance.product_id == product_id)
        stmt = self.apply_inv_filter(stmt, InvStockBalance, ctx, branch_scoped=True)
        return list(self.db.scalars(stmt).all())

    def get_for_update(
        self,
        ctx: TenantContext,
        *,
        company_id: UUID,
        warehouse_id: UUID,
        product_id: UUID,
        bin_id: UUID | None,
        batch_id: UUID | None,
        quality_status: str = "available",
    ) -> InvStockBalance | None:
        stmt = (
            select(InvStockBalance)
            .where(
                InvStockBalance.company_id == company_id,
                InvStockBalance.warehouse_id == warehouse_id,
                InvStockBalance.product_id == product_id,
                InvStockBalance.quality_status == quality_status,
                InvStockBalance.is_deleted.is_(False),
            )
            .with_for_update()
        )
        if bin_id is None:
            stmt = stmt.where(InvStockBalance.bin_id.is_(None))
        else:
            stmt = stmt.where(InvStockBalance.bin_id == bin_id)
        if batch_id is None:
            stmt = stmt.where(InvStockBalance.batch_id.is_(None))
        else:
            stmt = stmt.where(InvStockBalance.batch_id == batch_id)
        stmt = self.apply_tenant_filter(stmt, InvStockBalance, ctx)
        return self.db.scalar(stmt)

    def create(
        self,
        ctx: TenantContext,
        *,
        company_id: UUID,
        branch_id: UUID,
        warehouse_id: UUID,
        product_id: UUID,
        uom_id: UUID,
        bin_id: UUID | None = None,
        batch_id: UUID | None = None,
        quality_status: str = "available",
    ) -> InvStockBalance:
        row = InvStockBalance(
            id=uuid4(),
            tenant_id=ctx.tenant_id,
            company_id=company_id,
            branch_id=branch_id,
            warehouse_id=warehouse_id,
            product_id=product_id,
            uom_id=uom_id,
            bin_id=bin_id,
            batch_id=batch_id,
            quality_status=quality_status,
            on_hand_qty=0,
            reserved_qty=0,
            available_qty=0,
            status="active",
            created_by=ctx.user_id,
            updated_by=ctx.user_id,
        )
        self.db.add(row)
        self.db.flush()
        return row

    def get_or_create_for_update(
        self,
        ctx: TenantContext,
        *,
        company_id: UUID,
        branch_id: UUID,
        warehouse_id: UUID,
        product_id: UUID,
        uom_id: UUID,
        bin_id: UUID | None = None,
        batch_id: UUID | None = None,
        quality_status: str = "available",
    ) -> InvStockBalance:
        existing = self.get_for_update(
            ctx,
            company_id=company_id,
            warehouse_id=warehouse_id,
            product_id=product_id,
            bin_id=bin_id,
            batch_id=batch_id,
            quality_status=quality_status,
        )
        if existing is not None:
            return existing
        return self.create(
            ctx,
            company_id=company_id,
            branch_id=branch_id,
            warehouse_id=warehouse_id,
            product_id=product_id,
            uom_id=uom_id,
            bin_id=bin_id,
            batch_id=batch_id,
            quality_status=quality_status,
        )

    def touch(self, row: InvStockBalance, ctx: TenantContext) -> None:
        row.updated_at = utcnow()
        row.updated_by = ctx.user_id
        row.version = int(row.version or 1) + 1
