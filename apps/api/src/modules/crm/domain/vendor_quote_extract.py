"""Line items from a vendor / OEM / distributor quotation.

Formats vary per supplier, so a row is only accepted when three of its
trailing numbers reconcile as quantity x rate = amount (within 1%). That
rejects totals, tax rows and phone numbers while tolerating HSN columns,
Indian digit grouping (5,90,000.00) and wrapped descriptions.
"""

from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation
from typing import Any

_NUMBER_RE = re.compile(r"(?<![\w.,/-])(\d{1,3}(?:,\d{2,3})+(?:\.\d+)?|\d+(?:\.\d+)?)(?![\w%/])")
_GST_RE = re.compile(r"(?<![\d.])(5|12|18|28|0\.25|3)(?:\.0+)?\s*%")
_SERIAL_RE = re.compile(r"^\s*(?:\d{1,3}\s*[.)\-:]?\s+|[a-z]\)\s+)", re.IGNORECASE)
_HSN_RE = re.compile(r"\b(\d{4}|\d{6}|\d{8})\s*$")
_SKIP_RE = re.compile(
    r"\b(sub\s*-?\s*total|grand\s*total|total|cgst|sgst|igst|gst\s*amount|tax(?:able)?\s*(?:value|amount)|"
    r"freight|round(?:ing)?\s*off|amount\s*in\s*words|bank|ifsc|a/c|account\s*no|gstin|pan\b|phone|mobile|"
    r"email|quote\s*(?:no|date)|quotation\s*(?:no|date)|valid|page\s*\d)",
    re.IGNORECASE,
)
_HEADER_RE = re.compile(r"\b(description|particulars|item)\b.*\b(qty|quantity)\b", re.IGNORECASE)

_MAX_QTY = Decimal("100000")


def _to_decimal(token: str) -> Decimal | None:
    try:
        return Decimal(token.replace(",", ""))
    except InvalidOperation:
        return None


def _clean_description(text: str) -> tuple[str, str | None]:
    text = _SERIAL_RE.sub("", text).strip(" -:|\t")
    hsn = None
    match = _HSN_RE.search(text)
    if match and len(text) > len(match.group(1)) + 2:
        hsn = match.group(1)
        text = text[: match.start()].rstrip(" -:|\t")
    return re.sub(r"\s{2,}", " ", text).strip(), hsn


def _parse_line(line: str) -> dict[str, Any] | None:
    if _SKIP_RE.search(line) or _HEADER_RE.search(line):
        return None
    tokens = [(m.start(), m.group(1), _to_decimal(m.group(1))) for m in _NUMBER_RE.finditer(line)]
    tokens = [t for t in tokens if t[2] is not None]
    if len(tokens) < 3:
        return None
    tail = tokens[-6:]
    # Right-most qty/rate/amount triple wins (amount is usually the last column).
    for k in range(len(tail) - 1, 1, -1):
        amount = tail[k][2]
        for j in range(k - 1, 0, -1):
            rate = tail[j][2]
            for i in range(j - 1, -1, -1):
                qty = tail[i][2]
                if qty is None or rate is None or amount is None:
                    continue
                if qty <= 0 or qty > _MAX_QTY or qty != qty.to_integral_value() or rate <= 0:
                    continue
                if abs(qty * rate - amount) > max(Decimal("1"), amount * Decimal("0.01")):
                    continue
                description, hsn = _clean_description(line[: tail[i][0]])
                gst = _GST_RE.search(line[tail[i][0] :])
                return {
                    "product_name": description,
                    "hsn_sac": hsn,
                    "qty": qty,
                    "unit_cost": rate,
                    "line_total": amount,
                    "gst_pct": Decimal(gst.group(1)) if gst else None,
                }
    return None


def extract_vendor_quote_lines(text: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    pending_description: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            pending_description = []
            continue
        parsed = _parse_line(line)
        if parsed is None:
            # Remember wrapped description text that precedes a numbers-only row.
            if not _NUMBER_RE.search(line) or len(line.split()) >= 2:
                if not _SKIP_RE.search(line) and not _HEADER_RE.search(line):
                    pending_description = (pending_description + [line])[-2:]
            continue
        if len(parsed["product_name"]) < 3 and pending_description:
            parsed["product_name"], hsn = _clean_description(" ".join(pending_description))
            parsed["hsn_sac"] = parsed["hsn_sac"] or hsn
        pending_description = []
        if not parsed["product_name"]:
            parsed["product_name"] = f"Item {len(rows) + 1}"
        parsed["product_name"] = parsed["product_name"][:255]
        rows.append(parsed)
    return rows
