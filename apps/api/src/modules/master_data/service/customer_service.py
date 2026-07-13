"""Customer service."""

from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import NotFoundException
from modules.foundation.domain.value_objects import TenantContext
from modules.foundation.service.audit_service import AuditService
from modules.master_data.domain.enums import MasterEntityType
from modules.master_data.models.party import MasterCustomer
from modules.master_data.repository.customer_repository import CustomerRepository
from modules.master_data.service.code_generator_service import CodeGeneratorService
from modules.master_data.service.duplicate_checker_service import DuplicateCheckerService
from modules.master_data.service.governance_service import GovernanceService
from modules.master_data.service.master_scope_validator import MasterScopeValidator


class CustomerService:
    def __init__(self, db: Session) -> None:
        self._repo = CustomerRepository(db)
        self._audit = AuditService(db)
        self._codes = CodeGeneratorService(db)
        self._duplicates = DuplicateCheckerService(db)
        self._scope = MasterScopeValidator(db)
        self._governance = GovernanceService(db)

    def list_customers(
        self,
        ctx: TenantContext,
        *,
        company_id: UUID | None = None,
        branch_id: UUID | None = None,
    ):
        if company_id:
            self._scope.validate_company_access(ctx, company_id)
        if branch_id:
            self._scope.validate_branch_access(ctx, branch_id)
        return self._repo.list_customers(ctx, company_id=company_id, branch_id=branch_id)

    def get_customer(self, ctx: TenantContext, customer_id: UUID):
        customer = self._repo.get_by_id(ctx, customer_id)
        if customer is None:
            raise NotFoundException("Customer not found")
        self._scope.validate_company_access(ctx, customer.company_id)
        self._scope.validate_branch_access(ctx, customer.branch_id)
        return customer

    def create_customer(
        self,
        ctx: TenantContext,
        *,
        company_id: UUID | None = None,
        branch_id: UUID,
        customer_code: str | None = None,
        customer_name: str,
        customer_type: str,
        billing_address_json: dict,
        shipping_address_json: dict | None = None,
        tax_number: str | None = None,
        email: str | None = None,
        mobile: str | None = None,
        credit_limit: float | None = None,
        currency_code: str | None = None,
    ):
        resolved_company_id = self._scope.resolve_company_id(ctx, company_id)
        self._scope.validate_branch_access(ctx, branch_id)

        if customer_code is None:
            customer_code = self._codes.generate(
                MasterEntityType.CUSTOMER,
                resolved_company_id,
                model=MasterCustomer,
                code_column="customer_code",
            )
        else:
            self._duplicates.ensure_unique_code(
                model=MasterCustomer,
                company_id=resolved_company_id,
                code=customer_code,
                code_field="customer_code",
                label="Customer",
            )

        customer = self._repo.create(
            ctx,
            company_id=resolved_company_id,
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
        )
        self._audit.log_entity_change(
            tenant_id=ctx.tenant_id,
            entity_name="master_customer",
            entity_id=customer.id,
            operation="create",
            performed_by=ctx.user_id,
            new_value={"customer_code": customer_code, "branch_id": str(branch_id)},
        )
        return customer

    def update_customer(self, ctx: TenantContext, customer_id: UUID, **fields):
        self.get_customer(ctx, customer_id)
        if "branch_id" in fields and fields["branch_id"] is not None:
            self._scope.validate_branch_access(ctx, fields["branch_id"])

        updated = self._repo.update(ctx, customer_id, **fields)
        if updated is None:
            raise NotFoundException("Customer not found")
        self._audit.log_entity_change(
            tenant_id=ctx.tenant_id,
            entity_name="master_customer",
            entity_id=customer_id,
            operation="update",
            performed_by=ctx.user_id,
            new_value=fields,
        )
        return updated

    def delete_customer(self, ctx: TenantContext, customer_id: UUID) -> None:
        self.get_customer(ctx, customer_id)
        if not self._repo.soft_delete(ctx, customer_id):
            raise NotFoundException("Customer not found")
        self._audit.log_entity_change(
            tenant_id=ctx.tenant_id,
            entity_name="master_customer",
            entity_id=customer_id,
            operation="delete",
            performed_by=ctx.user_id,
        )

    def submit_for_approval(self, ctx: TenantContext, customer_id: UUID):
        self.get_customer(ctx, customer_id)
        return self._governance.submit_for_approval(
            ctx,
            entity_name="master_customer",
            entity_id=customer_id,
        )
