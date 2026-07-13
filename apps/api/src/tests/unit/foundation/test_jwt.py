"""Unit tests for JWT service."""

from uuid import uuid4

import pytest

from core.exceptions import UnauthorizedException
from security.jwt import JWTService


def test_create_and_decode_access_token() -> None:
    service = JWTService()
    user_id = uuid4()
    tenant_id = uuid4()
    session_id = uuid4()
    token = service.create_access_token(
        user_id=user_id,
        tenant_id=tenant_id,
        user_type="employee",
        session_id=session_id,
    )
    payload = service.decode_token(token, expected_type="access")
    assert payload["sub"] == str(user_id)
    assert payload["tenant_id"] == str(tenant_id)


def test_invalid_token_raises() -> None:
    service = JWTService()
    with pytest.raises(UnauthorizedException):
        service.decode_token("not-a-token", expected_type="access")
