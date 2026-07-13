"""Unit tests for password hashing."""

import pytest

from modules.foundation.domain.exceptions import InvalidPasswordPolicyException
from security.password import PasswordHasher, validate_password_policy


def test_hash_and_verify_password() -> None:
    hashed = PasswordHasher.hash_password("Secure1!")
    assert PasswordHasher.verify_password("Secure1!", hashed)
    assert not PasswordHasher.verify_password("Wrong1!", hashed)


def test_password_policy_rejects_weak_password() -> None:
    with pytest.raises(InvalidPasswordPolicyException):
        validate_password_policy("short")
