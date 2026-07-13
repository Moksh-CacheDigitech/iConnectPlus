"""Sales Pydantic schemas."""

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

# --- Price list ---


class PriceListCreateRequest(BaseModel):
    price_list_code: str
    price_list_name: str
    currency_code: str
    effective_from: date
    price_list_type: str = "standard"
    customer_id: UUID | None = None
    priority: int = 100
    effective_to: date | None = None
    status: str = "active"
    company_id: UUID | None = None


class PriceListUpdateRequest(BaseModel):
    price_list_name: str | None = None
    priority: int | None = None
    effective_to: date | None = None
    status: str | None = None
    version: int | None = None


class PriceListItemCreateRequest(BaseModel):
    line_number: int
    product_id: UUID
    product_code: str
    unit_price: float
    min_quantity: float = 1
    uom_id: UUID | None = None
    status: str = "active"


class PriceListItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    price_list_id: UUID
    line_number: int
    product_id: UUID
    product_code: str
    min_quantity: float
    unit_price: float
    status: str


class PriceListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    company_id: UUID
    price_list_code: str
    price_list_name: str
    price_list_type: str
    currency_code: str
    priority: int
    effective_from: date
    effective_to: date | None = None
    status: str
    customer_id: UUID | None = None
    version: int
    items: list[PriceListItemResponse] = Field(default_factory=list)


# --- Discount rule ---


class DiscountRuleCreateRequest(BaseModel):
    discount_code: str
    discount_name: str
    discount_type: str
    discount_value: float
    effective_from: date
    max_discount_percent: float | None = None
    customer_id: UUID | None = None
    product_id: UUID | None = None
    price_list_id: UUID | None = None
    min_order_amount: float | None = None
    effective_to: date | None = None
    requires_approval: bool = False
    branch_id: UUID | None = None
    status: str = "draft"
    company_id: UUID | None = None


class DiscountRuleUpdateRequest(BaseModel):
    discount_name: str | None = None
    discount_value: float | None = None
    max_discount_percent: float | None = None
    effective_to: date | None = None
    requires_approval: bool | None = None
    status: str | None = None
    version: int | None = None


class DiscountRuleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    company_id: UUID
    discount_code: str
    discount_name: str
    discount_type: str
    discount_value: float
    status: str
    requires_approval: bool
    workflow_instance_id: UUID | None = None
    version: int


# --- Customer credit ---


class CustomerCreditCreateRequest(BaseModel):
    customer_id: UUID
    currency_code: str
    credit_limit: float = 0
    payment_terms_days: int | None = None
    credit_hold: bool = False
    credit_hold_reason: str | None = None
    branch_id: UUID | None = None
    status: str = "active"
    company_id: UUID | None = None


class CustomerCreditUpdateRequest(BaseModel):
    credit_limit: float | None = None
    payment_terms_days: int | None = None
    credit_hold: bool | None = None
    credit_hold_reason: str | None = None
    status: str | None = None
    version: int | None = None


class CustomerCreditResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    company_id: UUID
    customer_id: UUID
    credit_limit: float
    credit_used: float
    credit_available: float
    currency_code: str
    credit_hold: bool
    status: str
    version: int


# --- Quotation ---


class QuotationCreateRequest(BaseModel):
    branch_id: UUID
    document_date: date
    valid_until: date
    customer_id: UUID
    currency_code: str
    exchange_rate: float = 1.0
    payment_terms: str | None = None
    opportunity_reference: UUID | None = None
    price_list_id: UUID | None = None
    notes: str | None = None
    company_id: UUID | None = None


class QuotationUpdateRequest(BaseModel):
    valid_until: date | None = None
    payment_terms: str | None = None
    notes: str | None = None
    price_list_id: UUID | None = None
    version: int | None = None


class QuotationLineCreateRequest(BaseModel):
    line_number: int
    product_id: UUID
    product_code: str
    product_name: str
    quantity: float
    uom_id: UUID
    unit_price: float
    description: str | None = None
    discount_percent: float = 0
    discount_amount: float = 0
    tax_id: UUID | None = None
    tax_rate: float = 0


class QuotationLineResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    line_number: int
    product_id: UUID
    product_code: str
    product_name: str
    quantity: float
    unit_price: float
    discount_amount: float
    tax_amount: float
    line_total: float


class QuotationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    company_id: UUID
    branch_id: UUID
    document_number: str
    document_date: date
    valid_until: date
    customer_id: UUID
    customer_name: str
    currency_code: str
    subtotal_amount: float
    discount_amount: float
    tax_amount: float
    total_amount: float
    status: str
    workflow_status: str
    workflow_instance_id: UUID | None = None
    version: int
    lines: list[QuotationLineResponse] = Field(default_factory=list)


