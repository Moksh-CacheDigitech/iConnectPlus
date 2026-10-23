"""IMAP support-mailbox reader (infrastructure)."""

from __future__ import annotations

import email
import imaplib
from dataclasses import dataclass
from datetime import datetime
from email.header import decode_header
from email.message import Message
from email.utils import parsedate_to_datetime

from core.config import settings
from shared.email_utils import parse_email_address, strip_html


@dataclass(frozen=True)
class MailboxMessage:
    uid: str
    message_id_header: str | None
    from_address: str
    from_name: str | None
    to_address: str | None
    subject: str
    body_text: str | None
    body_html: str | None
    received_raw: str
    received_at: datetime | None
    is_read: bool

    @property
    def preview(self) -> str:
        text = self.body_text or (strip_html(self.body_html) if self.body_html else "")
        return (text or "")[:2000]


def _decode_header_value(raw: str | None) -> str:
    out = ""
    for part, enc in decode_header(raw or ""):
        if isinstance(part, bytes):
            out += part.decode(enc or "utf-8", errors="replace")
        else:
            out += str(part)
    return out.strip()


def _bodies(msg: Message) -> tuple[str | None, str | None]:
    body_text = ""
    body_html = ""
    parts = msg.walk() if msg.is_multipart() else [msg]
    for part in parts:
        ctype = part.get_content_type()
        if ctype not in {"text/plain", "text/html"}:
            continue
        payload = part.get_payload(decode=True)
        if not payload:
            continue
        decoded = payload.decode(part.get_content_charset() or "utf-8", errors="replace")
        if ctype == "text/plain" and not body_text:
            body_text = decoded
        elif ctype == "text/html" and not body_html:
            body_html = decoded
    return body_text or None, body_html or None


def _parse(uid: str, raw: bytes, flags: bytes) -> MailboxMessage:
    msg = email.message_from_bytes(raw)
    from_name, from_addr = parse_email_address(msg.get("From", ""))
    body_text, body_html = _bodies(msg)
    date_hdr = msg.get("Date", "") or ""
    received_at: datetime | None = None
    if date_hdr:
        try:
            received_at = parsedate_to_datetime(date_hdr)
        except (TypeError, ValueError):
            received_at = None
    return MailboxMessage(
        uid=uid,
        message_id_header=msg.get("Message-ID") or msg.get("Message-Id"),
        from_address=from_addr,
        from_name=from_name or None,
        to_address=msg.get("To"),
        subject=(_decode_header_value(msg.get("Subject")) or "(No subject)")[:500],
        body_text=body_text,
        body_html=body_html,
        received_raw=date_hdr,
        received_at=received_at,
        is_read=b"\\Seen" in (flags or b""),
    )


class ImapMailboxAdapter:
    """Read-only access to the support mailbox; fetches never mark mail as read."""

    @property
    def configured(self) -> bool:
        return settings.imap_configured

    @property
    def mailbox(self) -> str:
        return settings.imap_user

    def _open(self) -> imaplib.IMAP4_SSL:
        client = imaplib.IMAP4_SSL(settings.imap_host, settings.imap_port)
        client.login(settings.imap_user, settings.imap_password)
        client.select(settings.imap_mailbox, readonly=True)
        return client

    @staticmethod
    def _fetch(client: imaplib.IMAP4_SSL, uid: str) -> MailboxMessage | None:
        status, data = client.uid("FETCH", uid, "(FLAGS BODY.PEEK[])")
        if status != "OK" or not data or not isinstance(data[0], tuple):
            return None
        meta, raw = data[0]
        return _parse(uid, raw, meta)

    def list_recent(self, *, top: int = 50) -> list[MailboxMessage]:
        client = self._open()
        try:
            status, data = client.uid("SEARCH", None, "ALL")
            if status != "OK" or not data or not data[0]:
                return []
            uids = [u.decode() for u in data[0].split()][-top:]
            messages = [self._fetch(client, uid) for uid in reversed(uids)]
            return [m for m in messages if m is not None]
        finally:
            client.logout()

    def get(self, uid: str) -> MailboxMessage | None:
        client = self._open()
        try:
            return self._fetch(client, uid)
        finally:
            client.logout()
