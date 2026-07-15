"""AssetReportService."""

from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import NotFoundException
from modules.asset.domain.enums import AstEntityType
from modules.asset.models import AstAssetReport
from modules.asset.repository.asset_report_repository import AssetReportRepository
from modules.asset.service.asset_scope_validator import AssetScopeValidator
from modules.asset.service.document_number_service import DocumentNumberService
from modules.asset.service.engines import AssetReportEngine
from modules.foundation.domain.value_objects import TenantContext
from modules.foundation.service.audit_service import AuditService


class AssetReportService:
    def __init__(self, db: Session) -> None:
        self._repo = AssetReportRepository(db)
        self._scope = AssetScopeValidator(db)
        self._numbers = DocumentNumberService(db)
        self._engine = AssetReportEngine()
        self._audit = AuditService(db)
        self._db = db

    def list(self, ctx: TenantContext, company_id: UUID | None = None):
        cid = self._scope.resolve_company_id(ctx, company_id)
        return self._repo.list_rows(ctx, cid)

    def get(self, ctx: TenantContext, row_id: UUID) -> AstAssetReport:
        row = self._repo.get(ctx, row_id)
        if row is None:
            raise NotFoundException("AssetReportService not found")
        return row

    def create(self, ctx: TenantContext, company_id: UUID | None = None, **fields):

        cid = self._scope.resolve_company_id(ctx, company_id)
        doc = self._numbers.generate(AstEntityType.REPORT, cid, AstAssetReport, "report_code")
        return self._repo.create(ctx, company_id=cid, report_code=doc, **fields)

    def update(self, ctx: TenantContext, row_id: UUID, **fields):
        self.get(ctx, row_id)
        row = self._repo.update(ctx, row_id, **fields)
        if row is None:
            raise NotFoundException("AssetReportService not found")
        return row

    def finalize(self, ctx: TenantContext, row_id: UUID):
        row = self.get(ctx, row_id)
        self._engine.finalize(row)
        return self._repo.update(ctx, row_id, status=row.status)

