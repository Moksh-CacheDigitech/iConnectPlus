"""Chart of accounts repository."""

from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from modules.finance.models.coa import FinAccountGroup, FinChartOfAccount
from modules.finance.repository.base import FinanceScopedRepository, utcnow
from modules.foundation.domain.value_objects import TenantContext


class COARepository(FinanceScopedRepository):
    def __init__(self, db: Session) -> None:
        super().__init__(db)

    def list_account_groups(self, ctx: TenantContext, company_id: UUID) -> list[FinAccountGroup]:
        stmt = select(FinAccountGroup).where(FinAccountGroup.company_id == company_id)
        stmt = self.apply_finance_filter(stmt, FinAccountGroup, ctx)
        return list(self.db.scalars(stmt).all())

    def get_account_group(self, ctx: TenantContext, group_id: UUID) -> FinAccountGroup | None:
        stmt = select(FinAccountGroup).where(
            FinAccountGroup.id == group_id,
            FinAccountGroup.tenant_id == ctx.tenant_id,
            FinAccountGroup.is_deleted.is_(False),
        )
        return self.db.scalar(stmt)

    def create_account_group(
        self, ctx: TenantContext, *, company_id: UUID, **fields: object
    ) -> FinAccountGroup:
        row = FinAccountGroup(
            id=uuid4(),
            tenant_id=ctx.tenant_id,
            company_id=company_id,
            created_by=ctx.user_id,
            updated_by=ctx.user_id,
            **fields,
        )
        self.db.add(row)
        self.db.flush()
        return row

    def list_accounts(self, ctx: TenantContext, company_id: UUID) -> list[FinChartOfAccount]:
        stmt = select(FinChartOfAccount).where(FinChartOfAccount.company_id == company_id)
        stmt = self.apply_finance_filter(stmt, FinChartOfAccount, ctx)
        return list(self.db.scalars(stmt).all())

    def get_account(self, ctx: TenantContext, account_id: UUID) -> FinChartOfAccount | None:
        stmt = select(FinChartOfAccount).where(
            FinChartOfAccount.id == account_id,
            FinChartOfAccount.tenant_id == ctx.tenant_id,
            FinChartOfAccount.is_deleted.is_(False),
        )
        return self.db.scalar(stmt)

    def get_account_for_update(self, ctx: TenantContext, account_id: UUID) -> FinChartOfAccount | None:
        stmt = (
            select(FinChartOfAccount)
            .where(
                FinChartOfAccount.id == account_id,
                FinChartOfAccount.tenant_id == ctx.tenant_id,
                FinChartOfAccount.is_deleted.is_(False),
            )
            .with_for_update()
        )
        return self.db.scalar(stmt)

    def create_account(
        self, ctx: TenantContext, *, company_id: UUID, **fields: object
    ) -> FinChartOfAccount:
        row = FinChartOfAccount(
            id=uuid4(),
            tenant_id=ctx.tenant_id,
            company_id=company_id,
            created_by=ctx.user_id,
            updated_by=ctx.user_id,
            **fields,
        )
        self.db.add(row)
        self.db.flush()
        return row

    def update_account(
        self, ctx: TenantContext, account_id: UUID, **fields: object
    ) -> FinChartOfAccount | None:
        row = self.get_account(ctx, account_id)
        if row is None:
            return None
        for key, value in fields.items():
            if hasattr(row, key) and value is not None:
                setattr(row, key, value)
        row.updated_at = utcnow()
        row.updated_by = ctx.user_id
        row.version += 1
        self.db.flush()
        return row

    def soft_delete_account(self, ctx: TenantContext, account_id: UUID) -> bool:
        row = self.get_account(ctx, account_id)
        if row is None:
            return False
        row.is_deleted = True
        row.deleted_at = utcnow()
        row.deleted_by = ctx.user_id
        self.db.flush()
        return True
