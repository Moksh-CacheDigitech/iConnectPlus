"""Customer repository."""

from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from modules.foundation.domain.value_objects import TenantContext
from modules.master_data.domain.entities import CustomerEntity
from modules.master_data.models.party import MasterCustomer
from modules.master_data.repository.base import MasterScopedRepository, utcnow


class CustomerRepository(MasterScopedRepository):
    def __init__(self, db: Session) -> None:
        super().__init__(db)

    def list_customers(
        self,
        ctx: TenantContext,
        *,
        company_id: UUID | None = None,
        branch_id: UUID | None = None,
    ) -> list[CustomerEntity]:
        stmt = select(MasterCustomer)
        stmt = self.apply_master_filter(stmt, MasterCustomer, ctx, branch_scoped=True)
        if company_id:
            stmt = stmt.where(MasterCustomer.company_id == company_id)
        if branch_id:
            stmt = stmt.where(MasterCustomer.branch_id == branch_id)
        return [self._to_entity(r) for r in self.db.scalars(stmt).all()]

    def get_by_id(self, ctx: TenantContext, customer_id: UUID) -> CustomerEntity | None:
        stmt = select(MasterCustomer).where(
            MasterCustomer.id == customer_id,
            MasterCustomer.tenant_id == ctx.tenant_id,
            MasterCustomer.is_deleted.is_(False),
        )
        row = self.db.scalar(stmt)
        return self._to_entity(row) if row else None

    def get_by_code(
        self, ctx: TenantContext, company_id: UUID, customer_code: str
    ) -> MasterCustomer | None:
        stmt = select(MasterCustomer).where(
            MasterCustomer.tenant_id == ctx.tenant_id,
            MasterCustomer.company_id == company_id,
            MasterCustomer.customer_code == customer_code,
            MasterCustomer.is_deleted.is_(False),
        )
        return self.db.scalar(stmt)

    def create(
        self,
        ctx: TenantContext,
        *,
        company_id: UUID,
        branch_id: UUID,
        customer_code: str,
        customer_name: str,
        customer_type: str,
        billing_address_json: dict,
        shipping_address_json: dict | None = None,
        tax_number: str | None = None,
        email: str | None = None,
        mobile: str | None = None,
        credit_limit: float | None = None,
        currency_code: str | None = None,
    ) -> CustomerEntity:
        row = MasterCustomer(
            id=uuid4(),
            tenant_id=ctx.tenant_id,
            company_id=company_id,
            branch_id=branch_id,
            customer_code=customer_code,
            customer_name=customer_name,
            customer_type=customer_type,
            billing_address_json=billing_address_json,
            shipping_address_json=shipping_address_json,
            tax_number=tax_number,
            email=email,
            mobile=mobile,
            credit_limit=credit_limit,
            currency_code=currency_code,
            status="draft",
            created_by=ctx.user_id,
            updated_by=ctx.user_id,
        )
        self.db.add(row)
        self.db.flush()
        return self._to_entity(row)

    def update(
        self, ctx: TenantContext, customer_id: UUID, **fields: object
    ) -> CustomerEntity | None:
        stmt = select(MasterCustomer).where(
            MasterCustomer.id == customer_id,
            MasterCustomer.tenant_id == ctx.tenant_id,
            MasterCustomer.is_deleted.is_(False),
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

    def soft_delete(self, ctx: TenantContext, customer_id: UUID) -> bool:
        stmt = select(MasterCustomer).where(
            MasterCustomer.id == customer_id,
            MasterCustomer.tenant_id == ctx.tenant_id,
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
    def _to_entity(row: MasterCustomer) -> CustomerEntity:
        return CustomerEntity(
            id=row.id,
            tenant_id=row.tenant_id,
            company_id=row.company_id,
            branch_id=row.branch_id,
            customer_code=row.customer_code,
            customer_name=row.customer_name,
            customer_type=row.customer_type,
            billing_address_json=row.billing_address_json,
            shipping_address_json=row.shipping_address_json,
            tax_number=row.tax_number,
            email=row.email,
            mobile=row.mobile,
            credit_limit=float(row.credit_limit) if row.credit_limit is not None else None,
            currency_code=row.currency_code,
            status=row.status,
            version=row.version,
            is_deleted=row.is_deleted,
        )
