"""OLTP → read-model projection foundation (BI off hot tables).

Projections are written from outbox domain events; analytics queries should
prefer these tables over OLTP transactional tables when available.
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Numeric, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from database.mixins import TenantMixin


class AnaFinancePostingFact(Base, TenantMixin):
    """Lightweight finance posting fact for reporting (read model)."""

    __tablename__ = "ana_finance_posting_fact"
    __table_args__ = {"schema": "analytics"}

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    source_module: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    source_document_type: Mapped[str] = mapped_column(String(80), nullable=False)
    source_document_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False, index=True)
    journal_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    amount: Mapped[float | None] = mapped_column(Numeric(18, 4), nullable=True)
    payload_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    projected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


class AnaInventoryMovementFact(Base, TenantMixin):
    """Lightweight inventory movement fact for reporting (read model)."""

    __tablename__ = "ana_inventory_movement_fact"
    __table_args__ = {"schema": "analytics"}

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    source_module: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    movement_type: Mapped[str] = mapped_column(String(80), nullable=False)
    source_document_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False, index=True)
    product_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True, index=True)
    warehouse_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    quantity: Mapped[float | None] = mapped_column(Numeric(18, 4), nullable=True)
    payload_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    projected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


def project_finance_journal_posted(db, *, tenant_id: UUID, payload: dict) -> None:
    row = AnaFinancePostingFact(
        tenant_id=tenant_id,
        source_module=str(payload.get("source_module") or "unknown"),
        source_document_type=str(payload.get("aggregate_type") or payload.get("source_document_type") or "journal"),
        source_document_id=UUID(str(payload.get("invoice_id") or payload.get("aggregate_id") or payload.get("source_document_id"))),
        journal_id=UUID(str(payload["journal_id"])) if payload.get("journal_id") else None,
        amount=float(payload["amount"]) if payload.get("amount") is not None else None,
        payload_json=payload,
    )
    db.add(row)
    db.flush()


class AnaPayrollRunFact(Base, TenantMixin):
    """Lightweight payroll run fact for reporting (read model)."""

    __tablename__ = "ana_payroll_run_fact"
    __table_args__ = {"schema": "analytics"}

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    payroll_run_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False, index=True)
    company_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="posted")
    gross_amount: Mapped[float | None] = mapped_column(Numeric(18, 4), nullable=True)
    net_amount: Mapped[float | None] = mapped_column(Numeric(18, 4), nullable=True)
    payload_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    projected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


def project_inventory_movement(db, *, tenant_id: UUID, payload: dict) -> None:
    doc_id = payload.get("document_id") or payload.get("aggregate_id") or payload.get("source_document_id")
    if doc_id is None:
        return
    row = AnaInventoryMovementFact(
        tenant_id=tenant_id,
        source_module=str(payload.get("source_module") or "inventory"),
        movement_type=str(payload.get("movement_type") or payload.get("aggregate_type") or "movement"),
        source_document_id=UUID(str(doc_id)),
        product_id=UUID(str(payload["product_id"])) if payload.get("product_id") else None,
        warehouse_id=UUID(str(payload["warehouse_id"])) if payload.get("warehouse_id") else None,
        quantity=float(payload["quantity"]) if payload.get("quantity") is not None else None,
        payload_json=payload,
    )
    db.add(row)
    db.flush()


def project_payroll_run_posted(db, *, tenant_id: UUID, payload: dict) -> None:
    run_id = payload.get("payroll_run_id") or payload.get("aggregate_id") or payload.get("run_id")
    if run_id is None:
        return
    row = AnaPayrollRunFact(
        tenant_id=tenant_id,
        payroll_run_id=UUID(str(run_id)),
        company_id=UUID(str(payload["company_id"])) if payload.get("company_id") else None,
        status=str(payload.get("status") or "posted"),
        gross_amount=float(payload["gross_amount"]) if payload.get("gross_amount") is not None else None,
        net_amount=float(payload["net_amount"]) if payload.get("net_amount") is not None else None,
        payload_json=payload,
    )
    db.add(row)
    db.flush()
