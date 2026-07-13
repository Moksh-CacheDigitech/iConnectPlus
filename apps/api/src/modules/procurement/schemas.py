"""Procurement Pydantic schemas."""

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

# --- Requisition ---


class RequisitionCreateRequest(BaseModel):
    branch_id: UUID
    document_date: date
    requester_id: UUID
    department_id: UUID
    cost_center_id: UUID
    required_date: date
    currency_code: str
    priority: str = "medium"
    exchange_rate: float = 1.0
    notes: str | None = None
    company_id: UUID | None = None


class RequisitionUpdateRequest(BaseModel):
    required_date: date | None = None
    priority: str | None = None
    notes: str | None = None
    version: int | None = None


class RequisitionLineCreateRequest(BaseModel):
    line_number: int
    product_id: UUID
    product_code: str | None = None
    product_name: str | None = None
    quantity: float
    uom_id: UUID
    estimated_unit_cost: float | None = None
    tax_id: UUID | None = None
    required_date: date | None = None


class RequisitionLineResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    line_number: int
    product_id: UUID
    product_code: str | None = None
    product_name: str | None = None
    quantity: float
    estimated_unit_cost: float | None = None
    tax_amount: float
    line_total: float
    status: str


class RequisitionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    company_id: UUID
    branch_id: UUID
    document_number: str
    document_date: date
    requester_id: UUID
    department_id: UUID
    cost_center_id: UUID
    required_date: date
    priority: str
    currency_code: str
    subtotal_amount: float
    tax_amount: float
    total_amount: float
    status: str
    workflow_status: str | None = None
    workflow_instance_id: UUID | None = None
    version: int
    lines: list[RequisitionLineResponse] = Field(default_factory=list)


# --- RFQ ---


class RfqCreateRequest(BaseModel):
    branch_id: UUID
    document_date: date
    closing_date: date
    currency_code: str
    requisition_header_id: UUID | None = None
    exchange_rate: float = 1.0
    notes: str | None = None
    company_id: UUID | None = None


class RfqUpdateRequest(BaseModel):
    closing_date: date | None = None
    notes: str | None = None
    version: int | None = None


class RfqLineCreateRequest(BaseModel):
    line_number: int
    product_id: UUID
    quantity: float
    uom_id: UUID
    requisition_line_id: UUID | None = None
    target_unit_cost: float | None = None


class RfqVendorCreateRequest(BaseModel):
    vendor_id: UUID


class RfqLineResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    line_number: int
    product_id: UUID
    quantity: float
    target_unit_cost: float | None = None
    status: str


class RfqVendorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    vendor_id: UUID
    invite_status: str
    sent_at: datetime | None = None
    responded_at: datetime | None = None


class RfqResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    company_id: UUID
    branch_id: UUID
    document_number: str
    document_date: date
    requisition_header_id: UUID | None = None
    closing_date: date
    currency_code: str
    status: str
    workflow_status: str | None = None
    workflow_instance_id: UUID | None = None
    version: int
    lines: list[RfqLineResponse] = Field(default_factory=list)
    vendors: list[RfqVendorResponse] = Field(default_factory=list)


# --- Vendor Quotation ---


class VendorQuotationCreateRequest(BaseModel):
    branch_id: UUID
    document_date: date
    rfq_header_id: UUID
    vendor_id: UUID
    valid_until: date
    currency_code: str
    vendor_quote_reference: str | None = None
    payment_terms: str | None = None
    delivery_days: int | None = None
    exchange_rate: float = 1.0
    company_id: UUID | None = None


class VendorQuotationUpdateRequest(BaseModel):
    valid_until: date | None = None
    payment_terms: str | None = None
    delivery_days: int | None = None
    vendor_quote_reference: str | None = None
    version: int | None = None


class VendorQuotationLineCreateRequest(BaseModel):
    line_number: int
    product_id: UUID
    quantity: float
    uom_id: UUID
    unit_cost: float
    rfq_line_id: UUID | None = None
    lead_time_days: int | None = None
    tax_id: UUID | None = None
    tax_rate: float = 0
    is_alternate_product: bool = False


class VendorQuotationLineResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    line_number: int
    product_id: UUID
    quantity: float
    unit_cost: float
    tax_amount: float
    line_total: float
    status: str


class VendorQuotationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    company_id: UUID
    branch_id: UUID
    document_number: str
    document_date: date
    rfq_header_id: UUID
    vendor_id: UUID
    valid_until: date
    currency_code: str
    subtotal_amount: float
    tax_amount: float
    total_amount: float
    status: str
    version: int
    lines: list[VendorQuotationLineResponse] = Field(default_factory=list)


class VendorQuotationSelectRequest(BaseModel):
    quotation_id: UUID


# --- Purchase Order ---


class OrderCreateRequest(BaseModel):
    branch_id: UUID
    document_date: date
    vendor_id: UUID
    currency_code: str
    exchange_rate: float = 1.0
    requisition_header_id: UUID | None = None
    rfq_header_id: UUID | None = None
    vendor_quotation_header_id: UUID | None = None
    contract_id: UUID | None = None
    payment_terms: str | None = None
    expected_delivery_date: date | None = None
    company_id: UUID | None = None


class OrderUpdateRequest(BaseModel):
    payment_terms: str | None = None
    expected_delivery_date: date | None = None
    version: int | None = None


class OrderLineCreateRequest(BaseModel):
    line_number: int
    product_id: UUID
    product_code: str | None = None
    product_name: str | None = None
    quantity: float
    uom_id: UUID
    unit_cost: float
    discount_percent: float = 0
    discount_amount: float = 0
    tax_id: UUID | None = None
    tax_rate: float = 0


class OrderLineResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    line_number: int
    product_id: UUID
    product_code: str | None = None
    quantity: float
    quantity_received: float
    unit_cost: float
    line_total: float
    status: str


class OrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    company_id: UUID
    branch_id: UUID
    document_number: str
    document_date: date
    vendor_id: UUID
    requisition_header_id: UUID | None = None
    rfq_header_id: UUID | None = None
    vendor_quotation_header_id: UUID | None = None
    contract_id: UUID | None = None
    currency_code: str
    total_amount: float
    status: str
    workflow_status: str | None = None
    version: int
    lines: list[OrderLineResponse] = Field(default_factory=list)


# --- GRN ---


class GrnCreateRequest(BaseModel):
    order_header_id: UUID
    document_date: date
    warehouse_reference: UUID
    notes: str | None = None
    company_id: UUID | None = None


class GrnLineCreateRequest(BaseModel):
    order_line_id: UUID
    line_number: int
    quantity: float
    quantity_rejected: float = 0


class GrnLineResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    order_line_id: UUID
    line_number: int
    product_id: UUID
    quantity: float
    quantity_rejected: float
    status: str


class GrnResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    company_id: UUID
    branch_id: UUID
    document_number: str
    document_date: date
    order_header_id: UUID
    vendor_id: UUID
    warehouse_reference: UUID
    status: str
    subtotal_amount: float
    version: int
    lines: list[GrnLineResponse] = Field(default_factory=list)


# --- Invoice ---


class InvoiceCreateRequest(BaseModel):
    grn_header_id: UUID
    document_date: date
    due_date: date
    vendor_invoice_number: str
    period_id: UUID | None = None
    company_id: UUID | None = None


class InvoiceUpdateRequest(BaseModel):
    due_date: date | None = None
    vendor_invoice_number: str | None = None
    version: int | None = None


class InvoiceLineResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    line_number: int
    product_id: UUID
    product_code: str | None = None
    quantity: float
    unit_cost: float
    tax_amount: float
    line_total: float
    expense_account_id: UUID | None = None


class InvoiceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    company_id: UUID
    branch_id: UUID
    document_number: str
    document_date: date
    due_date: date
    vendor_id: UUID
    vendor_invoice_number: str
    order_header_id: UUID | None = None
    grn_header_id: UUID | None = None
    total_amount: float
    balance_due: float
    match_status: str
    status: str
    workflow_status: str | None = None
    finance_ledger_id: UUID | None = None
    finance_journal_id: UUID | None = None
    posting_status: str | None = None
    version: int
    lines: list[InvoiceLineResponse] = Field(default_factory=list)


