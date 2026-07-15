"""MaintenancePlanService."""

from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import NotFoundException
from modules.asset.domain.enums import AstEntityType
from modules.asset.models import AstAssetMaintenancePlan
from modules.asset.repository.asset_maintenance_plan_repository import (
    AssetMaintenancePlanRepository,
)
from modules.asset.service.asset_scope_validator import AssetScopeValidator
from modules.asset.service.document_number_service import DocumentNumberService
from modules.asset.service.engines import AssetMaintenancePlanEngine
from modules.foundation.domain.value_objects import TenantContext
from modules.foundation.service.audit_service import AuditService


class MaintenancePlanService:
    def __init__(self, db: Session) -> None:
        self._repo = AssetMaintenancePlanRepository(db)
        self._scope = AssetScopeValidator(db)
        self._numbers = DocumentNumberService(db)
        self._engine = AssetMaintenancePlanEngine()
        self._audit = AuditService(db)
        self._db = db

    def list(self, ctx: TenantContext, company_id: UUID | None = None):
        cid = self._scope.resolve_company_id(ctx, company_id)
        return self._repo.list_rows(ctx, cid)

    def get(self, ctx: TenantContext, row_id: UUID) -> AstAssetMaintenancePlan:
        row = self._repo.get(ctx, row_id)
        if row is None:
            raise NotFoundException("MaintenancePlanService not found")
        return row

    def create(self, ctx: TenantContext, company_id: UUID | None = None, **fields):

        cid = self._scope.resolve_company_id(ctx, company_id)
        doc = self._numbers.generate(AstEntityType.MAINTENANCE_PLAN, cid, AstAssetMaintenancePlan, "document_number")
        return self._repo.create(ctx, company_id=cid, document_number=doc, **fields)

    def update(self, ctx: TenantContext, row_id: UUID, **fields):
        self.get(ctx, row_id)
        row = self._repo.update(ctx, row_id, **fields)
        if row is None:
            raise NotFoundException("MaintenancePlanService not found")
        return row

    def activate(self, ctx: TenantContext, row_id: UUID):
        row = self.get(ctx, row_id)
        self._engine.activate(row)
        return self._repo.update(ctx, row_id, status=row.status)

    def pause(self, ctx: TenantContext, row_id: UUID):
        row = self.get(ctx, row_id)
        self._engine.pause(row)
        return self._repo.update(ctx, row_id, status=row.status)

    def close(self, ctx: TenantContext, row_id: UUID):
        row = self.get(ctx, row_id)
        self._engine.close(row)
        return self._repo.update(ctx, row_id, status=row.status)

