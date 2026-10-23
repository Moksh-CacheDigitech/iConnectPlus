"""Read support mailbox messages for Service Head / Engineer inbox UI."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from modules.service.adapters.imap_mailbox_adapter import ImapMailboxAdapter, MailboxMessage
from modules.service.email_inbound_schemas import MailboxMessageDetail, MailboxMessageItem, MailboxMessagesResult
from modules.service.models import SvcEmailIngestLog
from modules.service.models.service_request import SvcServiceRequest
from modules.service.service.email_to_ticket_service import EmailToTicketService
from modules.service.service.mailbox_ticket_classifier import classify_mailbox_message, resolved_subject_patterns


def _message_id_keys(*values: str | None) -> list[str]:
    keys: list[str] = []
    for raw in values:
        candidate = (raw or "").strip()
        if not candidate:
            continue
        if candidate not in keys:
            keys.append(candidate)
        if candidate.startswith("<") and candidate.endswith(">"):
            inner = candidate[1:-1].strip()
            if inner and inner not in keys:
                keys.append(inner)
        else:
            wrapped = f"<{candidate}>"
            if wrapped not in keys:
                keys.append(wrapped)
    return keys


def _ticket_fields(ticket: SvcServiceRequest | None) -> dict:
    if ticket is None:
        return {
            "ticket_id": None,
            "document_number": None,
            "ticket_status": None,
            "opened_at": None,
            "resolved_at": None,
            "closed_at": None,
        }
    return {
        "ticket_id": ticket.id,
        "document_number": ticket.document_number,
        "ticket_status": ticket.status,
        "opened_at": ticket.opened_at,
        "resolved_at": ticket.resolved_at,
        "closed_at": ticket.closed_at,
    }


def _row(msg: MailboxMessage) -> dict:
    return {
        "mailbox_id": msg.uid,
        "message_id": EmailToTicketService.message_id_from_headers(
            msg.message_id_header, msg.from_address, msg.subject, msg.received_raw
        ),
        "internet_message_id": msg.message_id_header,
        "from_address": msg.from_address,
        "from_name": msg.from_name,
        "subject": msg.subject,
        "body_preview": msg.preview,
        "body_text": msg.body_text[:50000] if msg.body_text else None,
        "body_html": msg.body_html[:50000] if msg.body_html else None,
        "received_at": msg.received_at,
        "is_read": msg.is_read,
    }


class MailboxInboxService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._adapter = ImapMailboxAdapter()

    def _require_configured(self) -> None:
        if not self._adapter.configured:
            raise RuntimeError(
                "Support mailbox is not configured. Set IMAP_ENABLED, IMAP_HOST, IMAP_USER and IMAP_PASSWORD."
            )

    def _ingest_logs(self, rows: list[dict]) -> dict[str, SvcEmailIngestLog]:
        keys: set[str] = set()
        for row in rows:
            keys.update(_message_id_keys(row["message_id"], row.get("internet_message_id")))
        by_key: dict[str, SvcEmailIngestLog] = {}
        if not keys:
            return by_key
        for log in self._db.scalars(
            select(SvcEmailIngestLog).where(SvcEmailIngestLog.message_id.in_(keys))
        ).all():
            for key in _message_id_keys(log.message_id):
                by_key.setdefault(key, log)
        return by_key

    @staticmethod
    def _log_for(row: dict, logs: dict[str, SvcEmailIngestLog]) -> SvcEmailIngestLog | None:
        for key in _message_id_keys(row["message_id"], row.get("internet_message_id")):
            if key in logs:
                return logs[key]
        return None

    def _tickets(self, logs: list[SvcEmailIngestLog]) -> dict[UUID, SvcServiceRequest]:
        ids = [log.request_id for log in logs if log.request_id]
        if not ids:
            return {}
        rows = self._db.scalars(select(SvcServiceRequest).where(SvcServiceRequest.id.in_(ids))).all()
        return {ticket.id: ticket for ticket in rows}

    def _item_fields(self, row: dict, logs: dict[str, SvcEmailIngestLog], tickets: dict[UUID, SvcServiceRequest]) -> dict:
        log = self._log_for(row, logs)
        ticket = tickets.get(log.request_id) if log and log.request_id else None
        return {
            "mailbox_id": row["mailbox_id"],
            "message_id": row["message_id"],
            "internet_message_id": row["internet_message_id"],
            "from_address": row["from_address"],
            "from_name": row["from_name"],
            "subject": row["subject"],
            "body_preview": row["body_preview"],
            "received_at": row["received_at"],
            "is_read": row["is_read"],
            "classification": classify_mailbox_message(
                subject=row["subject"], from_address=row["from_address"]
            ),
            "ingest_status": log.status if log else None,
            **_ticket_fields(ticket),
        }

    def list_messages(self, *, top: int = 50) -> MailboxMessagesResult:
        self._require_configured()
        rows = [_row(msg) for msg in self._adapter.list_recent(top=top)]
        logs = self._ingest_logs(rows)
        tickets = self._tickets(list(logs.values()))
        items = [MailboxMessageItem(**self._item_fields(row, logs, tickets)) for row in rows]
        return MailboxMessagesResult(
            mailbox=self._adapter.mailbox,
            total=len(items),
            subject_patterns=resolved_subject_patterns(),
            messages=items,
        )

    def get_message(self, mailbox_id: str) -> MailboxMessageDetail:
        self._require_configured()
        msg = self._adapter.get(mailbox_id)
        if msg is None:
            raise LookupError("Mailbox message not found")
        row = _row(msg)
        logs = self._ingest_logs([row])
        tickets = self._tickets(list(logs.values()))
        return MailboxMessageDetail(
            **self._item_fields(row, logs, tickets),
            body_text=row["body_text"],
            body_html=row["body_html"],
        )
