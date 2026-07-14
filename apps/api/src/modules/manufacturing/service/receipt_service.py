"""Production receipt service."""

from datetime import date, datetime, timezone
from decimal import Decimal
from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import NotFoundException
from modules.foundation.domain.value_objects import TenantContext
from modules.foundation.service.audit_service import AuditService
from modules.manufacturing.adapters.inventory_port import ManufacturingInventoryAdapter
from modules.manufacturing.domain.enums import MaterialDocStatus, MfgEntityType
from modules.manufacturing.models.production_receipt import MfgProductionReceipt
from modules.manufacturing.repository.production_order_repository import ProductionOrderRepository
from modules.manufacturing.repository.production_receipt_repository import (
    ProductionReceiptRepository,
)
from modules.manufacturing.repository.wip_repository import WipRepository
from modules.manufacturing.service.document_number_service import DocumentNumberService
from modules.manufacturing.service.engines import (
    ProductionEngine,
    ProductionReceiptEngine,
    WipEngine,
)
from modules.manufacturing.service.mfg_scope_validator import MfgScopeValidator
from modules.manufacturing.service.posting_service import ManufacturingPostingService


class ProductionReceiptService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._repo = ProductionReceiptRepository(db)
        self._orders = ProductionOrderRepository(db)
        self._wip = WipRepository(db)
        self._numbers = DocumentNumberService(db)
        self._engine = ProductionReceiptEngine()
        self._prod_engine = ProductionEngine()
        self._wip_engine = WipEngine()
        self._inv = ManufacturingInventoryAdapter(db)
        self._posting = ManufacturingPostingService(db)
        self._scope = MfgScopeValidator(db)
        self._audit = AuditService(db)

    def list_receipts(self, ctx: TenantContext, company_id: UUID | None = None):
        cid = self._scope.resolve_company_id(ctx, company_id)
        return self._repo.list_receipts(ctx, cid)

    def get_receipt(self, ctx: TenantContext, receipt_id: UUID) -> MfgProductionReceipt:
        row = self._repo.get(ctx, receipt_id)
        if row is None:
            raise NotFoundException("Production receipt not found")
        return row

    def create_receipt(
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
    ) -> MfgProductionReceipt:
        self._scope.validate_company_access(ctx, company_id)
        branch_id = self._scope.require_branch(ctx, branch_id)
        number = self._numbers.generate(
            MfgEntityType.PRODUCTION_RECEIPT,
            company_id,
            model=MfgProductionReceipt,
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
                product_id=ln["product_id"],
                quantity=Decimal(str(ln["quantity"])),
                uom_id=ln["uom_id"],
                unit_cost=Decimal(str(ln["unit_cost"])) if ln.get("unit_cost") is not None else None,
                quality_status=ln.get("quality_status"),
                quality_reference=ln.get("quality_reference"),
                status="pending",
            )
        return self.get_receipt(ctx, header.id)

    def confirm(
        self,
        ctx: TenantContext,
        receipt_id: UUID,
        *,
        fg_account_id: UUID | None = None,
        wip_account_id: UUID | None = None,
        fiscal_year_id: UUID | None = None,
    ) -> MfgProductionReceipt:
        header = self.get_receipt(ctx, receipt_id)
        order = self._orders.get(ctx, header.production_order_id)
        self._engine.validate_confirmable(header, order)
        assert order is not None
        qty_total = Decimal("0")
        cost_total = Decimal("0")
        for ln in [x for x in header.lines if not x.is_deleted]:
            qty = Decimal(str(ln.quantity))
            unit_cost = Decimal(str(ln.unit_cost or 0))
            result = self._inv.receive_for_production_receipt(
                ctx,
                company_id=header.company_id,
                branch_id=header.branch_id,
                warehouse_id=header.warehouse_id,
                product_id=ln.product_id,
                uom_id=ln.uom_id,
                quantity=qty,
                source_document_id=header.id,
                source_line_id=ln.id,
                unit_cost=unit_cost if unit_cost > 0 else None,
                quality_status=ln.quality_status or "available",
            )
            ln.inventory_event_id = getattr(result, "ledger_id", None) or getattr(result, "id", None)
            ln.status = "received"
            qty_total += qty
            cost_total += unit_cost * qty
            self._prod_engine.apply_receipt_qty(order, qty)

        wip = self._wip.get_by_order(ctx, header.production_order_id)
        relieved = Decimal("0")
        if wip is not None:
            planned = Decimal(str(order.planned_qty or 0))
            ratio = (qty_total / planned) if planned > 0 else Decimal("1")
            if cost_total > 0 and Decimal(str(wip.total_cost or 0)) == 0:
                # absorb provided FG cost into relief amount for posting
                relieved = cost_total
            else:
                relieved = self._wip_engine.relieve_proportional(wip, ratio)

        if (
            fg_account_id
            and wip_account_id
            and relieved > 0
            and header.period_id is not None
        ):
            self._posting.post_production_receipt(
                ctx,
                header,
                amount=relieved,
                fg_account_id=fg_account_id,
                wip_account_id=wip_account_id,
                fiscal_year_id=fiscal_year_id,
            )

        self._repo.update(
            ctx,
            receipt_id,
            status=MaterialDocStatus.CONFIRMED.value,
            received_at=datetime.now(timezone.utc),
            received_by=ctx.user_id,
        )
        self._audit.log_entity_change(
            tenant_id=ctx.tenant_id,
            entity_name="mfg_production_receipt",
            entity_id=receipt_id,
            operation="confirm",
            performed_by=ctx.user_id,
        )
        return self.get_receipt(ctx, receipt_id)
