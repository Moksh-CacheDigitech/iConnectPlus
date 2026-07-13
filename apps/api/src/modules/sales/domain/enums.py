"""Sales domain enums."""

from enum import Enum


class QuotationStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    SENT = "sent"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class OrderStatus(str, Enum):
    DRAFT = "draft"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    PARTIALLY_DELIVERED = "partially_delivered"
    DELIVERED = "delivered"
    CLOSED = "closed"
    CANCELLED = "cancelled"


class DeliveryStatus(str, Enum):
    DRAFT = "draft"
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    PARTIALLY_DELIVERED = "partially_delivered"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class InvoiceStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    POSTED = "posted"
    PARTIALLY_PAID = "partially_paid"
    PAID = "paid"
    CANCELLED = "cancelled"


class ReturnStatus(str, Enum):
    DRAFT = "draft"
    REQUESTED = "requested"
    APPROVED = "approved"
    RECEIVED = "received"
    POSTED = "posted"
    CLOSED = "closed"
    CANCELLED = "cancelled"


class PriceListType(str, Enum):
    STANDARD = "standard"
    CUSTOMER = "customer"
    VOLUME = "volume"
    PROMOTIONAL = "promotional"
    CONTRACT = "contract"


class DiscountType(str, Enum):
    PERCENT = "percent"
    FIXED_AMOUNT = "fixed_amount"
    BUY_X_GET_Y = "buy_x_get_y"


class SalesEntityType(str, Enum):
    QUOTATION = "quotation"
    ORDER = "order"
    DELIVERY = "delivery"
    INVOICE = "invoice"
    RETURN = "return"


CODE_PREFIXES: dict[SalesEntityType, tuple[str, int]] = {
    SalesEntityType.QUOTATION: ("QT-", 6),
    SalesEntityType.ORDER: ("SO-", 6),
    SalesEntityType.DELIVERY: ("DLV-", 6),
    SalesEntityType.INVOICE: ("INV-", 6),
    SalesEntityType.RETURN: ("RET-", 6),
}

WORKFLOW_CODES: dict[str, str] = {
    "sales_quotation_header": "SALES_QUOTATION_APPROVAL",
    "sales_discount_rule": "SALES_DISCOUNT_APPROVAL",
    "sales_order_header": "SALES_ORDER_APPROVAL",
    "sales_invoice_header": "SALES_INVOICE_APPROVAL",
    "sales_return_header": "SALES_RETURN_APPROVAL",
}
