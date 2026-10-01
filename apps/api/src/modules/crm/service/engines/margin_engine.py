"""Quote margin rules and OVF finance-cost computation.

Product rules enforced here:
  6. Margin: HW/SW min 7%, Services min 20%. At/below the threshold the quote
     is locked pending Management approval. A "mixed" quote (both
     hardware/software AND services lines) must meet the stricter (higher)
     of the two thresholds.
  7. Finance cost: ~0.5% per 15 days of payment gap after a 5-day buffer
     (customer payment terms minus vendor payment terms minus 5).
  9. Live margin: after approval the OVF keeps paying 1% a month on any
     receivable still unpaid past its due date, and on stock bought for the
     deal that is still sitting in the warehouse, until the full payment lands.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import ROUND_HALF_UP, Decimal
from typing import Iterable

MIN_MARGIN_PCT: dict[str, Decimal] = {
    "hardware": Decimal("7"),
    "software": Decimal("7"),
    "services": Decimal("20"),
}

FINANCE_COST_PCT_PER_15_DAYS = Decimal("0.5")
# First N days of funding gap are free (working-capital buffer).
FINANCE_COST_BUFFER_DAYS = 5

MONTHLY_CARRYING_COST_PCT = Decimal("1")
DAYS_PER_MONTH = Decimal("30")

_MONEY = Decimal("0.0001")


@dataclass(frozen=True)
class LineMargin:
    margin_pct: Decimal
    margin_amount: Decimal
    line_total: Decimal


@dataclass(frozen=True)
class QuoteMarginResult:
    avg_margin_pct: Decimal
    total_margin_amount: Decimal
    total_sell_amount: Decimal
    required_threshold_pct: Decimal
    requires_management_approval: bool
    line_types_present: set[str] = field(default_factory=set)


def compute_line_margin(qty: Decimal, unit_cost: Decimal, unit_sell: Decimal) -> LineMargin:
    """Margin % is markup on cost: (sell - cost) / cost × 100.

    Matches the quote UI where Unit Price is cost and Margin % marks that
    cost up to the customer sell price (cost × (1 + margin%/100)).
    """
    qty = Decimal(str(qty))
    unit_cost = Decimal(str(unit_cost))
    unit_sell = Decimal(str(unit_sell))
    line_total = (qty * unit_sell).quantize(Decimal("0.0001"))
    total_cost = (qty * unit_cost).quantize(Decimal("0.0001"))
    margin_amount = (line_total - total_cost).quantize(Decimal("0.0001"))
    if total_cost == 0:
        margin_pct = Decimal("0")
    else:
        margin_pct = (margin_amount / total_cost * Decimal("100")).quantize(Decimal("0.001"))
    return LineMargin(margin_pct=margin_pct, margin_amount=margin_amount, line_total=line_total)


def required_threshold_for(line_types: Iterable[str]) -> Decimal:
    """Mixed lines (hw/sw + services) => stricter (higher) threshold applies."""
    types = {t for t in line_types if t}
    thresholds = [MIN_MARGIN_PCT.get(t, Decimal("7")) for t in types]
    if not thresholds:
        return Decimal("7")
    return max(thresholds)


def evaluate_quote_margin(
    lines: Iterable[tuple[str, Decimal, Decimal, Decimal]],
) -> QuoteMarginResult:
    """``lines`` is an iterable of (line_type, qty, unit_cost, unit_sell).

    Avg margin is the arithmetic mean of each line's margin %, not a weighted total.
    """
    total_sell = Decimal("0")
    total_margin = Decimal("0")
    line_margins: list[Decimal] = []
    line_types: set[str] = set()
    for line_type, qty, unit_cost, unit_sell in lines:
        line_types.add(line_type)
        result = compute_line_margin(qty, unit_cost, unit_sell)
        total_sell += result.line_total
        total_margin += result.margin_amount
        line_margins.append(result.margin_pct)

    if not line_margins:
        avg_margin_pct = Decimal("0")
    else:
        avg_margin_pct = (sum(line_margins, Decimal("0")) / Decimal(len(line_margins))).quantize(
            Decimal("0.001")
        )

    threshold = required_threshold_for(line_types)
    requires_approval = avg_margin_pct <= threshold

    return QuoteMarginResult(
        avg_margin_pct=avg_margin_pct,
        total_margin_amount=total_margin.quantize(Decimal("0.0001")),
        total_sell_amount=total_sell.quantize(Decimal("0.0001")),
        required_threshold_pct=threshold,
        requires_management_approval=requires_approval,
        line_types_present=line_types,
    )


def compute_finance_cost_pct(vendor_payment_days: int, customer_payment_days: int) -> Decimal:
    """~0.5% per 15 days of payment gap after a 5-day buffer (exact, 2 d.p.).

    The "gap" is how long the business must fund the deal out of pocket:
    the number of days it pays the vendor before it collects from the
    customer. The first ``FINANCE_COST_BUFFER_DAYS`` of that gap are free;
    a non-positive effective gap costs nothing.
    """
    raw_gap = Decimal(int(customer_payment_days) - int(vendor_payment_days))
    gap_days = raw_gap - Decimal(FINANCE_COST_BUFFER_DAYS)
    if gap_days <= 0:
        return Decimal("0.00")
    return (gap_days / Decimal("15") * FINANCE_COST_PCT_PER_15_DAYS).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )


def carrying_cost(principal: Decimal, days: int) -> Decimal:
    """1% a month, pro-rated per day, on ``principal`` held for ``days``."""
    principal = Decimal(str(principal))
    if principal <= 0 or days <= 0:
        return Decimal("0")
    return (
        principal * MONTHLY_CARRYING_COST_PCT / Decimal("100") * Decimal(days) / DAYS_PER_MONTH
    ).quantize(_MONEY, rounding=ROUND_HALF_UP)


@dataclass(frozen=True)
class OverdueCost:
    cost: Decimal
    overdue_days: int
    outstanding: Decimal


def compute_overdue_finance_cost(
    receivable: Decimal,
    due_date: date | None,
    receipts: Iterable[tuple[date, Decimal]],
    as_of: date,
) -> OverdueCost:
    """Carrying cost on the unpaid balance for every day it stays past due.

    Receipts on or before the due date reduce the balance before any cost
    starts; later receipts stop the clock on the part they settle.
    """
    receivable = Decimal(str(receivable))
    ordered = sorted(((d, Decimal(str(a))) for d, a in receipts), key=lambda item: item[0])
    if due_date is None or receivable <= 0:
        paid = sum((amount for _d, amount in ordered), Decimal("0"))
        return OverdueCost(Decimal("0"), 0, max(receivable - paid, Decimal("0")))

    outstanding = receivable
    cost = Decimal("0")
    cursor = due_date
    last_unpaid_day = due_date
    for received_on, amount in ordered:
        if received_on > as_of:
            break
        if received_on <= due_date:
            outstanding -= amount
            continue
        if outstanding > 0:
            cost += carrying_cost(outstanding, (received_on - cursor).days)
            last_unpaid_day = received_on
        outstanding -= amount
        cursor = received_on
    if outstanding > 0 and as_of > cursor:
        cost += carrying_cost(outstanding, (as_of - cursor).days)
        last_unpaid_day = as_of
    return OverdueCost(
        cost=cost.quantize(_MONEY),
        overdue_days=max((last_unpaid_day - due_date).days, 0),
        outstanding=max(outstanding, Decimal("0")).quantize(_MONEY),
    )


def compute_holding_cost(units: Iterable[tuple[Decimal, date]], as_of: date) -> Decimal:
    """Carrying cost on stock still on hand: (unit cost, received on) pairs."""
    total = Decimal("0")
    for unit_cost, received_on in units:
        if received_on is None:
            continue
        total += carrying_cost(Decimal(str(unit_cost or 0)), (as_of - received_on).days)
    return total.quantize(_MONEY)


def compute_early_payment_saving(vendor_total: Decimal, discount_pct: Decimal) -> Decimal:
    """Discount a distributor gives for paying early, credited back to the margin."""
    vendor_total = Decimal(str(vendor_total))
    discount_pct = Decimal(str(discount_pct or 0))
    if vendor_total <= 0 or discount_pct <= 0:
        return Decimal("0")
    return (vendor_total * discount_pct / Decimal("100")).quantize(_MONEY, rounding=ROUND_HALF_UP)


@dataclass(frozen=True)
class OvfMargin:
    finance_amount: Decimal
    early_payment_saving: Decimal
    margin_amount: Decimal
    margin_pct: Decimal


def compute_ovf_margin(
    *,
    customer_total: Decimal,
    vendor_total: Decimal,
    freight: Decimal,
    additional_charges: Decimal,
    finance_cost_pct: Decimal,
    execution_expenses: Decimal = Decimal("0"),
    early_payment_discount_pct: Decimal = Decimal("0"),
    overdue_finance_cost: Decimal = Decimal("0"),
    holding_cost: Decimal = Decimal("0"),
) -> OvfMargin:
    customer_total = Decimal(str(customer_total))
    vendor_total = Decimal(str(vendor_total))
    finance_amount = (vendor_total * Decimal(str(finance_cost_pct or 0)) / Decimal("100")).quantize(_MONEY)
    saving = compute_early_payment_saving(vendor_total, early_payment_discount_pct)
    margin_amount = (
        customer_total
        - vendor_total
        - Decimal(str(freight or 0))
        - Decimal(str(additional_charges or 0))
        - Decimal(str(execution_expenses or 0))
        - finance_amount
        + saving
        - Decimal(str(overdue_finance_cost or 0))
        - Decimal(str(holding_cost or 0))
    ).quantize(_MONEY)
    margin_pct = (
        (margin_amount / customer_total * Decimal("100")).quantize(Decimal("0.001"))
        if customer_total
        else Decimal("0")
    )
    return OvfMargin(
        finance_amount=finance_amount,
        early_payment_saving=saving,
        margin_amount=margin_amount,
        margin_pct=margin_pct,
    )
