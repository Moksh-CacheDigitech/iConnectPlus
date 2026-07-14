"""Manufacturing domain value objects / results."""

from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID


@dataclass
class BomComponentRequirement:
    component_product_id: UUID
    quantity: Decimal
    uom_id: UUID
    scrap_percent: Decimal
    bom_line_id: UUID | None = None
    alternate_product_id: UUID | None = None
    is_optional: bool = False

    @property
    def required_qty(self) -> Decimal:
        factor = Decimal("1") + (self.scrap_percent / Decimal("100"))
        return (self.quantity * factor).quantize(Decimal("0.0001"))


@dataclass
class OperationTemplate:
    operation_seq: int
    operation_code: str
    operation_name: str | None
    work_center_id: UUID
    setup_time_minutes: Decimal
    run_time_minutes: Decimal
    routing_operation_id: UUID | None = None


@dataclass
class WipCostSnapshot:
    material_cost: Decimal
    labor_cost: Decimal
    overhead_cost: Decimal

    @property
    def total_cost(self) -> Decimal:
        return (
            self.material_cost + self.labor_cost + self.overhead_cost
        ).quantize(Decimal("0.0001"))


@dataclass
class VarianceResult:
    variance_type: str
    standard_amount: Decimal
    actual_amount: Decimal

    @property
    def variance_amount(self) -> Decimal:
        return (self.actual_amount - self.standard_amount).quantize(Decimal("0.0001"))
