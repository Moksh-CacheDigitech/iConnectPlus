"""Seed master data permissions."""

import sys
from collections.abc import Sequence
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import sqlalchemy as sa
from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from modules.master_data.permissions import MASTER_PERMISSIONS

revision: str = "0021_seed_master_permissions"
down_revision: str | None = "0020_cross_module_employee_fk"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

PERMISSION_TABLE = sa.table(
    "sec_permission",
    sa.column("id", sa.Uuid),
    sa.column("permission_code", sa.String),
    sa.column("resource", sa.String),
    sa.column("action", sa.String),
    sa.column("module", sa.String),
    sa.column("is_active", sa.Boolean),
    sa.column("created_at", sa.DateTime(timezone=True)),
    schema="foundation",
)


def upgrade() -> None:
    conn = op.get_bind()
    now = datetime.now(timezone.utc)
    permission_ids: list[str] = []

    for code, resource, action, module in MASTER_PERMISSIONS:
        exists = conn.execute(
            sa.text("SELECT id FROM foundation.sec_permission WHERE permission_code = :code"),
            {"code": code},
        ).first()
        if exists:
            permission_ids.append(str(exists[0]))
            continue
        perm_id = str(uuid4())
        permission_ids.append(perm_id)
        conn.execute(
            sa.insert(PERMISSION_TABLE).values(
                id=perm_id,
                permission_code=code,
                resource=resource,
                action=action,
                module=module,
                is_active=True,
                created_at=now,
            )
        )

    super_admin = conn.execute(
        sa.text(
            """
            SELECT r.id, r.tenant_id FROM foundation.sec_role r
            WHERE r.role_code = 'SUPER_ADMIN' AND r.is_deleted = false
            LIMIT 1
            """
        )
    ).first()
    if super_admin:
        role_id, tenant_id = str(super_admin[0]), str(super_admin[1])
        for perm_id in permission_ids:
            exists = conn.execute(
                sa.text(
                    """
                    SELECT 1 FROM foundation.sec_role_permission
                    WHERE role_id = :rid AND permission_id = :pid
                    """
                ),
                {"rid": role_id, "pid": perm_id},
            ).first()
            if exists:
                continue
            conn.execute(
                sa.text(
                    """
                    INSERT INTO foundation.sec_role_permission
                    (id, tenant_id, role_id, permission_id, granted_at)
                    VALUES (:id, :tid, :rid, :pid, :now)
                    """
                ),
                {
                    "id": str(uuid4()),
                    "tid": tenant_id,
                    "rid": role_id,
                    "pid": perm_id,
                    "now": now,
                },
            )


def downgrade() -> None:
    conn = op.get_bind()
    codes = [p[0] for p in MASTER_PERMISSIONS]
    for code in codes:
        conn.execute(
            sa.text(
                """
                DELETE FROM foundation.sec_role_permission
                WHERE permission_id IN (
                    SELECT id FROM foundation.sec_permission WHERE permission_code = :code
                )
                """
            ),
            {"code": code},
        )
        conn.execute(
            sa.text("DELETE FROM foundation.sec_permission WHERE permission_code = :code"),
            {"code": code},
        )
