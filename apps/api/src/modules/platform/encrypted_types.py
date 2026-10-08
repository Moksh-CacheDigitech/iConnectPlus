"""Column types that encrypt on write and decrypt on read (field-level encryption at rest).

Values are non-deterministic ciphertext, so these columns cannot be used in
equality filters; add a blind-index column if a lookup is ever required.
"""

from __future__ import annotations

from typing import Any

from sqlalchemy import Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.types import TypeDecorator

from modules.platform.encryption import decrypt_field, encrypt_field

_ENC_PREFIX = "enc:"
_BANK_SECRET_KEYS = ("account_number", "bank_account_number", "iban", "account_no")


def _encrypt(value: str | None) -> str | None:
    if not value or value.startswith(_ENC_PREFIX):
        return value
    return encrypt_field(value)


def _decrypt(value: str | None) -> str | None:
    if not value or not value.startswith(_ENC_PREFIX):
        return value
    return decrypt_field(value)


class EncryptedText(TypeDecorator):
    impl = Text
    cache_ok = True

    def process_bind_param(self, value: Any, dialect) -> Any:
        return _encrypt(value) if isinstance(value, str) else value

    def process_result_value(self, value: Any, dialect) -> Any:
        return _decrypt(value) if isinstance(value, str) else value


class EncryptedBankJSON(TypeDecorator):
    """JSONB whose bank account identifiers are encrypted."""

    impl = JSONB
    cache_ok = True

    def process_bind_param(self, value: Any, dialect) -> Any:
        return _map_bank_keys(value, _encrypt)

    def process_result_value(self, value: Any, dialect) -> Any:
        return _map_bank_keys(value, _decrypt)


def _map_bank_keys(value: Any, fn) -> Any:
    if not isinstance(value, dict):
        return value
    out = dict(value)
    for key in _BANK_SECRET_KEYS:
        if isinstance(out.get(key), str):
            out[key] = fn(out[key])
    return out
