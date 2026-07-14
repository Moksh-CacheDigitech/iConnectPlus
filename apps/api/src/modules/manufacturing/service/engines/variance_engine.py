"""Production variance engine."""

from decimal import Decimal

from modules.manufacturing.domain.entities import VarianceResult


class VarianceEngine:
    def compute(
        self,
        *,
        variance_type: str,
        standard_amount: Decimal,
        actual_amount: Decimal,
    ) -> VarianceResult:
        return VarianceResult(
            variance_type=variance_type,
            standard_amount=standard_amount.quantize(Decimal("0.0001")),
            actual_amount=actual_amount.quantize(Decimal("0.0001")),
        )
