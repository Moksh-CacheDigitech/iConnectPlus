"""SMTP email delivery adapter (infrastructure)."""

from __future__ import annotations

import smtplib
from dataclasses import dataclass
from email.message import EmailMessage

from core.config import settings
from shared.email_utils import strip_html


@dataclass(frozen=True)
class EmailSendResult:
    ok: bool
    status_code: int
    message: str
    provider_response: str


class SmtpEmailAdapter:
    """Sends HTML mail (with a plain-text alternative) through the configured SMTP relay."""

    def __init__(
        self,
        *,
        host: str | None = None,
        port: int | None = None,
        user: str | None = None,
        password: str | None = None,
        from_email: str | None = None,
        use_tls: bool | None = None,
    ) -> None:
        self._host = (host if host is not None else settings.smtp_host).strip()
        self._port = int(port if port is not None else settings.smtp_port)
        self._user = (user if user is not None else settings.smtp_user).strip()
        self._password = password if password is not None else settings.smtp_password
        self._from_email = (from_email if from_email is not None else settings.smtp_from_address).strip()
        self._use_tls = settings.smtp_use_tls if use_tls is None else use_tls

    @property
    def configured(self) -> bool:
        return bool(self._host and self._from_email)

    @property
    def from_email(self) -> str:
        return self._from_email

    def _connect(self) -> smtplib.SMTP:
        # Hostinger (and many hosts) use implicit SSL on 465; 587 uses STARTTLS.
        if self._port == 465:
            client: smtplib.SMTP = smtplib.SMTP_SSL(self._host, self._port, timeout=30)
        else:
            client = smtplib.SMTP(self._host, self._port, timeout=30)
            if self._use_tls:
                client.starttls()
        if self._user:
            client.login(self._user, self._password)
        return client

    def send_mail(self, *, to_address: str, subject: str, body_html: str) -> EmailSendResult:
        recipient = (to_address or "").strip()
        if not recipient:
            return EmailSendResult(False, 400, "Recipient address is required", "missing_recipient")
        if not self.configured:
            return EmailSendResult(False, 503, "SMTP is not configured", "smtp_not_configured")

        msg = EmailMessage()
        msg["Subject"] = subject or "(no subject)"
        msg["From"] = self._from_email
        msg["To"] = recipient
        msg.set_content(strip_html(body_html or "") or " ")
        if body_html:
            msg.add_alternative(body_html, subtype="html")

        try:
            with self._connect() as client:
                refused = client.send_message(msg)
        except (smtplib.SMTPException, OSError) as exc:
            return EmailSendResult(False, 502, f"SMTP send failed: {exc}", str(exc)[:2000])
        if refused:
            return EmailSendResult(False, 502, "SMTP relay refused recipient", str(refused)[:2000])
        return EmailSendResult(True, 250, "accepted", f"smtp:{self._host}:{self._port}")

    def test_connection(self) -> EmailSendResult:
        if not self.configured:
            diag = settings.smtp_diagnostics()
            missing = ", ".join(diag["missing"]) or "unknown"
            return EmailSendResult(
                False,
                503,
                f"SMTP settings incomplete. Missing: {missing}",
                f"missing={diag['missing']}; hint={diag['hint']}",
            )
        try:
            with self._connect() as client:
                client.noop()
        except (smtplib.SMTPException, OSError) as exc:
            return EmailSendResult(False, 502, f"SMTP connection failed: {exc}", str(exc)[:2000])
        return EmailSendResult(True, 200, "SMTP connection OK", f"from={self._from_email}")