# --- Sales order ---


class SalesOrderCreateRequest(BaseModel):
    branch_id: UUID
    document_date: date
    customer_id: UUID
    currency_code: str
    exchange_rate: float = 1.0
    requested_delivery_date: date | None = None
    quotation_header_id: UUID | None = None
    price_list_id: UUID | None = None
    company_id: UUID | None = None


class SalesOrderUpdateRequest(BaseModel):
    requested_delivery_date: date | None = None
    price_list_id: UUID | None = None
    version: int | None = None


class SalesOrderLineCreateRequest(BaseModel):
    line_number: int
    product_id: UUID
    product_code: str
    product_name: str
    quantity: float
    uom_id: UUID
    unit_price: float
    quotation_line_id: UUID | None = None
    discount_percent: float = 0
    discount_amount: float = 0
    tax_id: UUID | None = None
    tax_rate: float = 0


class SalesOrderLineResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    line_number: int
    product_id: UUID
    product_code: str
    quantity: float
    quantity_delivered: float
    unit_price: float
    line_total: float
    status: str


class SalesOrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    company_id: UUID
    branch_id: UUID
    document_number: str
    document_date: date
    customer_id: UUID
    quotation_header_id: UUID | None = None
    currency_code: str
    total_amount: float
    status: str
    workflow_status: str
    version: int
    lines: list[SalesOrderLineResponse] = Field(default_factory=list)


# --- Delivery ---


class DeliveryCreateRequest(BaseModel):
    order_header_id: UUID
    document_date: date
    ship_to_address: str | None = None
    warehouse_reference: UUID | None = None
    company_id: UUID | None = None


class DeliveryLineCreateRequest(BaseModel):
    order_line_id: UUID
    line_number: int
    quantity: float
    batch_reference: str | None = None


class DeliveryLineResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    order_line_id: UUID
    line_number: int
    product_id: UUID
    quantity: float
    status: str


class DeliveryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    company_id: UUID
    branch_id: UUID
    document_number: str
    document_date: date
    order_header_id: UUID
    customer_id: UUID
    status: str
    shipped_at: datetime | None = None
    version: int
    lines: list[DeliveryLineResponse] = Field(default_factory=list)


# --- Invoice ---


class InvoiceCreateRequest(BaseModel):
    delivery_header_id: UUID
    document_date: date
    due_date: date
    period_id: UUID | None = None
    company_id: UUID | None = None


class InvoiceUpdateRequest(BaseModel):
    due_date: date | None = None
    version: int | None = None


class InvoiceLineResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    line_number: int
    product_id: UUID
    product_code: str
    quantity: float
    unit_price: float
    tax_amount: float
    line_total: float
    revenue_account_id: UUID | None = None


class InvoiceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    company_id: UUID
    branch_id: UUID
    document_number: str
    document_date: date
    due_date: date
    customer_id: UUID
    delivery_header_id: UUID | None = None
    order_header_id: UUID | None = None
    total_amount: float
    balance_due: float
    status: str
    workflow_status: str
    finance_ledger_id: UUID | None = None
    finance_journal_id: UUID | None = None
    version: int
    lines: list[InvoiceLineResponse] = Field(default_factory=list)


class InvoicePostRequest(BaseModel):
    ar_account_id: UUID
    revenue_account_id: UUID | None = None


# --- Return ---


class ReturnCreateRequest(BaseModel):
    branch_id: UUID
    document_date: date
    customer_id: UUID
    return_type: str
    currency_code: str
    invoice_header_id: UUID | None = None
    order_header_id: UUID | None = None
    period_id: UUID | None = None
    exchange_rate: float = 1.0
    reason: str | None = None
    company_id: UUID | None = None


class ReturnLineCreateRequest(BaseModel):
    line_number: int
    product_id: UUID
    quantity: float
    uom_id: UUID
    unit_price: float
    invoice_line_id: UUID | None = None
    order_line_id: UUID | None = None
    tax_id: UUID | None = None
    tax_amount: float = 0


class ReturnLineResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    line_number: int
    product_id: UUID
    quantity: float
    unit_price: float
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
    customer_id: UUID
    invoice_header_id: UUID | None = None
    return_type: str
    total_amount: float
    status: str
    workflow_status: str
    finance_journal_id: UUID | None = None
    version: int
    lines: list[ReturnLineResponse] = Field(default_factory=list)


class ReturnPostRequest(BaseModel):
    ar_account_id: UUID
    revenue_account_id: UUID


class WorkflowActionRequest(BaseModel):
    comments: str | None = None
