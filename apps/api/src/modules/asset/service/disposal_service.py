"""Disposal service — Finance post + master sync."""

from decimal import Decimal
from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import NotFoundException
from modules.asset.adapters.finance_port import AssetFinanceAdapter
from modules.asset.adapters.master_data_port import AssetMasterDataAdapter
from modules.asset.domain.enums import AstEntityType
from modules.asset.models import AstAssetDisposal
from modules.asset.repository.asset_disposal_repository import AssetDisposalRepository
from modules.asset.repository.asset_repository import AssetRepository
from modules.asset.service.asset_scope_validator import AssetScopeValidator
from modules.asset.service.document_number_service import DocumentNumberService
from modules.asset.service.engines import AssetDisposalEngine, AssetEngine
from modules.foundation.domain.value_objects import TenantContext
from modules.foundation.service.audit_service import AuditService


class DisposalService:
    def __init__(self, db: Session) -> None:
        self._repo = AssetDisposalRepository(db)
        self._assets = AssetRepository(db)
        self._scope = AssetScopeValidator(db)
        self._numbers = DocumentNumberService(db)
        self._engine = AssetDisposalEngine()
        self._asset_engine = AssetEngine()
        self._finance = AssetFinanceAdapter(db)
        self._master = AssetMasterDataAdapter(db)
        self._audit = AuditService(db)

    def list(self, ctx: TenantContext, company_id: UUID | None = None):
        cid = self._scope.resolve_company_id(ctx, company_id)
        return self._repo.list_rows(ctx, cid)

    def get(self, ctx: TenantContext, row_id: UUID) -> AstAssetDisposal:
        row = self._repo.get(ctx, row_id)
        if row is None:
            raise NotFoundException("DisposalService not found")
        return row

    def create(self, ctx: TenantContext, *, branch_id: UUID, company_id: UUID | None = None, **fields):
        cid = self._scope.resolve_company_id(ctx, company_id)
        self._scope.validate_branch_access(ctx, branch_id)
        doc = self._numbers.generate(AstEntityType.DISPOSAL, cid, AstAssetDisposal, "document_number")
        return self._repo.create(ctx, company_id=cid, branch_id=branch_id, document_number=doc, **fields)

    def update(self, ctx: TenantContext, row_id: UUID, **fields):
        self.get(ctx, row_id)
        row = self._repo.update(ctx, row_id, **fields)
        if row is None:
            raise NotFoundException("DisposalService not found")
        return row

    def submit(self, ctx: TenantContext, row_id: UUID):
        row = self.get(ctx, row_id)
        self._engine.submit(row)
        return self._repo.update(ctx, row_id, status=row.status)

    def approve(self, ctx: TenantContext, row_id: UUID):
        row = self.get(ctx, row_id)
        self._engine.approve(row)
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
        journal_id = self._finance.post_disposal(
            ctx,
            row,
            amount=Decimal(str(row.book_value_at_disposal or row.proceeds_amount or 0)),
            debit_account_id=debit_account_id,
            credit_account_id=credit_account_id,
            fiscal_year_id=fiscal_year_id,
        )
        self._engine.post(row)
        updated = self._repo.update(ctx, row_id, status=row.status, finance_journal_id=journal_id)
        asset = self._assets.get(ctx, row.asset_id)
        if asset is not None:
            self._asset_engine.dispose(asset)
            self._assets.update(ctx, asset.id, status=asset.status)
            if asset.master_asset_id is not None:
                self._master.mark_master_disposed(ctx, asset.master_asset_id)
        self._audit.log_entity_change(
            tenant_id=ctx.tenant_id,
            entity_name="ast_asset_disposal",
            entity_id=row_id,
            operation="post",
            performed_by=ctx.user_id,
            new_value={"finance_journal_id": str(journal_id)},
        )
        return updated
