"""Procurement domain enums."""

from enum import Enum


class RequisitionStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"
    CONVERTED_TO_RFQ = "converted_to_rfq"
    CANCELLED = "cancelled"


class RequisitionPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RfqStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    QUOTES_RECEIVED = "quotes_received"
    CLOSED = "closed"
    CANCELLED = "cancelled"


class VendorQuotationStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    SELECTED = "selected"
    REJECTED = "rejected"
    EXPIRED = "expired"


class ComparisonStatus(str, Enum):
    DRAFT = "draft"
    COMPLETED = "completed"


class OrderStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    SENT = "sent"
    PARTIALLY_RECEIVED = "partially_received"
    RECEIVED = "received"
    CLOSED = "closed"
    CANCELLED = "cancelled"


class GrnStatus(str, Enum):
    DRAFT = "draft"
    PENDING = "pending"
    PARTIALLY_RECEIVED = "partially_received"
    RECEIVED = "received"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class ContractStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    EXPIRED = "expired"
    TERMINATED = "terminated"


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


class ProcEntityType(str, Enum):
    REQUISITION = "requisition"
    RFQ = "rfq"
    VENDOR_QUOTATION = "vendor_quotation"
    VENDOR_COMPARISON = "vendor_comparison"
    ORDER = "order"
    GRN = "grn"
    CONTRACT = "contract"
    INVOICE = "invoice"
    RETURN = "return"


CODE_PREFIXES: dict[ProcEntityType, tuple[str, int]] = {
    ProcEntityType.REQUISITION: ("PR-", 6),
    ProcEntityType.RFQ: ("RFQ-", 6),
    ProcEntityType.VENDOR_QUOTATION: ("VQ-", 6),
    ProcEntityType.VENDOR_COMPARISON: ("VCMP-", 6),
    ProcEntityType.ORDER: ("PO-", 6),
    ProcEntityType.GRN: ("GRN-", 6),
    ProcEntityType.CONTRACT: ("PCT-", 6),
    ProcEntityType.INVOICE: ("PINV-", 6),
    ProcEntityType.RETURN: ("PRET-", 6),
}

WORKFLOW_CODES: dict[str, str] = {
    "proc_requisition_header": "PROC_PR_APPROVAL",
    "proc_rfq_header": "PROC_RFQ_APPROVAL",
    "proc_order_header": "PROC_PO_APPROVAL",
    "proc_invoice_header": "PROC_INVOICE_APPROVAL",
    "proc_return_header": "PROC_RETURN_APPROVAL",
    "proc_vendor_contract": "PROC_CONTRACT_APPROVAL",
}
