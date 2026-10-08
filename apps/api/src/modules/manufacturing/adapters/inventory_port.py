"""Inventory port — manufacturing stock via platform IInventoryStock."""

from decimal import Decimal
from uuid import UUID

from sqlalchemy.orm import Session

from modules.foundation.domain.value_objects import TenantContext
from modules.inventory.domain.enums import SourceModule
from modules.platform.adapters.inventory_adapter import InventoryStockAdapter
from modules.platform.dto import StockKey
from modules.platform.helpers.side_effects import enqueue_domain_event


class ManufacturingInventoryAdapter:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._stock = InventoryStockAdapter(db)

    def issue_for_material_issue(
        self,
        ctx: TenantContext,
        *,
        company_id: UUID,
        branch_id: UUID,
        warehouse_id: UUID,
        product_id: UUID,
        uom_id: UUID,
        quantity: Decimal,
        source_document_id: UUID,
        source_line_id: UUID | None = None,
        bin_id: UUID | None = None,
        batch_id: UUID | None = None,
    ):
        result = self._stock.issue(
            ctx,
            StockKey(
                company_id=company_id,
                branch_id=branch_id,
                warehouse_id=warehouse_id,
                product_id=product_id,
                uom_id=uom_id,
                bin_id=bin_id,
                batch_id=batch_id,
            ),
            quantity,
            source_module=SourceModule.MANUFACTURING.value,
            source_document_type="material_issue",
            source_document_id=source_document_id,
            source_line_id=source_line_id,
        )
        enqueue_domain_event(
            self._db,
            tenant_id=ctx.tenant_id,
            event_type="domain.inventory.stock_issued",
            aggregate_type="material_issue",
            aggregate_id=source_document_id,
            payload={"source_document_id": str(source_document_id)},
            idempotency_key=f"domain.inventory.stock_issued:material_issue:{source_document_id}:{source_line_id or 'hdr'}",
            created_by=ctx.user_id,
        )
        return result

    def receive_for_material_return(
        self,
        ctx: TenantContext,
        *,
        company_id: UUID,
        branch_id: UUID,
        warehouse_id: UUID,
        product_id: UUID,
        uom_id: UUID,
        quantity: Decimal,
        source_document_id: UUID,
        source_line_id: UUID | None = None,
        unit_cost: Decimal | None = None,
        bin_id: UUID | None = None,
        batch_id: UUID | None = None,
    ):
        return self._stock.receive(
            ctx,
            StockKey(
                company_id=company_id,
                branch_id=branch_id,
                warehouse_id=warehouse_id,
                product_id=product_id,
                uom_id=uom_id,
                bin_id=bin_id,
                batch_id=batch_id,
            ),
            quantity,
            source_module=SourceModule.MANUFACTURING.value,
            source_document_type="material_return",
            source_document_id=source_document_id,
            source_line_id=source_line_id,
            unit_cost=unit_cost,
        )

    def receive_for_production_receipt(
        self,
        ctx: TenantContext,
        *,
        company_id: UUID,
        branch_id: UUID,
        warehouse_id: UUID,
        product_id: UUID,
        uom_id: UUID,
        quantity: Decimal,
        source_document_id: UUID,
        source_line_id: UUID | None = None,
        unit_cost: Decimal | None = None,
        quality_status: str = "available",
    ):
        result = self._stock.receive(
            ctx,
            StockKey(
                company_id=company_id,
                branch_id=branch_id,
                warehouse_id=warehouse_id,
                product_id=product_id,
                uom_id=uom_id,
            ),
            quantity,
            source_module=SourceModule.MANUFACTURING.value,
            source_document_type="production_receipt",
            source_document_id=source_document_id,
            source_line_id=source_line_id,
            unit_cost=unit_cost,
            quality_status=quality_status,
        )
        enqueue_domain_event(
            self._db,
            tenant_id=ctx.tenant_id,
            event_type="domain.inventory.stock_received",
            aggregate_type="production_receipt",
            aggregate_id=source_document_id,
            payload={"source_document_id": str(source_document_id)},
            idempotency_key=f"domain.inventory.stock_received:production_receipt:{source_document_id}:{source_line_id or 'hdr'}",
            created_by=ctx.user_id,
        )
        return result
