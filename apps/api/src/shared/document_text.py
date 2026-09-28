"""Plain-text extraction from uploaded business documents (PDF, Excel, text, images).

Scanned PDFs and photos go through OCR. RapidOCR (pip-only, models bundled)
is preferred; Tesseract via ``pytesseract`` is used when RapidOCR is absent.
Both are optional - without them scanned documents simply yield no text.
"""

from __future__ import annotations

import logging
import re
import threading
from io import BytesIO
from typing import Any

IMAGE_SUFFIXES = (".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp", ".tif", ".tiff", ".heic", ".heif")

# A PDF with less extractable text than this is treated as scanned.
_MIN_PDF_TEXT_CHARS = 40
_MAX_OCR_PAGES = 6
_OCR_RENDER_SCALE = 2.0

_log = logging.getLogger(__name__)
_engine_lock = threading.Lock()
_rapid_engine: Any = None
_rapid_unavailable = False


def decode_pdf_parentheses(raw: bytes) -> str:
    parts: list[str] = []
    for match in re.finditer(rb"\((?:\\.|[^\\)])*\)", raw):
        chunk = match.group(0)[1:-1]
        chunk = chunk.replace(rb"\(", b"(").replace(rb"\)", b")").replace(rb"\\", b"\\")
        parts.append(chunk.decode("latin-1", errors="ignore"))
    if parts:
        return " ".join(parts)
    runs = re.findall(rb"[\x20-\x7e]{4,}", raw)
    return " ".join(r.decode("ascii", errors="ignore") for r in runs[:4000])


def text_from_pdf(raw: bytes) -> str | None:
    try:
        from pypdf import PdfReader

        reader = PdfReader(BytesIO(raw))
        chunks: list[str] = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                chunks.append(text)
        joined = "\n".join(chunks).strip()
        return joined if joined else None
    except Exception:
        return None


def text_from_excel(raw: bytes) -> str | None:
    try:
        from openpyxl import load_workbook

        workbook = load_workbook(BytesIO(raw), read_only=True, data_only=True)
        parts: list[str] = []
        for sheet in workbook.worksheets:
            for row in sheet.iter_rows(values_only=True):
                cells = [str(cell).strip() for cell in row if cell is not None and str(cell).strip()]
                if cells:
                    parts.append(" ".join(cells))
        joined = "\n".join(parts).strip()
        return joined if joined else None
    except Exception:
        return None


def text_from_xls(raw: bytes) -> str | None:
    try:
        import xlrd

        book = xlrd.open_workbook(file_contents=raw)
        parts: list[str] = []
        for sheet in book.sheets():
            for row_idx in range(sheet.nrows):
                cells = [
                    str(sheet.cell_value(row_idx, col_idx)).strip()
                    for col_idx in range(sheet.ncols)
                    if str(sheet.cell_value(row_idx, col_idx)).strip()
                ]
                if cells:
                    parts.append(" ".join(cells))
        joined = "\n".join(parts).strip()
        return joined if joined else None
    except Exception:
        return None


def _rapidocr_engine() -> Any:
    global _rapid_engine, _rapid_unavailable
    if _rapid_engine is not None or _rapid_unavailable:
        return _rapid_engine
    with _engine_lock:
        if _rapid_engine is None and not _rapid_unavailable:
            try:
                from rapidocr import RapidOCR

                _rapid_engine = RapidOCR()
            except Exception:  # not installed or failed to load models
                _rapid_unavailable = True
    return _rapid_engine


def _lines_top_to_bottom(boxes: Any, texts: Any) -> list[str]:
    """Group RapidOCR boxes into reading-order lines so labels stay next to their values."""
    items = []
    for box, text in zip(boxes, texts):
        ys = [point[1] for point in box]
        xs = [point[0] for point in box]
        items.append((min(ys), max(ys), min(xs), str(text)))
    items.sort(key=lambda item: (item[0], item[2]))
    lines: list[list[tuple[float, float, float, str]]] = []
    for item in items:
        if lines:
            top, bottom = lines[-1][0][0], lines[-1][0][1]
            mid = (item[0] + item[1]) / 2
            if top <= mid <= bottom:
                lines[-1].append(item)
                continue
        lines.append([item])
    return ["  ".join(part[3] for part in sorted(line, key=lambda p: p[2])) for line in lines]


def ocr_image(image: Any) -> str | None:
    """OCR one PIL image with the best available engine."""
    engine = _rapidocr_engine()
    if engine is not None:
        try:
            result = engine(image)
            if result is not None and getattr(result, "txts", None):
                return "\n".join(_lines_top_to_bottom(result.boxes, result.txts)).strip() or None
            return None
        except Exception:
            _log.warning("RapidOCR failed on an image", exc_info=True)
    try:
        import pytesseract

        return pytesseract.image_to_string(image).strip() or None
    except Exception:
        return None


def ocr_available() -> bool:
    if _rapidocr_engine() is not None:
        return True
    try:
        import pytesseract

        pytesseract.get_tesseract_version()
        return True
    except Exception:
        return False


def text_from_image_ocr(raw: bytes) -> str | None:
    """OCR a photo / scan; returns None when no OCR engine is installed."""
    try:
        from PIL import Image

        image = Image.open(BytesIO(raw))
        image.load()
        return ocr_image(image.convert("RGB"))
    except Exception:
        return None


def text_from_scanned_pdf(raw: bytes) -> str | None:
    """Render up to ``_MAX_OCR_PAGES`` pages with pdfium and OCR each one."""
    try:
        import pypdfium2 as pdfium
    except Exception:
        return None
    try:
        pdf = pdfium.PdfDocument(raw)
    except Exception:
        return None
    chunks: list[str] = []
    try:
        for index in range(min(len(pdf), _MAX_OCR_PAGES)):
            page = pdf[index]
            image = page.render(scale=_OCR_RENDER_SCALE).to_pil()
            text = ocr_image(image.convert("RGB"))
            if text:
                chunks.append(text)
    except Exception:
        _log.warning("Scanned PDF OCR failed", exc_info=True)
    finally:
        pdf.close()
    joined = "\n".join(chunks).strip()
    return joined or None


def _meaningful(text: str | None) -> bool:
    return bool(text) and len(re.sub(r"\s+", "", text or "")) >= _MIN_PDF_TEXT_CHARS


def text_from_bytes(raw: bytes, file_name: str, *, ocr: bool = False) -> str:
    lower = file_name.lower()
    if lower.endswith((".txt", ".csv")):
        return raw.decode("utf-8", errors="ignore")
    if lower.endswith((".xlsx", ".xlsm")):
        excel_text = text_from_excel(raw)
        if excel_text:
            return excel_text
    if lower.endswith(".xls"):
        xls_text = text_from_xls(raw)
        if xls_text:
            return xls_text
    if lower.endswith(".pdf") or raw[:4] == b"%PDF":
        pypdf_text = text_from_pdf(raw)
        if _meaningful(pypdf_text):
            return pypdf_text or ""
        if ocr and raw[:4] == b"%PDF":
            scanned = text_from_scanned_pdf(raw)
            if scanned:
                return scanned
        if pypdf_text:
            return pypdf_text
        if raw[:4] != b"%PDF":
            plain = raw.decode("utf-8", errors="ignore").strip()
            if plain:
                return plain
        return decode_pdf_parentheses(raw)
    if lower.endswith(IMAGE_SUFFIXES):
        return (text_from_image_ocr(raw) or "") if ocr else ""
    if lower.endswith((".doc", ".docx")):
        return raw.decode("utf-8", errors="ignore")
    return raw.decode("utf-8", errors="ignore")
