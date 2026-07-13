"""Seed foundation permissions and system role templates."""

import sys
from collections.abc import Sequence
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import sqlalchemy as sa
from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from modules.foundation.permissions import FOUNDATION_PERMISSIONS, SYSTEM_ROLE_CODES

revision: str = "0004_seed_permissions_roles"
down_revision: str | None = "0003_foundation_tables"
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

ROLE_TABLE = sa.table(
    "sec_role",
    sa.column("id", sa.Uuid),
    sa.column("tenant_id", sa.Uuid),
    sa.column("role_code", sa.String),
    sa.column("role_name", sa.String),
    sa.column("is_system_role", sa.Boolean),
    sa.column("status", sa.String),
    sa.column("created_at", sa.DateTime(timezone=True)),
    sa.column("updated_at", sa.DateTime(timezone=True)),
    sa.column("version", sa.Integer),
    sa.column("is_deleted", sa.Boolean),
    schema="foundation",
)


def upgrade() -> None:
    conn = op.get_bind()
    now = datetime.now(timezone.utc)
    permission_ids: dict[str, str] = {}

    for code, resource, action, module in FOUNDATION_PERMISSIONS:
        perm_id = str(uuid4())
        permission_ids[code] = perm_id
        exists = conn.execute(
            sa.text(
                "SELECT 1 FROM foundation.sec_permission WHERE permission_code = :code"
            ),
            {"code": code},
        ).first()
        if exists:
            continue
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

    # Bootstrap tenant for system role seeds (dev/bootstrap tenant)
    tenant_row = conn.execute(
        sa.text("SELECT id FROM foundation.sec_tenant WHERE tenant_code = 'BOOTSTRAP'")
    ).first()
    if tenant_row is None:
        tenant_id = str(uuid4())
        conn.execute(
            sa.text(
                """
                INSERT INTO foundation.sec_tenant
                (id, tenant_code, tenant_name, status, timezone, locale, created_at, updated_at, version, is_deleted)
                VALUES (:id, 'BOOTSTRAP', 'Bootstrap Tenant', 'active', 'UTC', 'en', :now, :now, 1, false)
                """
            ),
            {"id": tenant_id, "now": now},
        )
    else:
        tenant_id = str(tenant_row[0])

    role_ids: dict[str, str] = {}
    for role_code in SYSTEM_ROLE_CODES:
        existing = conn.execute(
            sa.text(
                "SELECT id FROM foundation.sec_role WHERE tenant_id = :tid AND role_code = :code"
            ),
            {"tid": tenant_id, "code": role_code},
        ).first()
        if existing:
            role_ids[role_code] = str(existing[0])
            continue
        role_id = str(uuid4())
        role_ids[role_code] = role_id
        conn.execute(
            sa.insert(ROLE_TABLE).values(
                id=role_id,
                tenant_id=tenant_id,
                role_code=role_code,
                role_name=role_code.replace("_", " ").title(),
                is_system_role=True,
                status="active",
                created_at=now,
                updated_at=now,
                version=1,
                is_deleted=False,
            )
        )

    super_admin_id = role_ids.get("SUPER_ADMIN")
    if super_admin_id:
        for perm_id in permission_ids.values():
            exists = conn.execute(
                sa.text(
                    """
                    SELECT 1 FROM foundation.sec_role_permission
                    WHERE role_id = :rid AND permission_id = :pid
                    """
                ),
                {"rid": super_admin_id, "pid": perm_id},
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
                    "rid": super_admin_id,
                    "pid": perm_id,
                    "now": now,
                },
            )


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(sa.text("DELETE FROM foundation.sec_role_permission"))
    conn.execute(
        sa.text("DELETE FROM foundation.sec_role WHERE role_code IN ('SUPER_ADMIN', 'TENANT_ADMIN')")
    )
    conn.execute(sa.text("DELETE FROM foundation.sec_permission"))
    conn.execute(sa.text("DELETE FROM foundation.sec_tenant WHERE tenant_code = 'BOOTSTRAP'"))
