"""Alembic-only stubs for removed module (import graph).

Historical migrations still import these symbols. Tables/permissions
already exist in deployed DBs; upgrade() is not re-run for stamped revs.
"""

SALES_PERMISSIONS: list[str] = []
SALES_EXECUTIVE_PERMISSIONS: list[str] = []
SALES_MANAGER_PERMISSIONS: list[str] = []
FINANCE_REVIEWER_PERMISSIONS: list[str] = []
