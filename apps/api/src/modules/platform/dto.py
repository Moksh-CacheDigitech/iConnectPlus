"""Shared DTOs for platform ports (no ORM types)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID


@dataclass(frozen=True, slots=True)
class JournalLineDraft:
    account_id: UUID
    debit_amount: Decimal
    credit_amount: Decimal
    description: str = ""
    line_number: int | None = None


@dataclass(frozen=True, slots=True)
class SystemJournalDraft:
    """Idempotent system journal request for cross-module posting."""

    company_id: UUID
    branch_id: UUID
    description: str
    lines: tuple[JournalLineDraft, ...]
    idempotency_key: str
    journal_date: date | None = None
    fiscal_year_id: UUID | None = None
    source_module: str = ""
    source_document_type: str = ""
    source_document_id: UUID | None = None


@dataclass(frozen=True, slots=True)
class PostingResult:
    journal_id: UUID
    gl_entry_count: int
    already_posted: bool = False


@dataclass(frozen=True, slots=True)
class StockKey:
    company_id: UUID
    branch_id: UUID
    warehouse_id: UUID
    product_id: UUID
    uom_id: UUID
    bin_id: UUID | None = None
    batch_id: UUID | None = None


@dataclass(frozen=True, slots=True)
class StockMovementResultDTO:
    balance_id: UUID
    ledger_id: UUID | None
    on_hand_qty: Decimal
    reserved_qty: Decimal
    available_qty: Decimal
    reservation_id: UUID | None = None
    total_cost: Decimal | None = None


@dataclass(frozen=True, slots=True)
class MasterRef:
    id: UUID
    code: str | None
    name: str | None
    company_id: UUID | None = None
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class NotifyIntent:
    tenant_id: UUID
    event_type: str
    template_code: str
    recipient_user_id: UUID | None = None
    recipient_address: str | None = None
    payload: dict[str, Any] = field(default_factory=dict)
    channel: str = "in_app"
    idempotency_key: str | None = None
    created_by: UUID | None = None


@dataclass(frozen=True, slots=True)
class AuditIntent:
    tenant_id: UUID | None
    entity_name: str
    entity_id: UUID
    operation: str
    performed_by: UUID | None
    old_value: dict[str, Any] | None = None
    new_value: dict[str, Any] | None = None
    ip_address: str | None = None
    request_id: str | None = None


@dataclass(frozen=True, slots=True)
class WorkflowStartRequest:
    tenant_id: UUID
    workflow_code: str
    entity_name: str
    entity_id: UUID
    started_by: UUID


@dataclass(frozen=True, slots=True)
class WorkflowActionRequest:
    tenant_id: UUID
    instance_id: UUID
    performed_by: UUID
    comments: str | None = None


@dataclass(frozen=True, slots=True)
class NumberRequest:
    tenant_id: UUID
    company_id: UUID
    sequence_key: str
    prefix: str
    pad_width: int = 6
    year: int | None = None
    branch_id: UUID | None = None


@dataclass(frozen=True, slots=True)
class OutboxMessageDTO:
    id: UUID
    tenant_id: UUID
    event_type: str
    aggregate_type: str
    aggregate_id: UUID
    payload: dict[str, Any]
    idempotency_key: str
    status: str
    created_at: datetime
