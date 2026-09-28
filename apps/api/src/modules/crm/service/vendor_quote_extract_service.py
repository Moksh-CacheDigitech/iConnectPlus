"""Read line items off an uploaded vendor quotation to seed the customer quote."""

from __future__ import annotations

import base64
import binascii
from typing import Any

from core.exceptions import ValidationException
from modules.crm.domain.vendor_quote_extract import extract_vendor_quote_lines
from shared.document_text import ocr_available, text_from_bytes

MAX_QUOTE_BYTES = 12 * 1024 * 1024


def extract_vendor_quote(file_name: str, content_base64: str) -> dict[str, Any]:
    try:
        raw = base64.b64decode(content_base64, validate=True)
    except (ValueError, binascii.Error) as exc:
        raise ValidationException("Invalid quote file data. Re-upload the PDF, image or Excel file.") from exc
    if len(raw) > MAX_QUOTE_BYTES:
        raise ValidationException("Quote file is too large (max 12 MB)")
    text = text_from_bytes(raw, file_name or "quote.pdf", ocr=True)
    lines = extract_vendor_quote_lines(text)
    return {
        "lines": lines,
        "text_extracted": bool(text.strip()),
        "ocr_available": ocr_available(),
    }
