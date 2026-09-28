"""Heuristic extraction of header fields from a customer purchase order.

Customer PO formats differ per customer (and per circle for telcos), so every
field is best-effort and stays editable in the UI.
"""

from __future__ import annotations

import re
from datetime import date, datetime
from typing import Any, Iterable

from modules.crm.domain.delivery_timeline import parse_delivery_weeks

GSTIN_RE = re.compile(r"\b(\d{2}[A-Z]{5}\d{4}[A-Z][1-9A-Z]Z[0-9A-Z])\b")

GST_STATE_CODES: dict[str, str] = {
    "01": "Jammu and Kashmir", "02": "Himachal Pradesh", "03": "Punjab", "04": "Chandigarh",
    "05": "Uttarakhand", "06": "Haryana", "07": "Delhi", "08": "Rajasthan", "09": "Uttar Pradesh",
    "10": "Bihar", "11": "Sikkim", "12": "Arunachal Pradesh", "13": "Nagaland", "14": "Manipur",
    "15": "Mizoram", "16": "Tripura", "17": "Meghalaya", "18": "Assam", "19": "West Bengal",
    "20": "Jharkhand", "21": "Odisha", "22": "Chhattisgarh", "23": "Madhya Pradesh", "24": "Gujarat",
    "26": "Dadra and Nagar Haveli and Daman and Diu", "27": "Maharashtra", "29": "Karnataka",
    "30": "Goa", "31": "Lakshadweep", "32": "Kerala", "33": "Tamil Nadu", "34": "Puducherry",
    "35": "Andaman and Nicobar Islands", "36": "Telangana", "37": "Andhra Pradesh", "38": "Ladakh",
}

_PO_NUMBER_PATTERNS = (
    r"purchase\s*order\s*(?:no\.?|number|#)\s*[:\-]?\s*([A-Za-z0-9][A-Za-z0-9/_\-.]{2,49})",
    r"\bp\.?\s*o\.?\s*(?:no\.?|number|#)\s*[:\-]?\s*([A-Za-z0-9][A-Za-z0-9/_\-.]{2,49})",
    r"\border\s*(?:no\.?|number|#)\s*[:\-]?\s*([A-Za-z0-9][A-Za-z0-9/_\-.]{2,49})",
)
_DATE_TOKEN = r"(\d{1,2}[-/.]\d{1,2}[-/.]\d{2,4}|\d{4}-\d{2}-\d{2}|\d{1,2}[- ][A-Za-z]{3,9}[- ,]+\d{2,4})"
_PO_DATE_PATTERNS = (
    rf"purchase\s*order\s*date\s*[:\-]?\s*{_DATE_TOKEN}",
    rf"\bp\.?\s*o\.?\s*date\s*[:\-]?\s*{_DATE_TOKEN}",
    rf"\border\s*date\s*[:\-]?\s*{_DATE_TOKEN}",
    rf"\bdated?\s*[:\-]?\s*{_DATE_TOKEN}",
)
_DATE_FORMATS = (
    "%d-%m-%Y", "%d/%m/%Y", "%d.%m.%Y", "%Y-%m-%d", "%d-%m-%y", "%d/%m/%y", "%d.%m.%y",
    "%d-%b-%Y", "%d %b %Y", "%d-%B-%Y", "%d %B %Y", "%d %b, %Y", "%d %B, %Y", "%d-%b-%y",
)
_ADDRESS_STOP = re.compile(
    r"^(ship\s*to|deliver\s*to|bill\s*to|invoice\s*to|gstin|gst\s*no|pan|sr\.?\s*no|s\.?\s*no|item|"
    r"description|terms|kind\s*attn|contact|phone|email|po\s*no|p\.o)",
    re.IGNORECASE,
)


def parse_date_token(token: str) -> date | None:
    cleaned = re.sub(r"\s+", " ", token.strip().rstrip(",."))
    for fmt in _DATE_FORMATS:
        try:
            parsed = datetime.strptime(cleaned, fmt).date()
        except ValueError:
            continue
        if 2000 <= parsed.year <= 2100:
            return parsed
    return None


def find_po_number(text: str) -> str | None:
    for pattern in _PO_NUMBER_PATTERNS:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            value = match.group(1).strip().rstrip(".-/")
            if value.lower() not in {"date", "dated"} and any(ch.isdigit() for ch in value):
                return value[:100]
    return None


def find_po_date(text: str) -> date | None:
    for pattern in _PO_DATE_PATTERNS:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            parsed = parse_date_token(match.group(1))
            if parsed:
                return parsed
    return None


def find_gstins(text: str, exclude: Iterable[str] = ()) -> list[str]:
    blocked = {g.strip().upper() for g in exclude if g}
    seen: list[str] = []
    for match in GSTIN_RE.finditer(text.upper()):
        gstin = match.group(1)
        if gstin in blocked or gstin in seen:
            continue
        seen.append(gstin)
    return seen


def _address_block(lines: list[str], label: str) -> str | None:
    pattern = re.compile(rf"^\s*{label}\s*[:\-]?\s*(.*)$", re.IGNORECASE)
    for idx, line in enumerate(lines):
        match = pattern.match(line)
        if not match:
            continue
        parts = [match.group(1).strip()] if match.group(1).strip() else []
        for follow in lines[idx + 1 : idx + 6]:
            stripped = follow.strip()
            if not stripped or _ADDRESS_STOP.match(stripped):
                break
            parts.append(stripped)
        text = ", ".join(p for p in parts if p)
        return text[:1000] or None
    return None


def extract_customer_po_fields(text: str, *, own_gstins: Iterable[str] = ()) -> dict[str, Any]:
    lines = [ln for ln in text.splitlines()]
    gstins = find_gstins(text, exclude=own_gstins)
    weeks = parse_delivery_weeks(text)
    registrations = [
        {
            "gstin": gstin,
            "state_code": gstin[:2],
            "state": GST_STATE_CODES.get(gstin[:2]),
        }
        for gstin in gstins
    ]
    fields = {
        "po_number": find_po_number(text),
        "po_date": find_po_date(text),
        "billing_address": _address_block(lines, r"(?:bill(?:ing)?\s*to|invoice\s*to|buyer)"),
        "shipping_address": _address_block(lines, r"(?:ship(?:ping)?\s*to|deliver(?:y)?\s*(?:to|address))"),
        "gst_registrations": registrations,
        "delivery_weeks_min": weeks[0] if weeks else None,
        "delivery_weeks_max": weeks[1] if weeks else None,
    }
    found = [k for k in ("po_number", "po_date", "billing_address", "shipping_address") if fields[k]]
    fields["fields_found"] = found + (["gst_registrations"] if registrations else [])
    fields["text_extracted"] = bool(text.strip())
    return fields
