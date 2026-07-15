"""Depreciation service — posts via Finance PostingService only."""

from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy.orm import Session

from core.exceptions import NotFoundException
from modules.asset.adapters.finance_port import AssetFinanceAdapter
from modules.asset.domain.enums import AstEntityType
from modules.asset.models import AstAssetDepreciation
from modules.asset.repository.asset_depreciation_repository import AssetDepreciationRepository
from modules.asset.service.asset_scope_validator import AssetScopeValidator
from modules.asset.service.document_number_service import DocumentNumberService
from modules.asset.service.engines import AssetDepreciationEngine
from modules.foundation.domain.value_objects import TenantContext
from modules.foundation.service.audit_service import AuditService


class DepreciationService:
    def __init__(self, db: Session) -> None:
        self._repo = AssetDepreciationRepository(db)
        self._scope = AssetScopeValidator(db)
        self._numbers = DocumentNumberService(db)
        self._engine = AssetDepreciationEngine()
        self._finance = AssetFinanceAdapter(db)
        self._audit = AuditService(db)

    def list(self, ctx: TenantContext, company_id: UUID | None = None):
        cid = self._scope.resolve_company_id(ctx, company_id)
        return self._repo.list_rows(ctx, cid)

    def get(self, ctx: TenantContext, row_id: UUID) -> AstAssetDepreciation:
        row = self._repo.get(ctx, row_id)
        if row is None:
            raise NotFoundException("DepreciationService not found")
        return row

    def create(self, ctx: TenantContext, company_id: UUID | None = None, **fields):
        cid = self._scope.resolve_company_id(ctx, company_id)
        doc = self._numbers.generate(
            AstEntityType.DEPRECIATION, cid, AstAssetDepreciation, "document_number"
        )
        fields.setdefault("idempotency_key", str(uuid4()))
        return self._repo.create(ctx, company_id=cid, document_number=doc, **fields)

    def update(self, ctx: TenantContext, row_id: UUID, **fields):
        self.get(ctx, row_id)
        row = self._repo.update(ctx, row_id, **fields)
        if row is None:
            raise NotFoundException("DepreciationService not found")
        return row

    def calculate(self, ctx: TenantContext, row_id: UUID):
        row = self.get(ctx, row_id)
        self._engine.calculate(row)
        return self._repo.update(ctx, row_id, status=row.status)

    def post(
        self,
        ctx: TenantContext,
        row_id: UUID,
        debit_account_id: UUID,
        credit_account_id: UUID,
        fiscal_year_id: UUID | None = None,
    ):
        row = self.get(ctx, row_id)
        try:
            journal_id = self._finance.post_depreciation(
                ctx,
                row,
                amount=Decimal(str(row.depreciation_amount or 0)),
                debit_account_id=debit_account_id,
                credit_account_id=credit_account_id,
                fiscal_year_id=fiscal_year_id,
            )
            self._engine.post(row)
            updated = self._repo.update(
                ctx, row_id, status=row.status, finance_journal_id=journal_id
            )
            self._audit.log_entity_change(
                tenant_id=ctx.tenant_id,
                entity_name="ast_asset_depreciation",
                entity_id=row_id,
                operation="post",
                performed_by=ctx.user_id,
                new_value={"finance_journal_id": str(journal_id)},
            )
            return updated
        except Exception:
            self._engine.fail(row)
            self._repo.update(ctx, row_id, status=row.status)
            raise
