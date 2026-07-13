"""Inventory domain value objects."""

from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID


@dataclass(frozen=True)
class StockKey:
    company_id: UUID
    branch_id: UUID
    warehouse_id: UUID
    product_id: UUID
    uom_id: UUID
    bin_id: UUID | None = None
    batch_id: UUID | None = None
    quality_status: str = "available"


@dataclass(frozen=True)
class MovementCommand:
    stock_key: StockKey
    quantity: Decimal
    movement_type: str
    source_module: str
    source_document_type: str
    source_document_id: UUID
    source_line_id: UUID | None = None
    unit_cost: Decimal | None = None
    serial_id: UUID | None = None


@dataclass(frozen=True)
class FifoConsumeResult:
    total_cost: Decimal
    average_unit_cost: Decimal
    layers_touched: int
