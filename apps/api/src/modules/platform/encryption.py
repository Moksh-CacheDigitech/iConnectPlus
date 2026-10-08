"""Field-level encrypt / mask helpers for classified sensitive data.

Keys come from ``FIELD_ENCRYPTION_KEYS`` (comma-separated, first encrypts, all
decrypt). The key derived from ``JWT_SECRET_KEY`` is kept as a decrypt-only
fallback for values written before dedicated keys existed, and as the encrypt
key only when no dedicated key is configured.
"""

from __future__ import annotations

import base64
import hashlib
import logging
from functools import lru_cache

from cryptography.fernet import Fernet, MultiFernet

from core.config import settings
from modules.platform.data_classification import ENCRYPTED_FIELD_INVENTORY

logger = logging.getLogger(__name__)

_PREFIX = "enc:v1:"
_LEGACY_HMAC_PREFIX = "enc:hmac:"
_DEFAULT_JWT_SECRET = "change-me-in-production"


def _derive(secret: str) -> Fernet:
    digest = hashlib.sha256(secret.encode("utf-8")).digest()
    return Fernet(base64.urlsafe_b64encode(digest))


@lru_cache(maxsize=1)
def _cipher() -> MultiFernet:
    dedicated = [k.strip() for k in (settings.field_encryption_keys or "").split(",") if k.strip()]
    jwt_secret = (settings.jwt_secret_key or "").strip()
    if not dedicated:
        if not settings.is_development and (not jwt_secret or jwt_secret == _DEFAULT_JWT_SECRET):
            raise RuntimeError(
                "FIELD_ENCRYPTION_KEYS (or a non-default JWT_SECRET_KEY) is required outside development"
            )
        logger.warning("FIELD_ENCRYPTION_KEYS not set; deriving field encryption key from JWT secret")
    keys = [_derive(k) for k in dedicated]
    if jwt_secret:
        keys.append(_derive(jwt_secret))
    return MultiFernet(keys)


def encrypt_field(value: str | None) -> str | None:
    if value is None or value == "":
        return value
    return _PREFIX + _cipher().encrypt(value.encode("utf-8")).decode("utf-8")


def decrypt_field(value: str | None) -> str | None:
    if value is None or value == "":
        return value
    if value.startswith(_PREFIX):
        return _cipher().decrypt(value.removeprefix(_PREFIX).encode("utf-8")).decode("utf-8")
    if value.startswith(_LEGACY_HMAC_PREFIX):
        # Pre-fix fallback format stored the plaintext base64-encoded.
        parts = value.split(":", 3)
        if len(parts) == 4:
            return base64.urlsafe_b64decode(parts[3].encode()).decode("utf-8")
    return value


def mask_field(value: str | None, *, visible_tail: int = 4) -> str:
    if not value:
        return ""
    if len(value) <= visible_tail:
        return "*" * len(value)
    return ("*" * (len(value) - visible_tail)) + value[-visible_tail:]


def should_encrypt_field(field_name: str) -> bool:
    return field_name in ENCRYPTED_FIELD_INVENTORY
