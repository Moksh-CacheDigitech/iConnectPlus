"""Reject unsafe data-entry strings and upload file names before handlers run."""

from __future__ import annotations

import json
from collections.abc import Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from core.config import settings
from core.logging import get_logger
from shared.input_validation import (
    UnsafeInputError,
    assert_safe_filename,
    extract_multipart_filenames,
    validate_json_entries,
)

logger = get_logger(__name__)

_WRITE_METHODS = frozenset({"POST", "PUT", "PATCH", "DELETE"})
_EXEMPT_SUFFIXES = (
    "/health",
    "/auth/login",
    "/auth/refresh",
    "/public/access-gate/verify",
    "/public/access-gate/session",
)


def _error(message: str, *, status_code: int = 422) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "message": message,
            "errors": [message],
        },
    )


class InputValidationMiddleware(BaseHTTPMiddleware):
    """Platform-wide validation for JSON entries and multipart upload names."""

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        path = request.url.path or ""
        if not path.startswith("/api/"):
            return await call_next(request)
        if any(path.endswith(suffix) or path == suffix for suffix in _EXEMPT_SUFFIXES):
            return await call_next(request)

        method = (request.method or "GET").upper()
        if method not in _WRITE_METHODS:
            return await call_next(request)

        content_type = (request.headers.get("content-type") or "").lower()
        max_upload = int(getattr(settings, "api_max_upload_request_bytes", 0) or 0)
        content_length = request.headers.get("content-length")
        if (
            max_upload > 0
            and content_length
            and content_length.isdigit()
            and (
                "multipart/form-data" in content_type
                or "content_base64" in path
                or "/upload" in path
                or "/attachment" in path
            )
            and int(content_length) > max_upload
        ):
            return _error(
                f"Upload exceeds maximum request size of {max_upload // (1024 * 1024)} MB",
                status_code=413,
            )

        if "application/json" in content_type:
            body = await request.body()
            if body:
                try:
                    payload = json.loads(body)
                except json.JSONDecodeError:
                    # Let FastAPI/Pydantic return the normal 422 for bad JSON.
                    return await _replay(request, body, call_next)
                try:
                    validate_json_entries(
                        payload,
                        max_string_length=int(
                            getattr(settings, "api_max_entry_string_length", 20_000) or 20_000
                        ),
                    )
                except UnsafeInputError as exc:
                    return _error(str(exc))
            return await _replay(request, body, call_next)

        if "multipart/form-data" in content_type:
            body = await request.body()
            if body:
                try:
                    for name in extract_multipart_filenames(body):
                        assert_safe_filename(name, required=True)
                except UnsafeInputError as exc:
                    return _error(str(exc))
            return await _replay(request, body, call_next)

        return await call_next(request)


async def _replay(
    request: Request,
    body: bytes,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    async def receive() -> dict:
        return {"type": "http.request", "body": body, "more_body": False}

    return await call_next(Request(request.scope, receive))
