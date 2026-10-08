"""Seed every catalog permission missing from sec_permission and grant to SUPER_ADMIN.

Idempotent: re-running only inserts codes that are still absent.
"""

import sys
from collections.abc import Sequence
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import sqlalchemy as sa
from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from modules.platform.permission_catalog import all_permission_entries

revision: str = "0633_permission_catalog_sync"
down_revision: str | Sequence[str] | None = "0632_payroll_run_fact"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()
    now = datetime.now(timezone.utc)
    existing = {
        row[0]
        for row in bind.execute(sa.text("SELECT permission_code FROM foundation.sec_permission"))
    }
    new_ids: list[str] = []
    for code, resource, action, module in all_permission_entries():
        if code in existing:
            continue
        perm_id = str(uuid4())
        new_ids.append(perm_id)
        bind.execute(
            sa.text(
                """
                INSERT INTO foundation.sec_permission
                (id, permission_code, resource, action, module, is_active, created_at)
                VALUES (:id, :code, :resource, :action, :module, true, :now)
                """
            ),
            {
                "id": perm_id,
                "code": code,
                "resource": resource,
                "action": action,
                "module": module,
                "now": now,
            },
        )
    if not new_ids:
        return
    super_admins = bind.execute(
        sa.text(
            "SELECT id, tenant_id FROM foundation.sec_role "
            "WHERE role_code = 'SUPER_ADMIN' AND is_deleted = false"
        )
    ).fetchall()
    for role_id, tenant_id in super_admins:
        for perm_id in new_ids:
            bind.execute(
                sa.text(
                    """
                    INSERT INTO foundation.sec_role_permission
                    (id, tenant_id, role_id, permission_id, granted_at)
                    VALUES (:id, :tid, :rid, :pid, :now)
                    """
                ),
                {
                    "id": str(uuid4()),
                    "tid": str(tenant_id),
                    "rid": str(role_id),
                    "pid": perm_id,
                    "now": now,
                },
            )


def downgrade() -> None:
    # Catalog rows may already be granted to custom roles; leave them in place.
    pass
