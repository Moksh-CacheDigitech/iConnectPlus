"""Unit tests for upload path detection in rate limiting."""

from starlette.requests import Request

from middleware.rate_limit import _is_upload_request


def _request(path: str, *, content_type: str | None = None, method: str = "POST") -> Request:
    headers: list[tuple[bytes, bytes]] = []
    if content_type:
        headers.append((b"content-type", content_type.encode()))
    scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": method,
        "scheme": "http",
        "path": path,
        "raw_path": path.encode(),
        "query_string": b"",
        "headers": headers,
        "client": ("127.0.0.1", 12345),
        "server": ("test", 80),
    }

    async def receive():
        return {"type": "http.request", "body": b"", "more_body": False}

    return Request(scope, receive)


def test_multipart_is_upload() -> None:
    assert _is_upload_request(
        _request("/api/v1/anything", content_type="multipart/form-data; boundary=x")
    )


def test_attachment_path_is_upload() -> None:
    assert _is_upload_request(_request("/api/v1/crm/attachments"))


def test_plain_create_is_not_upload() -> None:
    assert not _is_upload_request(
        _request("/api/v1/crm/leads", content_type="application/json")
    )
