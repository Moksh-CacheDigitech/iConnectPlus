"""IInventoryStock → InventoryApplicationService."""

from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from sqlalchemy.orm import Session

from modules.foundation.domain.value_objects import TenantContext
from modules.inventory.service.inventory_application_service import InventoryApplicationService
from modules.platform.dto import StockKey, StockMovementResultDTO


class InventoryStockAdapter:
    def __init__(self, db: Session) -> None:
        self._inv = InventoryApplicationService(db)

    def reserve(
        self,
        ctx: TenantContext,
        key: StockKey,
        quantity: Decimal,
        *,
        source_module: str,
        source_document_type: str,
        source_document_id: UUID,
        source_line_id: UUID | None = None,
    ) -> StockMovementResultDTO:
        reservation = self._inv.reserve(
            ctx,
            company_id=key.company_id,
            branch_id=key.branch_id,
            warehouse_id=key.warehouse_id,
            product_id=key.product_id,
            uom_id=key.uom_id,
            quantity=quantity,
            source_module=source_module,
            source_document_type=source_document_type,
            source_document_id=source_document_id,
            source_line_id=source_line_id,
            bin_id=key.bin_id,
            batch_id=key.batch_id,
        )
        return StockMovementResultDTO(
            balance_id=reservation.id,  # reservation row; balance updated inside service
            ledger_id=None,
            on_hand_qty=Decimal("0"),
            reserved_qty=Decimal(str(reservation.quantity_reserved)),
            available_qty=Decimal("0"),
            reservation_id=reservation.id,
        )

    def release(
        self,
        ctx: TenantContext,
        reservation_id: UUID,
    ) -> StockMovementResultDTO:
        reservation = self._inv.release_reservation(ctx, reservation_id)
        return StockMovementResultDTO(
            balance_id=reservation.id,
            ledger_id=None,
            on_hand_qty=Decimal("0"),
            reserved_qty=Decimal(str(reservation.quantity_reserved)),
            available_qty=Decimal("0"),
            reservation_id=reservation.id,
        )

    def receive(
        self,
        ctx: TenantContext,
        key: StockKey,
        quantity: Decimal,
        *,
        source_module: str,
        source_document_type: str,
        source_document_id: UUID,
        source_line_id: UUID | None = None,
        unit_cost: Decimal | None = None,
        quality_status: str = "available",
    ) -> StockMovementResultDTO:
        result = self._inv.receive_goods(
            ctx,
            company_id=key.company_id,
            branch_id=key.branch_id,
            warehouse_id=key.warehouse_id,
            product_id=key.product_id,
            uom_id=key.uom_id,
            quantity=quantity,
            source_module=source_module,
            source_document_type=source_document_type,
            source_document_id=source_document_id,
            source_line_id=source_line_id,
            bin_id=key.bin_id,
            batch_id=key.batch_id,
            unit_cost=unit_cost,
            quality_status=quality_status,
        )
        return StockMovementResultDTO(
            balance_id=result.balance_id,
            ledger_id=result.ledger_id,
            on_hand_qty=result.on_hand_qty,
            reserved_qty=result.reserved_qty,
            available_qty=result.available_qty,
            total_cost=result.total_cost,
        )

    def issue(
        self,
        ctx: TenantContext,
        key: StockKey,
        quantity: Decimal,
        *,
        source_module: str,
        source_document_type: str,
        source_document_id: UUID,
        source_line_id: UUID | None = None,
        reservation_id: UUID | None = None,
    ) -> StockMovementResultDTO:
        result = self._inv.issue_goods(
            ctx,
            company_id=key.company_id,
            branch_id=key.branch_id,
            warehouse_id=key.warehouse_id,
            product_id=key.product_id,
            uom_id=key.uom_id,
            quantity=quantity,
            source_module=source_module,
            source_document_type=source_document_type,
            source_document_id=source_document_id,
            source_line_id=source_line_id,
            bin_id=key.bin_id,
            batch_id=key.batch_id,
            reservation_id=reservation_id,
        )
        return StockMovementResultDTO(
            balance_id=result.balance_id,
            ledger_id=result.ledger_id,
            on_hand_qty=result.on_hand_qty,
            reserved_qty=result.reserved_qty,
            available_qty=result.available_qty,
            reservation_id=reservation_id,
            total_cost=result.total_cost,
        )
