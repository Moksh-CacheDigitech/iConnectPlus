"""Alembic-only stubs for removed module (import graph).

Historical migrations still import these symbols. Tables/permissions
already exist in deployed DBs; upgrade() is not re-run for stamped revs.
"""

PORTAL_PERMISSIONS: list[str] = []
PORTAL_ADMIN_PERMISSIONS: list[str] = []
PORTAL_MANAGER_PERMISSIONS: list[str] = []
CUSTOMER_USER_PERMISSIONS: list[str] = []
SUPPORT_USER_PERMISSIONS: list[str] = []
