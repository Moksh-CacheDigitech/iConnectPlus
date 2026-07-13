"""Chart of accounts service."""

from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import NotFoundException
from modules.finance.repository.coa_repository import COARepository
from modules.finance.service.finance_scope_validator import FinanceScopeValidator
from modules.foundation.domain.value_objects import TenantContext
from modules.foundation.service.audit_service import AuditService


class ChartOfAccountService:
    def __init__(self, db: Session) -> None:
        self._repo = COARepository(db)
        self._scope = FinanceScopeValidator(db)
        self._audit = AuditService(db)

    def list_account_groups(self, ctx: TenantContext, company_id: UUID | None = None):
        cid = self._scope.resolve_company_id(ctx, company_id)
        return self._repo.list_account_groups(ctx, cid)

    def create_account_group(self, ctx: TenantContext, company_id: UUID | None = None, **fields):
        cid = self._scope.resolve_company_id(ctx, company_id)
        group = self._repo.create_account_group(ctx, company_id=cid, **fields)
        self._audit.log_entity_change(
            tenant_id=ctx.tenant_id,
            entity_name="fin_account_group",
            entity_id=group.id,
            operation="create",
            performed_by=ctx.user_id,
        )
        return group

    def list_accounts(self, ctx: TenantContext, company_id: UUID | None = None):
        cid = self._scope.resolve_company_id(ctx, company_id)
        return self._repo.list_accounts(ctx, cid)

    def get_account(self, ctx: TenantContext, account_id: UUID):
        account = self._repo.get_account(ctx, account_id)
        if account is None:
            raise NotFoundException("Account not found")
        self._scope.validate_company_access(ctx, account.company_id)
        return account

    def create_account(self, ctx: TenantContext, company_id: UUID | None = None, **fields):
        cid = self._scope.resolve_company_id(ctx, company_id)
        account = self._repo.create_account(ctx, company_id=cid, **fields)
        self._audit.log_entity_change(
            tenant_id=ctx.tenant_id,
            entity_name="fin_chart_of_account",
            entity_id=account.id,
            operation="create",
            performed_by=ctx.user_id,
        )
        return account

    def update_account(self, ctx: TenantContext, account_id: UUID, **fields):
        self.get_account(ctx, account_id)
        updated = self._repo.update_account(ctx, account_id, **fields)
        if updated is None:
            raise NotFoundException("Account not found")
        self._audit.log_entity_change(
            tenant_id=ctx.tenant_id,
            entity_name="fin_chart_of_account",
            entity_id=account_id,
            operation="update",
            performed_by=ctx.user_id,
            new_value=fields,
        )
        return updated
