"""Tax repository."""

from datetime import date
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from modules.foundation.domain.value_objects import TenantContext
from modules.master_data.domain.entities import TaxEntity
from modules.master_data.models.reference import MasterTax
from modules.master_data.repository.base import MasterScopedRepository, utcnow


class TaxRepository(MasterScopedRepository):
    def __init__(self, db: Session) -> None:
        super().__init__(db)

    def list_taxes(self, ctx: TenantContext, *, company_id: UUID | None = None) -> list[TaxEntity]:
        stmt = select(MasterTax)
        stmt = self.apply_master_filter(stmt, MasterTax, ctx)
        if company_id:
            stmt = stmt.where(MasterTax.company_id == company_id)
        return [self._to_entity(r) for r in self.db.scalars(stmt).all()]

    def get_by_id(self, ctx: TenantContext, tax_id: UUID) -> TaxEntity | None:
        stmt = select(MasterTax).where(
            MasterTax.id == tax_id,
            MasterTax.tenant_id == ctx.tenant_id,
            MasterTax.is_deleted.is_(False),
        )
        row = self.db.scalar(stmt)
        return self._to_entity(row) if row else None

    def get_by_code(self, ctx: TenantContext, company_id: UUID, tax_code: str) -> MasterTax | None:
        stmt = select(MasterTax).where(
            MasterTax.tenant_id == ctx.tenant_id,
            MasterTax.company_id == company_id,
            MasterTax.tax_code == tax_code,
            MasterTax.is_deleted.is_(False),
        )
        return self.db.scalar(stmt)

    def create(
        self,
        ctx: TenantContext,
        *,
        company_id: UUID,
        tax_code: str,
        tax_name: str,
        tax_type: str,
        rate_percent: float,
        effective_from: date,
        is_compound: bool = False,
        effective_to: date | None = None,
    ) -> TaxEntity:
        row = MasterTax(
            id=uuid4(),
            tenant_id=ctx.tenant_id,
            company_id=company_id,
            tax_code=tax_code,
            tax_name=tax_name,
            tax_type=tax_type,
            rate_percent=rate_percent,
            effective_from=effective_from,
            is_compound=is_compound,
            effective_to=effective_to,
            status="active",
            created_by=ctx.user_id,
            updated_by=ctx.user_id,
        )
        self.db.add(row)
        self.db.flush()
        return self._to_entity(row)

    def update(self, ctx: TenantContext, tax_id: UUID, **fields: object) -> TaxEntity | None:
        stmt = select(MasterTax).where(
            MasterTax.id == tax_id,
            MasterTax.tenant_id == ctx.tenant_id,
            MasterTax.is_deleted.is_(False),
        )
        row = self.db.scalar(stmt)
        if row is None:
            return None
        for key, value in fields.items():
            if hasattr(row, key) and value is not None:
                setattr(row, key, value)
        row.updated_at = utcnow()
        row.updated_by = ctx.user_id
        row.version += 1
        self.db.flush()
        return self._to_entity(row)

    def soft_delete(self, ctx: TenantContext, tax_id: UUID) -> bool:
        stmt = select(MasterTax).where(
            MasterTax.id == tax_id,
            MasterTax.tenant_id == ctx.tenant_id,
        )
        row = self.db.scalar(stmt)
        if row is None or row.is_deleted:
            return False
        row.is_deleted = True
        row.deleted_at = utcnow()
        row.deleted_by = ctx.user_id
        self.db.flush()
        return True

    @staticmethod
    def _to_entity(row: MasterTax) -> TaxEntity:
        return TaxEntity(
            id=row.id,
            tenant_id=row.tenant_id,
            company_id=row.company_id,
            tax_code=row.tax_code,
            tax_name=row.tax_name,
            tax_type=row.tax_type,
            rate_percent=float(row.rate_percent),
            effective_from=row.effective_from,
            is_compound=row.is_compound,
            effective_to=row.effective_to,
            status=row.status,
            version=row.version,
            is_deleted=row.is_deleted,
        )
