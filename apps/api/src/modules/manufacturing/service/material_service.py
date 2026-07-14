"""Material issue and return services."""

from datetime import date, datetime, timezone
from decimal import Decimal
from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import NotFoundException
from modules.foundation.domain.value_objects import TenantContext
from modules.foundation.service.audit_service import AuditService
from modules.manufacturing.adapters.inventory_port import ManufacturingInventoryAdapter
from modules.manufacturing.domain.enums import MaterialDocStatus, MfgEntityType
from modules.manufacturing.models.material_issue import MfgMaterialIssue
from modules.manufacturing.models.material_return import MfgMaterialReturn
from modules.manufacturing.repository.material_issue_repository import MaterialIssueRepository
from modules.manufacturing.repository.material_return_repository import MaterialReturnRepository
from modules.manufacturing.repository.production_order_repository import ProductionOrderRepository
from modules.manufacturing.repository.wip_repository import WipRepository
from modules.manufacturing.service.document_number_service import DocumentNumberService
from modules.manufacturing.service.engines import (
    MaterialIssueEngine,
    MaterialReturnEngine,
    WipEngine,
)
from modules.manufacturing.service.mfg_scope_validator import MfgScopeValidator
from modules.manufacturing.service.posting_service import ManufacturingPostingService


class MaterialIssueService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._repo = MaterialIssueRepository(db)
        self._orders = ProductionOrderRepository(db)
        self._wip = WipRepository(db)
        self._numbers = DocumentNumberService(db)
        self._engine = MaterialIssueEngine()
        self._wip_engine = WipEngine()
        self._inv = ManufacturingInventoryAdapter(db)
        self._posting = ManufacturingPostingService(db)
        self._scope = MfgScopeValidator(db)
        self._audit = AuditService(db)

    def list_issues(self, ctx: TenantContext, company_id: UUID | None = None):
        cid = self._scope.resolve_company_id(ctx, company_id)
        return self._repo.list_issues(ctx, cid)

    def get_issue(self, ctx: TenantContext, issue_id: UUID) -> MfgMaterialIssue:
        row = self._repo.get(ctx, issue_id)
        if row is None:
            raise NotFoundException("Material issue not found")
        return row

    def create_issue(
        self,
        ctx: TenantContext,
        *,
        company_id: UUID,
        branch_id: UUID,
        production_order_id: UUID,
        warehouse_id: UUID,
        lines: list[dict],
        document_date: date | None = None,
        period_id: UUID | None = None,
    ) -> MfgMaterialIssue:
        self._scope.validate_company_access(ctx, company_id)
        branch_id = self._scope.require_branch(ctx, branch_id)
        number = self._numbers.generate(
            MfgEntityType.MATERIAL_ISSUE,
            company_id,
            model=MfgMaterialIssue,
            code_column="document_number",
        )
        header = self._repo.create(
            ctx,
            company_id=company_id,
            branch_id=branch_id,
            document_number=number,
            document_date=document_date or date.today(),
            production_order_id=production_order_id,
            warehouse_id=warehouse_id,
            status=MaterialDocStatus.DRAFT.value,
            period_id=period_id,
        )
        for i, ln in enumerate(lines, start=1):
            self._repo.add_line(
                ctx,
                header,
                line_number=ln.get("line_number", i),
                component_product_id=ln["component_product_id"],
                quantity=Decimal(str(ln["quantity"])),
                uom_id=ln["uom_id"],
                bom_line_id=ln.get("bom_line_id"),
                batch_reference=ln.get("batch_reference"),
                bin_reference=ln.get("bin_reference"),
                unit_cost=Decimal(str(ln["unit_cost"])) if ln.get("unit_cost") is not None else None,
                status="pending",
            )
        return self.get_issue(ctx, header.id)

    def confirm(
        self,
        ctx: TenantContext,
        issue_id: UUID,
        *,
        wip_account_id: UUID | None = None,
        inventory_account_id: UUID | None = None,
        fiscal_year_id: UUID | None = None,
    ) -> MfgMaterialIssue:
        header = self.get_issue(ctx, issue_id)
        order = self._orders.get(ctx, header.production_order_id)
        self._engine.validate_confirmable(header, order)
        material_total = Decimal("0")
        for ln in [x for x in header.lines if not x.is_deleted]:
            result = self._inv.issue_for_material_issue(
                ctx,
                company_id=header.company_id,
                branch_id=header.branch_id,
                warehouse_id=header.warehouse_id,
                product_id=ln.component_product_id,
                uom_id=ln.uom_id,
                quantity=Decimal(str(ln.quantity)),
                source_document_id=header.id,
                source_line_id=ln.id,
                bin_id=ln.bin_reference,
                batch_id=ln.batch_reference,
            )
            ln.inventory_event_id = getattr(result, "ledger_id", None) or getattr(result, "id", None)
            ln.status = "issued"
            cost = Decimal(str(ln.unit_cost or 0)) * Decimal(str(ln.quantity))
            material_total += cost
        wip = self._wip.get_by_order(ctx, header.production_order_id)
        if wip is not None and material_total > 0:
            self._wip_engine.add_material(wip, material_total)
        if (
            wip_account_id
            and inventory_account_id
            and material_total > 0
            and header.period_id is not None
        ):
            self._posting.post_material_issue(
                ctx,
                header,
                amount=material_total,
                wip_account_id=wip_account_id,
                inventory_account_id=inventory_account_id,
                fiscal_year_id=fiscal_year_id,
            )
        self._repo.update(
            ctx,
            issue_id,
            status=MaterialDocStatus.CONFIRMED.value,
            issued_at=datetime.now(timezone.utc),
            issued_by=ctx.user_id,
        )
        if order and order.status == "released":
            order.status = "in_progress"
            if order.actual_start is None:
                order.actual_start = datetime.now(timezone.utc)
        self._audit.log_entity_change(
            tenant_id=ctx.tenant_id,
            entity_name="mfg_material_issue",
            entity_id=issue_id,
            operation="confirm",
            performed_by=ctx.user_id,
        )
        return self.get_issue(ctx, issue_id)


