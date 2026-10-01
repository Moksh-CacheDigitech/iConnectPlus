"""Tests for upload hardening (VAPT stored XSS via attachments)."""

import pytest

from shared.upload_safety import (
    UnsafeUploadError,
    content_disposition_type,
    sanitize_filename,
    validate_upload,
)


def test_blocks_html_extension() -> None:
    with pytest.raises(UnsafeUploadError):
        validate_upload(
            file_name="xss.html",
            content_type="text/html",
            raw=b"<script>alert(1)</script>",
        )


def test_blocks_svg_extension() -> None:
    with pytest.raises(UnsafeUploadError):
        validate_upload(
            file_name="payload.svg",
            content_type="image/svg+xml",
            raw=b'<svg onload="alert(1)"></svg>',
        )


def test_blocks_html_masquerading_as_pdf() -> None:
    with pytest.raises(UnsafeUploadError):
        validate_upload(
            file_name="invoice.pdf",
            content_type="application/pdf",
            raw=b"<!DOCTYPE html><html><script>alert(1)</script></html>",
        )


def test_allows_pdf_bytes() -> None:
    name, media = validate_upload(
        file_name="quote.pdf",
        content_type="application/pdf",
        raw=b"%PDF-1.4 fake",
    )
    assert name == "quote.pdf"
    assert media == "application/pdf"
    assert content_disposition_type(name, media) == "attachment"


def test_sanitize_strips_path_and_specials() -> None:
    assert ".." not in sanitize_filename("../../evil.html")
    cleaned = sanitize_filename("1_--____script__svg_onload='_alert(Xss)_'_.pdf")
    assert "<" not in cleaned
    assert cleaned.endswith(".pdf")


def test_office_download_not_inline() -> None:
    assert content_disposition_type("boq.xlsx", "application/vnd.ms-excel") == "attachment"
