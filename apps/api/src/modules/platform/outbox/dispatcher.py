"""Drain pending outbox messages into domain handlers."""

from __future__ import annotations

import logging
from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from modules.platform.domain_events import publish_domain_event
from modules.platform.outbox.repository import OutboxRepository
from modules.platform.read_models import (
    project_finance_journal_posted,
    project_inventory_movement,
    project_payroll_run_posted,
)

logger = logging.getLogger(__name__)


class OutboxDispatcher:
    """Routes outbox event_type → handler. Keep handlers thin and idempotent."""

    def __init__(self, db: Session) -> None:
        self._db = db
        self._repo = OutboxRepository(db)

    def process_batch(self, *, limit: int = 50) -> dict[str, int]:
        rows = self._repo.claim_batch(limit=limit)
        ok = 0
        failed = 0
        for row in rows:
            try:
                self._dispatch(row.event_type, row.payload_json, row.tenant_id)
                self._repo.mark_processed(row)
                self._db.commit()
                ok += 1
            except Exception as exc:
                logger.exception("Outbox dispatch failed for %s", row.id)
                self._db.rollback()
                # Re-load after rollback
                fresh = self._db.get(type(row), row.id)
                if fresh is not None:
                    self._repo.mark_failed(fresh, str(exc))
                    self._db.commit()
                failed += 1
        return {"processed": ok, "failed": failed, "claimed": len(rows)}

    def _dispatch(self, event_type: str, payload: dict[str, Any], tenant_id: UUID) -> None:
        if event_type.startswith("notify."):
            self._handle_notify(payload, tenant_id)
            return
        if event_type.startswith("audit."):
            self._handle_audit(payload, tenant_id)
            return
        if event_type.startswith("finance."):
            self._handle_finance(payload, tenant_id)
            return
        if event_type.startswith("integration."):
            self._handle_integration(payload, tenant_id)
            return
        if event_type.startswith("domain."):
            self._handle_domain(event_type, payload, tenant_id)
            return
        raise ValueError(f"Unknown outbox event_type: {event_type}")

    def _handle_domain(self, event_type: str, payload: dict[str, Any], tenant_id: UUID) -> None:
        aggregate_type = str(payload.get("aggregate_type") or "domain")
        aggregate_id = _uuid_or_none(
            payload.get("aggregate_id") or payload.get("invoice_id") or payload.get("grn_id")
        )
        if aggregate_id is None:
            aggregate_id = tenant_id
        publish_domain_event(
            event_type=event_type,
            tenant_id=tenant_id,
            aggregate_type=aggregate_type,
            aggregate_id=aggregate_id,
            payload=payload,
        )
        try:
            if event_type == "domain.finance.journal_posted":
                project_finance_journal_posted(
                    self._db,
                    tenant_id=tenant_id,
                    payload={**payload, "aggregate_type": aggregate_type, "aggregate_id": str(aggregate_id)},
                )
            elif event_type.startswith("domain.inventory."):
                project_inventory_movement(
                    self._db,
                    tenant_id=tenant_id,
                    payload={**payload, "aggregate_type": aggregate_type, "aggregate_id": str(aggregate_id)},
                )
            elif event_type.startswith("domain.payroll."):
                project_payroll_run_posted(
                    self._db,
                    tenant_id=tenant_id,
                    payload={**payload, "aggregate_type": aggregate_type, "aggregate_id": str(aggregate_id)},
                )
        except Exception:
            logger.exception("Read-model projection failed for %s", event_type)

    def _handle_notify(self, payload: dict[str, Any], tenant_id: UUID) -> None:
        from modules.platform.adapters.notify_adapter import NotifyAdapter
        from modules.platform.dto import NotifyIntent

        intent = NotifyIntent(
            tenant_id=tenant_id,
            event_type=str(payload.get("event_type") or "notify"),
            template_code=str(payload["template_code"]),
            recipient_user_id=_uuid_or_none(payload.get("recipient_user_id")),
            recipient_address=payload.get("recipient_address"),
            payload=dict(payload.get("payload") or {}),
            channel=str(payload.get("channel") or "in_app"),
            idempotency_key=payload.get("idempotency_key"),
            created_by=_uuid_or_none(payload.get("created_by")),
        )
        NotifyAdapter(self._db).publish(intent)

    def _handle_audit(self, payload: dict[str, Any], tenant_id: UUID) -> None:
        from modules.platform.adapters.audit_adapter import AuditAdapter
        from modules.platform.dto import AuditIntent

        intent = AuditIntent(
            tenant_id=tenant_id,
            entity_name=str(payload["entity_name"]),
            entity_id=UUID(str(payload["entity_id"])),
            operation=str(payload["operation"]),
            performed_by=_uuid_or_none(payload.get("performed_by")),
            old_value=payload.get("old_value"),
            new_value=payload.get("new_value"),
            ip_address=payload.get("ip_address"),
            request_id=payload.get("request_id"),
        )
        AuditAdapter(self._db).log_entity_change(intent)

    def _handle_finance(self, payload: dict[str, Any], tenant_id: UUID) -> None:
        from datetime import date
        from decimal import Decimal

        from modules.foundation.domain.value_objects import TenantContext
        from modules.platform.adapters.finance_adapter import FinancePostingAdapter
        from modules.platform.dto import JournalLineDraft, SystemJournalDraft

        lines = tuple(
            JournalLineDraft(
                account_id=UUID(str(line["account_id"])),
                debit_amount=Decimal(str(line.get("debit_amount") or 0)),
                credit_amount=Decimal(str(line.get("credit_amount") or 0)),
                description=str(line.get("description") or ""),
                line_number=line.get("line_number"),
            )
            for line in payload.get("lines") or []
        )
        draft = SystemJournalDraft(
            company_id=UUID(str(payload["company_id"])),
            branch_id=UUID(str(payload["branch_id"])),
            description=str(payload.get("description") or ""),
            lines=lines,
            idempotency_key=str(payload["idempotency_key"]),
            journal_date=date.fromisoformat(payload["journal_date"])
            if payload.get("journal_date")
            else None,
            fiscal_year_id=_uuid_or_none(payload.get("fiscal_year_id")),
            source_module=str(payload.get("source_module") or ""),
            source_document_type=str(payload.get("source_document_type") or ""),
            source_document_id=_uuid_or_none(payload.get("source_document_id")),
        )
        ctx = TenantContext(
            tenant_id=tenant_id,
            user_id=_uuid_or_none(payload.get("user_id")) or tenant_id,
            user_type="system",
            company_id=draft.company_id,
            branch_id=draft.branch_id,
        )
        FinancePostingAdapter(self._db).post_system_journal(ctx, draft)

    def _handle_integration(self, payload: dict[str, Any], tenant_id: UUID) -> None:
        from modules.platform.adapters.integration_adapter import IntegrationGatewayAdapter

        IntegrationGatewayAdapter(self._db).dispatch_outbound(
            tenant_id=tenant_id,
            system_code=str(payload["system_code"]),
            operation=str(payload["operation"]),
            payload=dict(payload.get("payload") or {}),
            idempotency_key=str(payload["idempotency_key"]),
        )


def _uuid_or_none(value: Any) -> UUID | None:
    if value is None or value == "":
        return None
    return UUID(str(value))
