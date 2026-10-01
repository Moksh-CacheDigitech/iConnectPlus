"""Unit tests for ClamAV client helpers and contact normalization."""

from __future__ import annotations

from modules.crm.repository.contact_repository import (
    normalize_email,
    normalize_name,
    normalize_phone,
)
from shared.antivirus import ScanResult


def test_normalize_email_lower_strip() -> None:
    assert normalize_email("  Foo@Bar.COM ") == "foo@bar.com"
    assert normalize_email("") is None
    assert normalize_email(None) is None


def test_normalize_phone_digits() -> None:
    assert normalize_phone("+91-98765-43210") == "9876543210"
    assert normalize_phone("123") is None
    assert normalize_phone(None) is None


def test_normalize_name() -> None:
    assert normalize_name("Ada", "Lovelace") == "ada lovelace"
    assert normalize_name("Ada", None) == "ada"


def test_scan_result_dataclass() -> None:
    assert ScanResult(clean=True, skipped=True).skipped is True
