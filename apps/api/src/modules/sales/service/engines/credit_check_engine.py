"""Customer credit check engine."""

from decimal import Decimal

from modules.sales.domain.entities import CreditCheckResult
from modules.sales.domain.exceptions import CreditHoldError, CreditLimitExceeded
from modules.sales.models.credit import SalesCustomerCredit


class CreditCheckEngine:
    def check(
        self,
        credit: SalesCustomerCredit,
        *,
        additional_amount: Decimal = Decimal("0"),
        raise_on_fail: bool = True,
    ) -> CreditCheckResult:
        credit_limit = Decimal(str(credit.credit_limit))
        credit_used = Decimal(str(credit.credit_used))
        credit_available = Decimal(str(credit.credit_available))
        hold = bool(credit.credit_hold)

        if hold:
            if raise_on_fail:
                reason = credit.credit_hold_reason or "Customer is on credit hold"
                raise CreditHoldError(reason)
            return CreditCheckResult(
                customer_id=credit.customer_id,
                credit_limit=credit_limit,
                credit_used=credit_used,
                credit_available=credit_available,
                credit_hold=True,
                approved=False,
            )

        projected_used = credit_used + additional_amount
        available_after = credit_limit - projected_used
        approved = projected_used <= credit_limit

        if not approved and raise_on_fail:
            raise CreditLimitExceeded(
                f"Credit limit exceeded: used={projected_used}, limit={credit_limit}"
            )

        return CreditCheckResult(
            customer_id=credit.customer_id,
            credit_limit=credit_limit,
            credit_used=credit_used,
            credit_available=available_after if approved else credit_available,
            credit_hold=False,
            approved=approved,
        )

    def recalculate_available(self, credit: SalesCustomerCredit) -> Decimal:
        available = Decimal(str(credit.credit_limit)) - Decimal(str(credit.credit_used))
        if available < 0:
            available = Decimal("0")
        credit.credit_available = float(available.quantize(Decimal("0.0001")))
        return available
