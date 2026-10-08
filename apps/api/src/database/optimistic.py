"""Re-export platform optimistic locking helpers at the database layer."""

from modules.platform.optimistic import OptimisticLockError, assert_version, bump_version

__all__ = ["OptimisticLockError", "assert_version", "bump_version"]
