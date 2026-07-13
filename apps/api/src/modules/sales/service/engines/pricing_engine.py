"""Pricing resolution engine."""

from datetime import date
from decimal import Decimal
from uuid import UUID

from modules.sales.domain.enums import PriceListType
from modules.sales.domain.exceptions import PricingNotFound
from modules.sales.domain.value_objects import PricingResult
from modules.sales.models.pricing import SalesPriceList, SalesPriceListItem


class PricingEngine:
    """Resolve unit price by FRD-06 hierarchy (lower priority number wins)."""

    TYPE_PRIORITY: dict[str, int] = {
        PriceListType.CONTRACT.value: 10,
        PriceListType.CUSTOMER.value: 20,
        PriceListType.VOLUME.value: 30,
        PriceListType.PROMOTIONAL.value: 40,
        PriceListType.STANDARD.value: 50,
    }

    def resolve_price(
        self,
        *,
        product_id: UUID,
        quantity: Decimal,
        price_lists: list[SalesPriceList],
        as_of: date | None = None,
        customer_id: UUID | None = None,
    ) -> PricingResult:
        as_of = as_of or date.today()
        candidates: list[tuple[int, int, SalesPriceList, SalesPriceListItem]] = []

        for price_list in price_lists:
            if price_list.status != "active":
                continue
            if price_list.effective_from > as_of:
                continue
            if price_list.effective_to is not None and price_list.effective_to < as_of:
                continue
            if price_list.customer_id is not None and price_list.customer_id != customer_id:
                continue

            type_priority = self.TYPE_PRIORITY.get(
                price_list.price_list_type, price_list.priority
            )
            item = self._match_item(price_list, product_id, quantity)
            if item is None:
                continue
            candidates.append((type_priority, price_list.priority, price_list, item))

        if not candidates:
            raise PricingNotFound(f"No price found for product {product_id}")

        candidates.sort(key=lambda row: (row[0], row[1]))
        _, _, price_list, item = candidates[0]
        return PricingResult(
            product_id=product_id,
            unit_price=Decimal(str(item.unit_price)),
            price_list_id=price_list.id,
            source=price_list.price_list_type,
        )

    def _match_item(
        self,
        price_list: SalesPriceList,
        product_id: UUID,
        quantity: Decimal,
    ) -> SalesPriceListItem | None:
        matching = [
            item
            for item in price_list.items
            if not getattr(item, "is_deleted", False)
            and item.status == "active"
            and item.product_id == product_id
            and Decimal(str(item.min_quantity)) <= quantity
        ]
        if not matching:
            return None
        # Volume breaks: highest min_quantity that still qualifies
        matching.sort(key=lambda item: Decimal(str(item.min_quantity)), reverse=True)
        return matching[0]
