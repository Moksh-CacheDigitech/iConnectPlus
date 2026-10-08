"""SSRF-guarded outbound HTTP for Integration Hub connectors."""

from __future__ import annotations

import hashlib
import hmac
import ipaddress
import json
import socket
from typing import Any
from urllib.parse import urlparse

import httpx

from core.config import get_settings

_TIMEOUT = httpx.Timeout(10.0, connect=5.0)


class OutboundBlockedError(ValueError):
    """Target URL is not an allowed public endpoint."""


class OutboundDeliveryError(RuntimeError):
    """Remote endpoint rejected or failed the delivery (retryable via outbox)."""


def _blocked(ip: ipaddress.IPv4Address | ipaddress.IPv6Address) -> bool:
    if ip.version == 6 and ip.ipv4_mapped is not None:
        ip = ip.ipv4_mapped
    return bool(
        ip.is_loopback
        or ip.is_private
        or ip.is_link_local
        or ip.is_multicast
        or ip.is_reserved
        or ip.is_unspecified
    )


def guard_outbound_url(url: str) -> str:
    parsed = urlparse(url)
    if (parsed.scheme or "").lower() not in {"http", "https"}:
        raise OutboundBlockedError("Outbound URL must use http or https")
    host = (parsed.hostname or "").strip().lower().rstrip(".")
    if not host:
        raise OutboundBlockedError("Outbound URL has no host")

    settings = get_settings()
    allowed = tuple(
        h.strip().lower().rstrip(".")
        for h in (settings.integration_outbound_allowed_hosts or "").split(",")
        if h.strip()
    )
    if allowed:
        if not any(host == a or host.endswith("." + a) for a in allowed):
            raise OutboundBlockedError(f"Host {host!r} is not in INTEGRATION_OUTBOUND_ALLOWED_HOSTS")
    elif not settings.is_development:
        raise OutboundBlockedError("Set INTEGRATION_OUTBOUND_ALLOWED_HOSTS to enable outbound webhooks")

    try:
        literal = ipaddress.ip_address(host.strip("[]"))
        ips = [literal]
    except ValueError:
        try:
            ips = [ipaddress.ip_address(info[4][0]) for info in socket.getaddrinfo(host, None)]
        except socket.gaierror as exc:
            raise OutboundBlockedError(f"Host {host!r} did not resolve") from exc
    for ip in ips:
        if _blocked(ip):
            raise OutboundBlockedError(f"Host {host!r} resolves to non-public address {ip}")
    return host


def post_json(
    url: str,
    body: dict[str, Any],
    *,
    idempotency_key: str,
    request_id: str | None,
) -> int:
    guard_outbound_url(url)
    raw = json.dumps(body, default=str, separators=(",", ":")).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "Idempotency-Key": idempotency_key,
    }
    if request_id:
        headers["X-Request-ID"] = request_id
    secret = (get_settings().integration_webhook_signing_secret or "").encode("utf-8")
    if secret:
        headers["X-ERP-Signature"] = "sha256=" + hmac.new(secret, raw, hashlib.sha256).hexdigest()
    try:
        with httpx.Client(timeout=_TIMEOUT, follow_redirects=False) as client:
            response = client.post(url, content=raw, headers=headers)
    except httpx.HTTPError as exc:
        raise OutboundDeliveryError(f"Webhook delivery failed: {exc.__class__.__name__}") from exc
    if response.status_code >= 300:
        raise OutboundDeliveryError(f"Webhook returned HTTP {response.status_code}")
    return response.status_code
