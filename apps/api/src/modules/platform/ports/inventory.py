"""Inventory stock port — inventory owns quantity truth."""

from __future__ import annotations

from decimal import Decimal
from typing import Protocol
from uuid import UUID

from modules.foundation.domain.value_objects import TenantContext
from modules.platform.dto import StockKey, StockMovementResultDTO


class IInventoryStock(Protocol):
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
        ...

    def release(
        self,
        ctx: TenantContext,
        reservation_id: UUID,
    ) -> StockMovementResultDTO:
        ...

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
        ...

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
        ...
