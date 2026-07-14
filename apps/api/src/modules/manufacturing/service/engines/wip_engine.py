"""WIP cost engine."""

from decimal import Decimal

from modules.manufacturing.domain.enums import WipStatus
from modules.manufacturing.domain.exceptions import InvalidWipState
from modules.manufacturing.models.wip import MfgWip


class WipEngine:
    def ensure_open(self, wip: MfgWip) -> None:
        if wip.status != WipStatus.OPEN.value:
            raise InvalidWipState("WIP is not open")

    def recompute_total(self, wip: MfgWip) -> Decimal:
        total = (
            Decimal(str(wip.material_cost or 0))
            + Decimal(str(wip.labor_cost or 0))
            + Decimal(str(wip.overhead_cost or 0))
        ).quantize(Decimal("0.0001"))
        wip.total_cost = total
        return total

    def add_material(self, wip: MfgWip, amount: Decimal) -> None:
        self.ensure_open(wip)
        if amount < 0:
            raise InvalidWipState("Material add amount must be non-negative")
        wip.material_cost = (Decimal(str(wip.material_cost or 0)) + amount).quantize(
            Decimal("0.0001")
        )
        self.recompute_total(wip)

    def relieve_material(self, wip: MfgWip, amount: Decimal) -> None:
        self.ensure_open(wip)
        if amount < 0:
            raise InvalidWipState("Material relieve amount must be non-negative")
        new_mat = Decimal(str(wip.material_cost or 0)) - amount
        if new_mat < 0:
            new_mat = Decimal("0")
        wip.material_cost = new_mat.quantize(Decimal("0.0001"))
        self.recompute_total(wip)

    def relieve_proportional(self, wip: MfgWip, qty_ratio: Decimal) -> Decimal:
        self.ensure_open(wip)
        if qty_ratio <= 0:
            raise InvalidWipState("Relief ratio must be positive")
        if qty_ratio > 1:
            qty_ratio = Decimal("1")
        relieved = (Decimal(str(wip.total_cost or 0)) * qty_ratio).quantize(Decimal("0.0001"))
        for field in ("material_cost", "labor_cost", "overhead_cost"):
            current = Decimal(str(getattr(wip, field) or 0))
            setattr(
                wip,
                field,
                (current * (Decimal("1") - qty_ratio)).quantize(Decimal("0.0001")),
            )
        self.recompute_total(wip)
        if Decimal(str(wip.total_cost or 0)) <= 0:
            wip.status = WipStatus.RELIEVED.value
        return relieved

    def close(self, wip: MfgWip) -> None:
        wip.status = WipStatus.CLOSED.value
        self.recompute_total(wip)
