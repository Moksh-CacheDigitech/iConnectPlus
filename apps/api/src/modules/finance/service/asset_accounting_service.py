"""Asset accounting service."""

from datetime import date
from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import NotFoundException
from modules.finance.domain.enums import FinanceEntityType
from modules.finance.models.asset import FinAssetTransaction
from modules.finance.repository.asset_repository import AssetRepository
from modules.finance.service.document_number_service import DocumentNumberService
from modules.finance.service.finance_scope_validator import FinanceScopeValidator
from modules.foundation.domain.value_objects import TenantContext
from modules.foundation.service.audit_service import AuditService


class AssetAccountingService:
    def __init__(self, db: Session) -> None:
        self._repo = AssetRepository(db)
        self._scope = FinanceScopeValidator(db)
        self._numbers = DocumentNumberService(db)
        self._audit = AuditService(db)

    def list_transactions(self, ctx: TenantContext, company_id: UUID | None = None):
        cid = self._scope.resolve_company_id(ctx, company_id)
        return self._repo.list_transactions(ctx, cid)

    def create_transaction(
        self,
        ctx: TenantContext,
        *,
        company_id: UUID | None = None,
        branch_id: UUID,
        asset_id: UUID,
        transaction_date: date,
        transaction_type: str,
        amount: float,
        period_id: UUID,
        currency_code: str = "INR",
        description: str | None = None,
    ):
        cid = self._scope.resolve_company_id(ctx, company_id)
        self._scope.validate_branch_access(ctx, branch_id)
        txn_number = self._numbers.generate(
            FinanceEntityType.ASSET_TRANSACTION,
            cid,
            model=FinAssetTransaction,
            code_column="transaction_number",
        )
        txn = self._repo.create_transaction(
            ctx,
            company_id=cid,
            branch_id=branch_id,
            transaction_number=txn_number,
            transaction_date=transaction_date,
            asset_id=asset_id,
            transaction_type=transaction_type,
            amount=amount,
            currency_code=currency_code,
            period_id=period_id,
            status="draft",
            description=description,
        )
        self._audit.log_entity_change(
            tenant_id=ctx.tenant_id,
            entity_name="fin_asset_transaction",
            entity_id=txn.id,
            operation="create",
            performed_by=ctx.user_id,
        )
        return txn

    def get_transaction(self, ctx: TenantContext, transaction_id: UUID):
        txn = self._repo.get_transaction(ctx, transaction_id)
        if txn is None:
            raise NotFoundException("Asset transaction not found")
        return txn
