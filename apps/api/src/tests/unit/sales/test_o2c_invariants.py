"""O2C document number and invoice engine invariants."""

from decimal import Decimal

from modules.sales.domain.enums import CODE_PREFIXES, SalesEntityType
from modules.sales.service.engines.invoice_engine import InvoiceEngine


class _ILine:
    def __init__(self, qty, price, discount=0, tax=0):
        self.quantity = qty
        self.unit_price = price
        self.discount_amount = discount
        self.tax_amount = tax
        self.line_total = qty * price - discount + tax
        self.is_deleted = False


class _Invoice:
    def __init__(self, status, lines=None):
        self.status = status
        self.lines = lines or []
        self.subtotal_amount = 0
        self.discount_amount = 0
        self.tax_amount = 0
        self.total_amount = 0
        self.amount_due = 0


def test_document_prefixes() -> None:
    assert CODE_PREFIXES[SalesEntityType.QUOTATION][0] == "QT-"
    assert CODE_PREFIXES[SalesEntityType.ORDER][0] == "SO-"
    assert CODE_PREFIXES[SalesEntityType.DELIVERY][0] == "DLV-"
    assert CODE_PREFIXES[SalesEntityType.INVOICE][0] == "INV-"
    assert CODE_PREFIXES[SalesEntityType.RETURN][0] == "RET-"


def test_invoice_header_totals() -> None:
    engine = InvoiceEngine()
    lines = [_ILine(2, 100, discount=10, tax=19), _ILine(1, 50)]
    totals = engine.compute_header_totals(lines)
    assert totals.subtotal_amount == Decimal("250.0000")
    assert totals.discount_amount == Decimal("10.0000")
    assert totals.tax_amount == Decimal("19.0000")
    assert totals.total_amount == Decimal("259.0000")


def test_invoice_postable_state() -> None:
    engine = InvoiceEngine()
    invoice = _Invoice("submitted", [_ILine(1, 100)])
    engine.validate_postable(invoice)
