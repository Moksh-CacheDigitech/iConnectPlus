"""Scrap lifecycle engine."""

from decimal import Decimal

from modules.manufacturing.domain.enums import ScrapStatus
from modules.manufacturing.domain.exceptions import InvalidScrapState
from modules.manufacturing.models.scrap import MfgScrap


class ScrapEngine:
    def validate_submittable(self, scrap: MfgScrap) -> None:
        if scrap.status != ScrapStatus.DRAFT.value:
            raise InvalidScrapState("Only draft scrap can be submitted")
        if Decimal(str(scrap.quantity or 0)) < 0:
            raise InvalidScrapState("Scrap quantity invalid")

    def validate_approvable(self, scrap: MfgScrap) -> None:
        if scrap.status != ScrapStatus.SUBMITTED.value:
            raise InvalidScrapState("Only submitted scrap can be approved")

    def validate_postable(self, scrap: MfgScrap) -> None:
        if scrap.status != ScrapStatus.APPROVED.value:
            raise InvalidScrapState("Only approved scrap can be posted")
        if scrap.period_id is None:
            raise InvalidScrapState("Period required to post scrap")

    def compute_total_cost(self, scrap: MfgScrap) -> Decimal:
        qty = Decimal(str(scrap.quantity or 0))
        unit = Decimal(str(scrap.unit_cost or 0))
        total = (qty * unit).quantize(Decimal("0.0001"))
        scrap.total_cost = total
        return total