class InvoicePostRequest(BaseModel):
    ap_account_id: UUID
    expense_account_id: UUID | None = None


# --- Return ---


class ReturnCreateRequest(BaseModel):
    branch_id: UUID
    document_date: date
    vendor_id: UUID
    invoice_header_id: UUID
    currency_code: str
    order_header_id: UUID | None = None
    grn_header_id: UUID | None = None
    period_id: UUID | None = None
    exchange_rate: float = 1.0
    reason_code: str | None = None
    company_id: UUID | None = None


class ReturnLineCreateRequest(BaseModel):
    line_number: int
    product_id: UUID
    quantity: float
    unit_cost: float
    invoice_line_id: UUID | None = None
    order_line_id: UUID | None = None
    grn_line_id: UUID | None = None
    tax_amount: float = 0


class ReturnLineResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    line_number: int
    product_id: UUID
    quantity: float
    unit_cost: float
    tax_amount: float
    line_total: float
    status: str


class ReturnResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    company_id: UUID
    branch_id: UUID
    document_number: str
    document_date: date
    vendor_id: UUID
    invoice_header_id: UUID
    order_header_id: UUID | None = None
    grn_header_id: UUID | None = None
    reason_code: str | None = None
    total_amount: float
    status: str
    workflow_status: str | None = None
    finance_journal_id: UUID | None = None
    version: int
    lines: list[ReturnLineResponse] = Field(default_factory=list)


class ReturnPostRequest(BaseModel):
    ap_account_id: UUID
    expense_account_id: UUID


# --- Contract ---


class ContractCreateRequest(BaseModel):
    vendor_id: UUID
    contract_name: str
    start_date: date
    end_date: date
    currency_code: str
    contract_value: float | None = None
    branch_id: UUID | None = None
    company_id: UUID | None = None


class ContractUpdateRequest(BaseModel):
    contract_name: str | None = None
    end_date: date | None = None
    contract_value: float | None = None
    version: int | None = None


class ContractLineCreateRequest(BaseModel):
    line_number: int
    product_id: UUID | None = None
    unit_cost: float
    min_quantity: float | None = None
    max_quantity: float | None = None
    effective_from: date | None = None
    effective_to: date | None = None


class ContractLineResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    line_number: int
    product_id: UUID | None = None
    unit_cost: float
    min_quantity: float | None = None
    max_quantity: float | None = None
    status: str


class ContractResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    company_id: UUID
    branch_id: UUID | None = None
    document_number: str
    vendor_id: UUID
    contract_name: str
    start_date: date
    end_date: date
    contract_value: float | None = None
    currency_code: str
    status: str
    workflow_status: str | None = None
    workflow_instance_id: UUID | None = None
    version: int
    lines: list[ContractLineResponse] = Field(default_factory=list)


# --- Vendor comparison ---


class ComparisonSelectRequest(BaseModel):
    quotation_id: UUID


class ComparisonResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    company_id: UUID
    branch_id: UUID
    document_number: str | None = None
    rfq_header_id: UUID
    best_price_quotation_id: UUID | None = None
    best_delivery_quotation_id: UUID | None = None
    best_overall_quotation_id: UUID | None = None
    selected_quotation_id: UUID | None = None
    score_breakdown: dict | None = None
    status: str
    compared_at: datetime | None = None


# --- Performance ---


class PerformanceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    company_id: UUID
    branch_id: UUID | None = None
    vendor_id: UUID
    period_code: str
    on_time_delivery_pct: float | None = None
    quality_rating: float | None = None
    cost_competitiveness_score: float | None = None
    contract_compliance_score: float | None = None
    issue_resolution_days: float | None = None
    overall_score: float
    calculated_at: datetime
    status: str


# --- Shared ---


class WorkflowActionRequest(BaseModel):
    comments: str | None = None
