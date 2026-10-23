"""Redis client and session cache."""

import hashlib
import json
import logging
from typing import Any, cast
from uuid import UUID

import redis
from redis.exceptions import RedisError

from core.config import settings
from core.exceptions import RedisUnavailableException

logger = logging.getLogger(__name__)

_redis_client: redis.Redis | None = None

# Fail fast when VM Redis is unreachable so FastAPI is not blocked (~260s Windows TCP).
_REDIS_SOCKET_TIMEOUT = 1.5


def get_redis() -> redis.Redis:
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.from_url(
            settings.redis_url,
            decode_responses=True,
            socket_connect_timeout=_REDIS_SOCKET_TIMEOUT,
            socket_timeout=_REDIS_SOCKET_TIMEOUT,
            retry_on_timeout=False,
            health_check_interval=30,
        )
    return _redis_client


class SessionStore:
    def __init__(self, client: redis.Redis | None = None) -> None:
        self._client = client or get_redis()
        self._ttl = settings.session_ttl_seconds

    def set_session(self, session_id: UUID, payload: dict[str, Any]) -> None:
        key = f"session:{session_id}"
        try:
            self._client.setex(key, self._ttl, json.dumps(payload))
        except RedisError as exc:
            logger.warning("Redis unavailable for set_session: %s", exc)

    def get_session(self, session_id: UUID) -> dict[str, Any] | None:
        try:
            raw = cast(str | None, self._client.get(f"session:{session_id}"))
        except RedisError as exc:
            logger.warning("Redis unavailable for get_session: %s", exc)
            return None
        if raw is None:
            return None
        return json.loads(raw)

    def delete_session(self, session_id: UUID) -> None:
        try:
            self._client.delete(f"session:{session_id}")
        except RedisError as exc:
            logger.warning("Redis unavailable for delete_session: %s", exc)

    def set_permissions(self, user_id: UUID, permissions: set[str]) -> None:
        key = f"permissions:{user_id}"
        ttl = settings.jwt_access_token_expire_minutes * 60
        try:
            self._client.setex(key, ttl, json.dumps(list(permissions)))
        except RedisError as exc:
            logger.warning("Redis unavailable for set_permissions: %s", exc)

    def get_permissions(self, user_id: UUID) -> set[str] | None:
        try:
            raw = cast(str | None, self._client.get(f"permissions:{user_id}"))
        except RedisError as exc:
            logger.warning("Redis unavailable for get_permissions: %s", exc)
            return None
        if raw is None:
            return None
        return set(json.loads(raw))

    def invalidate_permissions(self, user_id: UUID) -> None:
        try:
            self._client.delete(f"permissions:{user_id}")
        except RedisError as exc:
            logger.warning("Redis unavailable for invalidate_permissions: %s", exc)

    def touch_session(self, session_id: UUID, payload: dict[str, Any] | None = None) -> None:
        """Refresh session TTL; optionally replace cached payload."""
        key = f"session:{session_id}"
        try:
            if payload is not None:
                self._client.setex(key, self._ttl, json.dumps(payload))
                return
            raw = cast(str | None, self._client.get(key))
            if raw is not None:
                self._client.setex(key, self._ttl, raw)
        except RedisError as exc:
            logger.warning("Redis unavailable for touch_session: %s", exc)

    def increment_login_attempts(self, ip: str) -> int:
        """Return attempt count. When login_rate_limit <= 0, rate limiting is disabled."""
        if settings.login_rate_limit <= 0:
            return 0
        key = f"rate_limit:login:{ip}"
        try:
            count = cast(int, self._client.incr(key))
            if count == 1:
                self._client.expire(key, settings.login_rate_window_seconds)
            return count
        except RedisError as exc:
            logger.warning("Redis unavailable for increment_login_attempts: %s", exc)
            return 0

    @staticmethod
    def _reset_key(token: str) -> str:
        # Only a digest is stored so a Redis dump cannot be replayed as reset links.
        return f"password_reset:{hashlib.sha256(token.encode()).hexdigest()}"

    def set_password_reset(self, token: str, user_id: UUID, *, ttl_seconds: int) -> None:
        try:
            self._client.setex(self._reset_key(token), ttl_seconds, str(user_id))
        except RedisError as exc:
            logger.error("Redis unavailable for set_password_reset: %s", exc)
            raise RedisUnavailableException(
                "Password reset temporarily unavailable (session store unreachable)"
            ) from exc

    def pop_password_reset(self, token: str) -> UUID | None:
        key = self._reset_key(token)
        try:
            raw = cast(str | None, self._client.get(key))
            if raw is None:
                return None
            self._client.delete(key)
        except RedisError as exc:
            logger.error("Redis unavailable for pop_password_reset: %s", exc)
            raise RedisUnavailableException(
                "Password reset temporarily unavailable (session store unreachable)"
            ) from exc
        try:
            return UUID(raw)
        except ValueError:
            return None
