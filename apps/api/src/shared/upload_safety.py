"""Server-side upload hardening (VAPT: stored XSS via HTML/SVG attachments)."""

from __future__ import annotations

import re
from pathlib import Path

# Active web content that executes under blob: / same-origin preview.
BLOCKED_EXTENSIONS = frozenset(
    {
        ".html",
        ".htm",
        ".xhtml",
        ".shtml",
        ".svg",
        ".svgz",
        ".js",
        ".mjs",
        ".jsx",
        ".ts",
        ".tsx",
        ".css",
        ".xml",
        ".xsl",
        ".xslt",
        ".hta",
        ".htaccess",
        ".php",
        ".phtml",
        ".asp",
        ".aspx",
        ".jsp",
        ".cgi",
        ".exe",
        ".bat",
        ".cmd",
        ".ps1",
        ".vbs",
        ".wsf",
        ".jar",
        ".war",
    }
)

# Business documents + images commonly used in CRM / procurement.
# Archives excluded by default (VAPT: uninspected archive / malware surface).
ALLOWED_EXTENSIONS = frozenset(
    {
        ".pdf",
        ".png",
        ".jpg",
        ".jpeg",
        ".gif",
        ".webp",
        ".tif",
        ".tiff",
        ".bmp",
        ".txt",
        ".csv",
        ".doc",
        ".docx",
        ".xls",
        ".xlsx",
        ".ppt",
        ".pptx",
        ".odt",
        ".ods",
        ".odp",
        ".rtf",
        ".msg",
        ".eml",
    }
)

# Never serve uploads inline — force download (VAPT stored XSS via attachments).
INLINE_SAFE_EXTENSIONS = frozenset()

BLOCKED_CONTENT_TYPES = frozenset(
    {
        "text/html",
        "application/xhtml+xml",
        "image/svg+xml",
        "text/javascript",
        "application/javascript",
        "application/x-javascript",
        "text/css",
        "application/xml",
        "text/xml",
    }
)

_SAFE_NAME_RE = re.compile(r"[^\w.\-()+ ]+", re.UNICODE)
_MULTI_DOT_RE = re.compile(r"\.{2,}")

DEFAULT_MAX_UPLOAD_BYTES = 25 * 1024 * 1024
DEFAULT_MAX_ATTACHMENTS_PER_ENTITY = 50
# Procurement PO commercial pack: Customer PO + Vendor Quote (VAPT two-slot policy).
PO_MAX_ATTACHMENTS = 2


class UnsafeUploadError(ValueError):
    """Raised when an upload fails extension, MIME, or content checks."""


def sanitize_filename(file_name: str, *, max_length: int = 180) -> str:
    """Strip path segments and dangerous characters from an upload name."""
    base = Path((file_name or "").strip().replace("\\", "/")).name
    cleaned = _SAFE_NAME_RE.sub("_", base).strip(" ._")
    cleaned = _MULTI_DOT_RE.sub(".", cleaned)
    if not cleaned:
        cleaned = "document"
    return cleaned[:max_length]


def file_extension(file_name: str) -> str:
    return Path(sanitize_filename(file_name)).suffix.lower()


def is_inline_safe(file_name: str, content_type: str | None = None) -> bool:
    ext = file_extension(file_name)
    if ext not in INLINE_SAFE_EXTENSIONS:
        return False
    media = (content_type or "").split(";")[0].strip().lower()
    if media in BLOCKED_CONTENT_TYPES:
        return False
    return True


def _looks_like_html_or_svg(raw: bytes) -> bool:
    head = raw[:4096].lstrip().lower()
    if not head:
        return False
    markers = (
        b"<!doctype html",
        b"<html",
        b"<svg",
        b"<script",
        b"<?xml",
    )
    return any(head.startswith(m) or m in head[:512] for m in markers)


def validate_upload(
    *,
    file_name: str,
    content_type: str | None,
    raw: bytes | None = None,
    max_bytes: int = DEFAULT_MAX_UPLOAD_BYTES,
) -> tuple[str, str | None]:
    """Validate upload metadata/bytes. Returns (safe_name, normalized_content_type)."""
    safe_name = sanitize_filename(file_name)
    ext = file_extension(safe_name)

    if not ext:
        raise UnsafeUploadError("Uploaded file must include a valid extension")
    if ext in BLOCKED_EXTENSIONS:
        raise UnsafeUploadError(
            f"File type '{ext}' is not allowed. Upload documents or images only."
        )
    if ext not in ALLOWED_EXTENSIONS:
        raise UnsafeUploadError(
            f"File type '{ext}' is not allowed. Allowed types include PDF, Office, and images."
        )

    media = (content_type or "").split(";")[0].strip().lower() or None
    if media and media in BLOCKED_CONTENT_TYPES:
        raise UnsafeUploadError(f"Content type '{media}' is not allowed")

    if raw is not None:
        if len(raw) <= 0:
            raise UnsafeUploadError("Uploaded file is empty")
        if len(raw) > max_bytes:
            raise UnsafeUploadError(
                f"Uploaded file exceeds the maximum size of {max_bytes // (1024 * 1024)} MB"
            )
        if _looks_like_html_or_svg(raw):
            raise UnsafeUploadError(
                "File content looks like HTML/SVG and cannot be uploaded"
            )
        # Antivirus (ClamAV) — VAPT 7.1.25
        try:
            from shared.antivirus import (
                AntivirusUnavailableError,
                MalwareDetectedError,
                scan_bytes,
            )

            scan_bytes(raw)
        except MalwareDetectedError as exc:
            raise UnsafeUploadError(str(exc)) from exc
        except AntivirusUnavailableError as exc:
            raise UnsafeUploadError(str(exc)) from exc

    return safe_name, media


def content_disposition_type(file_name: str, content_type: str | None = None) -> str:
    # Always force download — never inline-render user uploads (VAPT XSS).
    _ = file_name, content_type
    return "attachment"
