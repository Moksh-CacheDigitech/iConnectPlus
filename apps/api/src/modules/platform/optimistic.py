"""Shared optimistic locking helper (VersionMixin)."""

from __future__ import annotations

from typing import Any

from core.exceptions import ConflictException


class OptimisticLockError(ConflictException):
    def __init__(self, message: str = "Version conflict — reload and retry") -> None:
        super().__init__(message)


def assert_version(entity: Any, expected_version: int | None) -> None:
    """Raise if entity.version does not match the client-supplied expected version."""
    if expected_version is None:
        return
    current = getattr(entity, "version", None)
    if current is None:
        return
    if int(current) != int(expected_version):
        raise OptimisticLockError(
            f"Version conflict: expected {expected_version}, actual {current}"
        )


def bump_version(entity: Any) -> int:
    """Increment version after a successful update; returns new version."""
    current = int(getattr(entity, "version", 1) or 1)
    new_version = current + 1
    entity.version = new_version
    return new_version
