"""Asset transaction repository."""

from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from modules.finance.models.asset import FinAssetTransaction
from modules.finance.repository.base import FinanceScopedRepository, utcnow
from modules.foundation.domain.value_objects import TenantContext


class AssetRepository(FinanceScopedRepository):
    def __init__(self, db: Session) -> None:
        super().__init__(db)

    def list_transactions(self, ctx: TenantContext, company_id: UUID) -> list[FinAssetTransaction]:
        stmt = select(FinAssetTransaction).where(FinAssetTransaction.company_id == company_id)
        stmt = self.apply_finance_filter(stmt, FinAssetTransaction, ctx, branch_scoped=True)
        return list(self.db.scalars(stmt).all())

    def get_transaction(self, ctx: TenantContext, transaction_id: UUID) -> FinAssetTransaction | None:
        stmt = select(FinAssetTransaction).where(
            FinAssetTransaction.id == transaction_id,
            FinAssetTransaction.tenant_id == ctx.tenant_id,
            FinAssetTransaction.is_deleted.is_(False),
        )
        return self.db.scalar(stmt)

    def create_transaction(
        self, ctx: TenantContext, *, company_id: UUID, branch_id: UUID, **fields: object
    ) -> FinAssetTransaction:
        row = FinAssetTransaction(
            id=uuid4(),
            tenant_id=ctx.tenant_id,
            company_id=company_id,
            branch_id=branch_id,
            created_by=ctx.user_id,
            updated_by=ctx.user_id,
            **fields,
        )
        self.db.add(row)
        self.db.flush()
        return row

    def update_transaction(
        self, ctx: TenantContext, transaction_id: UUID, **fields: object
    ) -> FinAssetTransaction | None:
        row = self.get_transaction(ctx, transaction_id)
        if row is None:
            return None
        for key, value in fields.items():
            if hasattr(row, key):
                setattr(row, key, value)
        row.updated_at = utcnow()
        row.updated_by = ctx.user_id
        row.version += 1
        self.db.flush()
        return row
