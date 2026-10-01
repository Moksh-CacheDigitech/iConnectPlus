"""Simple Redis-backed API rate limiting (AppScan / VAPT resource exhaustion)."""

from collections.abc import Awaitable, Callable

from redis.exceptions import RedisError
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from core.config import settings
from core.logging import get_logger
from core.redis import get_redis

logger = get_logger(__name__)

_EXEMPT_SUFFIXES = (
    "/health",
    "/auth/microsoft/config",
    "/auth/microsoft/login",
    "/auth/microsoft/callback",
    "/auth/microsoft/exchange",
    "/auth/login",
    "/auth/logout",
    "/auth/refresh",
    "/public/access-gate/verify",
    "/public/access-gate/session",
)

_WRITE_METHODS = frozenset({"POST", "PUT", "PATCH", "DELETE"})


def _client_key(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip() or "unknown"
    if request.client and request.client.host:
        return request.client.host
    return "unknown"


def _limit_response(limit: int, window: int, ttl: int) -> JSONResponse:
    return JSONResponse(
        status_code=429,
        content={
            "success": False,
            "message": "Too many requests. Please try again later.",
            "errors": [],
        },
        headers={
            "Retry-After": str(max(ttl, 1)),
            "X-RateLimit-Limit": str(limit),
            "X-RateLimit-Remaining": "0",
        },
    )


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Limit requests per client IP within a sliding fixed window."""

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        path = request.url.path or ""
        if any(path.endswith(suffix) or path == suffix for suffix in _EXEMPT_SUFFIXES):
            return await call_next(request)
        if not path.startswith("/api/"):
            return await call_next(request)

        method = (request.method or "GET").upper()
        is_write = method in _WRITE_METHODS
        if is_write:
            limit = int(getattr(settings, "api_write_rate_limit", 0) or 0)
            window = int(getattr(settings, "api_write_rate_window_seconds", 60) or 60)
            # Fall back to global API limit when write limit disabled.
            if limit <= 0:
                limit = int(getattr(settings, "api_rate_limit", 0) or 0)
                window = int(getattr(settings, "api_rate_window_seconds", 60) or 60)
            bucket = "write"
        else:
            limit = int(getattr(settings, "api_rate_limit", 0) or 0)
            window = int(getattr(settings, "api_rate_window_seconds", 60) or 60)
            bucket = "api"

        if limit <= 0:
            return await call_next(request)

        ip = _client_key(request)
        key = f"rate_limit:{bucket}:{ip}"
        try:
            client = get_redis()
            count = int(client.incr(key))
            if count == 1:
                client.expire(key, window)
            if count > limit:
                ttl = int(client.ttl(key) or window)
                return _limit_response(limit, window, ttl)
            remaining = max(limit - count, 0)
            response = await call_next(request)
            response.headers["X-RateLimit-Limit"] = str(limit)
            response.headers["X-RateLimit-Remaining"] = str(remaining)
            return response
        except RedisError as exc:
            logger.warning("API rate limit skipped (Redis unavailable): %s", exc)
            return await call_next(request)
        except Exception as exc:  # noqa: BLE001 - never block requests on limiter bugs
            logger.warning("API rate limit skipped: %s", exc)
            return await call_next(request)