class MaterialReturnService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._repo = MaterialReturnRepository(db)
        self._orders = ProductionOrderRepository(db)
        self._wip = WipRepository(db)
        self._numbers = DocumentNumberService(db)
        self._engine = MaterialReturnEngine()
        self._wip_engine = WipEngine()
        self._inv = ManufacturingInventoryAdapter(db)
        self._posting = ManufacturingPostingService(db)
        self._scope = MfgScopeValidator(db)
        self._audit = AuditService(db)

    def list_returns(self, ctx: TenantContext, company_id: UUID | None = None):
        cid = self._scope.resolve_company_id(ctx, company_id)
        return self._repo.list_returns(ctx, cid)

    def get_return(self, ctx: TenantContext, return_id: UUID) -> MfgMaterialReturn:
        row = self._repo.get(ctx, return_id)
        if row is None:
            raise NotFoundException("Material return not found")
        return row

    def create_return(
        self,
        ctx: TenantContext,
        *,
        company_id: UUID,
        branch_id: UUID,
        production_order_id: UUID,
        warehouse_id: UUID,
        lines: list[dict],
        document_date: date | None = None,
        period_id: UUID | None = None,
    ) -> MfgMaterialReturn:
        self._scope.validate_company_access(ctx, company_id)
        branch_id = self._scope.require_branch(ctx, branch_id)
        number = self._numbers.generate(
            MfgEntityType.MATERIAL_RETURN,
            company_id,
            model=MfgMaterialReturn,
            code_column="document_number",
        )
        header = self._repo.create(
            ctx,
            company_id=company_id,
            branch_id=branch_id,
            document_number=number,
            document_date=document_date or date.today(),
            production_order_id=production_order_id,
            warehouse_id=warehouse_id,
            status=MaterialDocStatus.DRAFT.value,
            period_id=period_id,
        )
        for i, ln in enumerate(lines, start=1):
            self._repo.add_line(
                ctx,
                header,
                line_number=ln.get("line_number", i),
                component_product_id=ln["component_product_id"],
                quantity=Decimal(str(ln["quantity"])),
                uom_id=ln["uom_id"],
                bom_line_id=ln.get("bom_line_id"),
                batch_reference=ln.get("batch_reference"),
                bin_reference=ln.get("bin_reference"),
                unit_cost=Decimal(str(ln["unit_cost"])) if ln.get("unit_cost") is not None else None,
                status="pending",
            )
        return self.get_return(ctx, header.id)

    def confirm(
        self,
        ctx: TenantContext,
        return_id: UUID,
        *,
        wip_account_id: UUID | None = None,
        inventory_account_id: UUID | None = None,
        fiscal_year_id: UUID | None = None,
    ) -> MfgMaterialReturn:
        header = self.get_return(ctx, return_id)
        order = self._orders.get(ctx, header.production_order_id)
        self._engine.validate_confirmable(header, order)
        material_total = Decimal("0")
        for ln in [x for x in header.lines if not x.is_deleted]:
            unit_cost = Decimal(str(ln.unit_cost or 0))
            result = self._inv.receive_for_material_return(
                ctx,
                company_id=header.company_id,
                branch_id=header.branch_id,
                warehouse_id=header.warehouse_id,
                product_id=ln.component_product_id,
                uom_id=ln.uom_id,
                quantity=Decimal(str(ln.quantity)),
                source_document_id=header.id,
                source_line_id=ln.id,
                unit_cost=unit_cost if unit_cost > 0 else None,
                bin_id=ln.bin_reference,
                batch_id=ln.batch_reference,
            )
            ln.inventory_event_id = getattr(result, "ledger_id", None) or getattr(result, "id", None)
            ln.status = "returned"
            material_total += unit_cost * Decimal(str(ln.quantity))
        wip = self._wip.get_by_order(ctx, header.production_order_id)
        if wip is not None and material_total > 0:
            self._wip_engine.relieve_material(wip, material_total)
        if (
            wip_account_id
            and inventory_account_id
            and material_total > 0
            and header.period_id is not None
        ):
            self._posting.post_material_return(
                ctx,
                header,
                amount=material_total,
                wip_account_id=wip_account_id,
                inventory_account_id=inventory_account_id,
                fiscal_year_id=fiscal_year_id,
            )
        self._repo.update(
            ctx,
            return_id,
            status=MaterialDocStatus.CONFIRMED.value,
            returned_at=datetime.now(timezone.utc),
            returned_by=ctx.user_id,
        )
        self._audit.log_entity_change(
            tenant_id=ctx.tenant_id,
            entity_name="mfg_material_return",
            entity_id=return_id,
            operation="confirm",
            performed_by=ctx.user_id,
        )
        return self.get_return(ctx, return_id)
