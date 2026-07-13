"""Vendor comparison / recommendation engine (FRD-07 §7)."""

from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from modules.procurement.models.vendor_quotation import ProcVendorQuotationHeader


@dataclass(frozen=True)
class ComparisonResult:
    best_price_quotation_id: UUID | None
    best_delivery_quotation_id: UUID | None
    best_overall_quotation_id: UUID | None
    score_breakdown: dict


class VendorComparisonEngine:
    """Rank submitted vendor quotations by price, delivery, and overall score."""

    def compare(self, quotations: list[ProcVendorQuotationHeader]) -> ComparisonResult:
        active = [
            q
            for q in quotations
            if not getattr(q, "is_deleted", False)
            and q.status in {"submitted", "under_review", "selected"}
        ]
        if not active:
            return ComparisonResult(None, None, None, {"quotations": []})

        scored: list[dict] = []
        for q in active:
            total = Decimal(str(q.total_amount))
            delivery = q.delivery_days if q.delivery_days is not None else 9999
            scored.append(
                {
                    "id": str(q.id),
                    "total_amount": float(total),
                    "delivery_days": delivery,
                }
            )

        by_price = sorted(active, key=lambda q: Decimal(str(q.total_amount)))
        by_delivery = sorted(
            active,
            key=lambda q: q.delivery_days if q.delivery_days is not None else 9999,
        )

        # Overall: normalize rank sum (lower is better)
        price_rank = {q.id: i for i, q in enumerate(by_price)}
        delivery_rank = {q.id: i for i, q in enumerate(by_delivery)}
        overall = sorted(
            active,
            key=lambda q: price_rank[q.id] + delivery_rank[q.id],
        )

        return ComparisonResult(
            best_price_quotation_id=by_price[0].id if by_price else None,
            best_delivery_quotation_id=by_delivery[0].id if by_delivery else None,
            best_overall_quotation_id=overall[0].id if overall else None,
            score_breakdown={"quotations": scored},
        )
