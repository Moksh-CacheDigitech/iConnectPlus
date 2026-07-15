"""Asset register service — C-01 master_asset link on approve."""

from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import NotFoundException
from modules.asset.adapters.master_data_port import AssetMasterDataAdapter
from modules.asset.domain.enums import AstEntityType
from modules.asset.models import AstAsset
from modules.asset.repository.asset_repository import AssetRepository
from modules.asset.service.asset_scope_validator import AssetScopeValidator
from modules.asset.service.document_number_service import DocumentNumberService
from modules.asset.service.engines import AssetEngine
from modules.foundation.domain.value_objects import TenantContext
from modules.foundation.service.audit_service import AuditService


class AssetService:
    def __init__(self, db: Session) -> None:
        self._repo = AssetRepository(db)
        self._scope = AssetScopeValidator(db)
        self._numbers = DocumentNumberService(db)
        self._engine = AssetEngine()
        self._audit = AuditService(db)
        self._master = AssetMasterDataAdapter(db)
        self._db = db

    def list(self, ctx: TenantContext, company_id: UUID | None = None):
        cid = self._scope.resolve_company_id(ctx, company_id)
        return self._repo.list_rows(ctx, cid)

    def get(self, ctx: TenantContext, row_id: UUID) -> AstAsset:
        row = self._repo.get(ctx, row_id)
        if row is None:
            raise NotFoundException("AssetService not found")
        return row

    def create(self, ctx: TenantContext, *, branch_id: UUID, company_id: UUID | None = None, **fields):
        cid = self._scope.resolve_company_id(ctx, company_id)
        self._scope.validate_branch_access(ctx, branch_id)
        doc = self._numbers.generate(AstEntityType.ASSET, cid, AstAsset, "document_number")
        asset_code = fields.pop("asset_code", None) or doc
        return self._repo.create(
            ctx,
            company_id=cid,
            branch_id=branch_id,
            document_number=doc,
            asset_code=asset_code,
            **fields,
        )

    def update(self, ctx: TenantContext, row_id: UUID, **fields):
        self.get(ctx, row_id)
        row = self._repo.update(ctx, row_id, **fields)
        if row is None:
            raise NotFoundException("AssetService not found")
        return row

    def submit(self, ctx: TenantContext, row_id: UUID):
        row = self.get(ctx, row_id)
        self._engine.submit(row)
        return self._repo.update(ctx, row_id, status=row.status)

    def approve(self, ctx: TenantContext, row_id: UUID):
        row = self.get(ctx, row_id)
        self._engine.approve(row)
        if row.master_asset_id is None:
            master = self._master.create_or_link_master_asset(ctx, row)
            row.master_asset_id = master.id
        self._engine.activate(row)
        updated = self._repo.update(
            ctx,
            row_id,
            status=row.status,
            master_asset_id=row.master_asset_id,
        )
        self._audit.log_entity_change(
            tenant_id=ctx.tenant_id,
            entity_name="ast_asset",
            entity_id=row_id,
            operation="approve",
            performed_by=ctx.user_id,
            new_value={"master_asset_id": str(row.master_asset_id), "status": row.status},
        )
        return updated
