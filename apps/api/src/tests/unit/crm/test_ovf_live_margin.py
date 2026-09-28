"""Live OVF margin: overdue receivable, held stock, early-payment saving, delivery weeks."""

from datetime import date
from decimal import Decimal

from modules.crm.domain.delivery_timeline import expected_delivery_date, parse_delivery_weeks
from modules.crm.service.engines import margin_engine


def test_carrying_cost_is_one_percent_a_month():
    # 8 lakh server held a month → ₹8,000 (the Samsung example).
    assert margin_engine.carrying_cost(Decimal("800000"), 30) == Decimal("8000.0000")
    assert margin_engine.carrying_cost(Decimal("800000"), 0) == Decimal("0")
    assert margin_engine.carrying_cost(Decimal("-5"), 30) == Decimal("0")


def test_overdue_cost_accrues_until_paid():
    # ₹4 Cr unpaid for a year past due → 48 lakh at 1% a month (360 days).
    result = margin_engine.compute_overdue_finance_cost(
        Decimal("40000000"), date(2025, 1, 1), [], date(2025, 12, 27)
    )
    assert result.cost == Decimal("4800000.0000")
    assert result.overdue_days == 360
    assert result.outstanding == Decimal("40000000.0000")


def test_overdue_cost_stops_on_the_part_that_is_paid():
    due = date(2026, 1, 1)
    receipts = [(date(2026, 1, 31), Decimal("600000")), (date(2026, 3, 2), Decimal("400000"))]
    result = margin_engine.compute_overdue_finance_cost(Decimal("1000000"), due, receipts, date(2026, 6, 1))
    # 1,000,000 x 30d + 400,000 x 30d at 1%/30d.
    assert result.cost == Decimal("14000.0000")
    assert result.outstanding == Decimal("0.0000")
    assert result.overdue_days == 60


def test_payment_before_due_date_costs_nothing():
    receipts = [(date(2026, 1, 1), Decimal("500"))]
    result = margin_engine.compute_overdue_finance_cost(Decimal("500"), date(2026, 2, 1), receipts, date(2026, 5, 1))
    assert result.cost == Decimal("0.0000")
    assert result.overdue_days == 0


def test_no_due_date_means_no_overdue_cost():
    result = margin_engine.compute_overdue_finance_cost(Decimal("1000"), None, [], date(2026, 5, 1))
    assert result.cost == Decimal("0")
    assert result.outstanding == Decimal("1000")


def test_holding_cost_sums_units_on_hand():
    units = [(Decimal("300000"), date(2026, 1, 1)), (Decimal("300000"), date(2026, 1, 31))]
    assert margin_engine.compute_holding_cost(units, date(2026, 3, 2)) == Decimal("9000.0000")


def test_live_margin_absorbs_penalties_and_expenses():
    base = margin_engine.compute_ovf_margin(
        customer_total=Decimal("1000000"),
        vendor_total=Decimal("800000"),
        freight=Decimal("10000"),
        additional_charges=Decimal("0"),
        finance_cost_pct=Decimal("1"),
    )
    assert base.finance_amount == Decimal("8000.0000")
    assert base.margin_amount == Decimal("182000.0000")

    live = margin_engine.compute_ovf_margin(
        customer_total=Decimal("1000000"),
        vendor_total=Decimal("800000"),
        freight=Decimal("10000"),
        additional_charges=Decimal("0"),
        finance_cost_pct=Decimal("1"),
        execution_expenses=Decimal("100000"),
        early_payment_discount_pct=Decimal("0.5"),
        overdue_finance_cost=Decimal("40000"),
        holding_cost=Decimal("16000"),
    )
    assert live.early_payment_saving == Decimal("4000.0000")
    assert live.margin_amount == Decimal("30000.0000")
    assert live.margin_pct == Decimal("3.000")


def test_live_margin_can_turn_negative():
    live = margin_engine.compute_ovf_margin(
        customer_total=Decimal("100"),
        vendor_total=Decimal("90"),
        freight=Decimal("0"),
        additional_charges=Decimal("0"),
        finance_cost_pct=Decimal("0"),
        overdue_finance_cost=Decimal("25"),
    )
    assert live.margin_amount == Decimal("-15.0000")


def test_parse_delivery_weeks():
    assert parse_delivery_weeks("16-18 weeks") == (16, 18)
    assert parse_delivery_weeks("Delivery: 16 to 18 Weeks from PO") == (16, 18)
    assert parse_delivery_weeks("6 weeks") == (6, 6)
    assert parse_delivery_weeks("18-16 wks") == (16, 18)
    assert parse_delivery_weeks("ASAP") is None
    assert parse_delivery_weeks(None) is None


def test_expected_delivery_is_last_day_of_final_week():
    assert expected_delivery_date(date(2026, 1, 1), 18) == date(2026, 5, 7)
