"""HttpOnly auth cookie helpers (VAPT: tokens in localStorage)."""

from __future__ import annotations

from fastapi import Response

from core.config import settings

ACCESS_COOKIE = settings.auth_cookie_access
REFRESH_COOKIE = settings.auth_cookie_refresh


def _cookie_kwargs(*, max_age: int) -> dict:
    same_site = (settings.auth_cookie_samesite or "lax").lower()
    if same_site not in {"lax", "strict", "none"}:
        same_site = "lax"
    # Secure cookies required when SameSite=None; locally allow insecure for http://localhost.
    secure = bool(settings.auth_cookie_secure)
    if settings.is_development and same_site != "none":
        secure = False
    return {
        "httponly": True,
        "secure": secure,
        "samesite": same_site,
        "path": "/",
        "max_age": max_age,
    }


def set_auth_cookies(
    response: Response,
    *,
    access_token: str | None,
    refresh_token: str | None,
) -> None:
    if access_token:
        response.set_cookie(
            ACCESS_COOKIE,
            access_token,
            **_cookie_kwargs(max_age=settings.jwt_access_token_expire_minutes * 60),
        )
    if refresh_token:
        response.set_cookie(
            REFRESH_COOKIE,
            refresh_token,
            **_cookie_kwargs(max_age=settings.jwt_refresh_token_expire_days * 86400),
        )


def clear_auth_cookies(response: Response) -> None:
    for name in (ACCESS_COOKIE, REFRESH_COOKIE):
        response.delete_cookie(name, path="/")
