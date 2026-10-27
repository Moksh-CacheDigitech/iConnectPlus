"""Alembic-only stubs for removed module (import graph).

Historical migrations still import these symbols. Tables/permissions
already exist in deployed DBs; upgrade() is not re-run for stamped revs.
"""

INTEGRATION_PERMISSIONS: list[str] = []
INTEGRATION_ADMIN_PERMISSIONS: list[str] = []
INTEGRATION_ENGINEER_PERMISSIONS: list[str] = []
API_MANAGER_PERMISSIONS: list[str] = []
SYSTEM_OPERATOR_PERMISSIONS: list[str] = []
