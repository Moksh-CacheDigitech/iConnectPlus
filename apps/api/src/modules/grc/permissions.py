"""Alembic-only stubs for removed module (import graph).

Historical migrations still import these symbols. Tables/permissions
already exist in deployed DBs; upgrade() is not re-run for stamped revs.
"""

GRC_PERMISSIONS: list[str] = []
GRC_ADMIN_PERMISSIONS: list[str] = []
GRC_MANAGER_PERMISSIONS: list[str] = []
COMPLIANCE_OFFICER_PERMISSIONS: list[str] = []
RISK_MANAGER_PERMISSIONS: list[str] = []
