"""BOM application service."""

from datetime import date
from decimal import Decimal
from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import NotFoundException
from modules.foundation.domain.value_objects import TenantContext
from modules.foundation.service.audit_service import AuditService
from modules.manufacturing.domain.enums import BomStatus, MfgEntityType
from modules.manufacturing.models.bom import MfgBom
from modules.manufacturing.repository.bom_repository import BomRepository
from modules.manufacturing.service.document_number_service import DocumentNumberService
from modules.manufacturing.service.engines import BomEngine
from modules.manufacturing.service.mfg_scope_validator import MfgScopeValidator


class BomService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._repo = BomRepository(db)
        self._numbers = DocumentNumberService(db)
        self._engine = BomEngine()
        self._scope = MfgScopeValidator(db)
        self._audit = AuditService(db)

    def list_boms(self, ctx: TenantContext, company_id: UUID | None = None, product_id: UUID | None = None):
        cid = self._scope.resolve_company_id(ctx, company_id)
        return self._repo.list_boms(ctx, cid, product_id)

    def get_bom(self, ctx: TenantContext, bom_id: UUID) -> MfgBom:
        row = self._repo.get(ctx, bom_id)
        if row is None:
            raise NotFoundException("BOM not found")
        return row

    def create_bom(
        self,
        ctx: TenantContext,
        *,
        company_id: UUID,
        product_id: UUID,
        revision: str,
        effective_from: date,
        lines: list[dict],
        branch_id: UUID | None = None,
        effective_to: date | None = None,
        notes: str | None = None,
    ) -> MfgBom:
        self._scope.validate_company_access(ctx, company_id)
        number = self._numbers.generate(
            MfgEntityType.BOM, company_id, model=MfgBom, code_column="bom_number"
        )
        bom = self._repo.create(
            ctx,
            company_id=company_id,
            branch_id=branch_id,
            bom_number=number,
            product_id=product_id,
            revision=revision,
            effective_from=effective_from,
            effective_to=effective_to,
            notes=notes,
            status=BomStatus.DRAFT.value,
        )
        for i, ln in enumerate(lines, start=1):
            self._repo.add_line(
                ctx,
                bom,
                line_number=ln.get("line_number", i),
                component_product_id=ln["component_product_id"],
                quantity=Decimal(str(ln["quantity"])),
                uom_id=ln["uom_id"],
                scrap_percent=Decimal(str(ln.get("scrap_percent", 0))),
                alternate_product_id=ln.get("alternate_product_id"),
                is_optional=bool(ln.get("is_optional", False)),
                status=ln.get("status", "active"),
            )
        self._audit.log_entity_change(
            tenant_id=ctx.tenant_id,
            entity_name="mfg_bom",
            entity_id=bom.id,
            operation="create",
            performed_by=ctx.user_id,
        )
        return self.get_bom(ctx, bom.id)

    def update_bom(self, ctx: TenantContext, bom_id: UUID, **fields) -> MfgBom:
        bom = self.get_bom(ctx, bom_id)
        if bom.status != BomStatus.DRAFT.value:
            fields = {k: v for k, v in fields.items() if k in {"notes", "effective_to"}}
        row = self._repo.update(ctx, bom_id, **fields)
        assert row is not None
        return self.get_bom(ctx, bom_id)

    def submit(self, ctx: TenantContext, bom_id: UUID) -> MfgBom:
        bom = self.get_bom(ctx, bom_id)
        self._engine.validate_activatable(bom)
        self._repo.update(ctx, bom_id, workflow_status="submitted")
        return self.get_bom(ctx, bom_id)

    def approve_activate(self, ctx: TenantContext, bom_id: UUID) -> MfgBom:
        bom = self.get_bom(ctx, bom_id)
        self._engine.validate_activatable(bom)
        existing = self._repo.find_active_for_product(ctx, bom.company_id, bom.product_id)
        if existing and existing.id != bom.id:
            self._engine.ensure_no_active_conflict(existing)
        self._repo.update(ctx, bom_id, status=BomStatus.ACTIVE.value, workflow_status="approved")
        self._audit.log_entity_change(
            tenant_id=ctx.tenant_id,
            entity_name="mfg_bom",
            entity_id=bom_id,
            operation="activate",
            performed_by=ctx.user_id,
        )
        return self.get_bom(ctx, bom_id)

    def explode(self, ctx: TenantContext, bom_id: UUID, planned_qty: Decimal):
        bom = self.get_bom(ctx, bom_id)
        return self._engine.explode(bom, planned_qty)
