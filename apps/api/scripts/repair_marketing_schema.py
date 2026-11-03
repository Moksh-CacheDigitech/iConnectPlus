"""Create marketing schema/tables + permissions without waiting for full alembic head.

Usage (from apps/api or docker erp-api):
  python -m scripts.repair_marketing_schema
"""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from sqlalchemy import text

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from database.session import SessionLocal  # noqa: E402
# Register FK targets in SQLAlchemy metadata before create().
from modules.foundation.models.security import SecTenant  # noqa: E402, F401
from modules.organization.models.branch import OrgBranch  # noqa: E402, F401
from modules.organization.models.company import OrgCompany  # noqa: E402, F401
from modules.marketing.models.approval import MktApproval  # noqa: E402
from modules.marketing.models.brand_voice import MktBrandVoice  # noqa: E402
from modules.marketing.models.brand_voice_source import MktBrandVoiceSource  # noqa: E402
from modules.marketing.models.calendar_entry import MktCalendarEntry  # noqa: E402
from modules.marketing.models.campaign import MktCampaign  # noqa: E402
from modules.marketing.models.competitor import MktCompetitor  # noqa: E402
from modules.marketing.models.content_pillar import MktContentPillar  # noqa: E402
from modules.marketing.models.content_request import MktContentRequest  # noqa: E402
from modules.marketing.models.generated_content import MktGeneratedContent  # noqa: E402
from modules.marketing.models.generated_content_version import (  # noqa: E402
    MktGeneratedContentVersion,
)
from modules.marketing.models.m365_file import MktM365File  # noqa: E402
from modules.marketing.models.m365_meeting import MktM365Meeting  # noqa: E402
from modules.marketing.models.m365_workspace import MktM365Workspace  # noqa: E402
from modules.marketing.models.ops_event import MktOpsEvent  # noqa: E402
from modules.marketing.models.platform import MktPlatform  # noqa: E402
from modules.marketing.models.publish_job import MktPublishJob  # noqa: E402
from modules.marketing.models.research_report import MktResearchReport  # noqa: E402
from modules.marketing.models.social_account import MktSocialAccount  # noqa: E402
from modules.marketing.models.social_inbox import MktSocialInbox  # noqa: E402
from modules.marketing.models.task import MktTask  # noqa: E402
from modules.marketing.models.time_entry import MktTimeEntry  # noqa: E402
from modules.marketing.models.trend_report import MktTrendReport  # noqa: E402
from modules.marketing.permissions import (  # noqa: E402
    MARKETING_ADMIN_PERMISSIONS,
    MARKETING_EDITOR_PERMISSIONS,
    MARKETING_MANAGER_PERMISSIONS,
    MARKETING_PERMISSIONS,
    MARKETING_VIEWER_PERMISSIONS,
)

TABLES = [
    MktPlatform,
    MktCampaign,
    MktContentPillar,
    MktBrandVoice,
    MktBrandVoiceSource,
    MktSocialAccount,
    MktContentRequest,
    MktGeneratedContent,
    MktGeneratedContentVersion,
    MktResearchReport,
    MktTrendReport,
    MktCompetitor,
    MktCalendarEntry,
    MktPublishJob,
    MktTask,
    MktTimeEntry,
    MktApproval,
    MktM365Workspace,
    MktM365File,
    MktM365Meeting,
    MktOpsEvent,
    MktSocialInbox,
]

ROLE_SPECS = [
    ("MARKETING_MANAGER", "Marketing Manager", MARKETING_MANAGER_PERMISSIONS),
    ("MARKETING_EDITOR", "Marketing Editor", MARKETING_EDITOR_PERMISSIONS),
    ("MARKETING_VIEWER", "Marketing Viewer", MARKETING_VIEWER_PERMISSIONS),
    ("MARKETING_ADMIN", "Marketing Admin", MARKETING_ADMIN_PERMISSIONS),
]

ADDITIVE_COLUMNS = [
    "ALTER TABLE marketing.mkt_campaign ADD COLUMN IF NOT EXISTS priority VARCHAR(20) NOT NULL DEFAULT 'medium'",
    "ALTER TABLE marketing.mkt_campaign ADD COLUMN IF NOT EXISTS success_metrics JSONB",
    "ALTER TABLE marketing.mkt_campaign ADD COLUMN IF NOT EXISTS stakeholders JSONB",
    "ALTER TABLE marketing.mkt_campaign ADD COLUMN IF NOT EXISTS departments JSONB",
    "ALTER TABLE marketing.mkt_campaign ADD COLUMN IF NOT EXISTS approvers JSONB",
    "ALTER TABLE marketing.mkt_content_request ADD COLUMN IF NOT EXISTS purpose VARCHAR(255)",
    "ALTER TABLE marketing.mkt_content_request ADD COLUMN IF NOT EXISTS technical_depth VARCHAR(40)",
    "ALTER TABLE marketing.mkt_content_request ADD COLUMN IF NOT EXISTS keywords TEXT",
    "ALTER TABLE marketing.mkt_content_request ADD COLUMN IF NOT EXISTS reference_notes TEXT",
    "ALTER TABLE marketing.mkt_content_request ADD COLUMN IF NOT EXISTS assigned_to_user_id UUID",
    "ALTER TABLE marketing.mkt_content_request ADD COLUMN IF NOT EXISTS due_at TIMESTAMPTZ",
    "ALTER TABLE marketing.mkt_brand_voice ADD COLUMN IF NOT EXISTS brand_kit JSONB",
]


def main() -> None:
    db = SessionLocal()
    try:
        db.execute(text("CREATE SCHEMA IF NOT EXISTS marketing"))
        db.commit()
        bind = db.get_bind()
        for model in TABLES:
            model.__table__.create(bind=bind, checkfirst=True)
        for stmt in ADDITIVE_COLUMNS:
            db.execute(text(stmt))

        now = datetime.now(timezone.utc)
        perm_ids: dict[str, str] = {}
        for code, resource, action, module in MARKETING_PERMISSIONS:
            row = db.execute(
                text("SELECT id FROM foundation.sec_permission WHERE permission_code = :c"),
                {"c": code},
            ).first()
            if row:
                perm_ids[code] = str(row[0])
                db.execute(
                    text("UPDATE foundation.sec_permission SET is_active=true WHERE id=:id"),
                    {"id": perm_ids[code]},
                )
            else:
                pid = str(uuid4())
                db.execute(
                    text(
                        """
                        INSERT INTO foundation.sec_permission
                        (id, permission_code, resource, action, module, is_active, created_at)
                        VALUES (:id, :code, :resource, :action, :module, true, :now)
                        """
                    ),
                    {
                        "id": pid,
                        "code": code,
                        "resource": resource,
                        "action": action,
                        "module": module,
                        "now": now,
                    },
                )
                perm_ids[code] = pid

        def ensure_role(tid: str, code: str, name: str) -> str:
            row = db.execute(
                text(
                    """
                    SELECT id FROM foundation.sec_role
                    WHERE tenant_id=:tid AND role_code=:code
                    ORDER BY CASE WHEN coalesce(is_deleted,false) THEN 1 ELSE 0 END
                    LIMIT 1
                    """
                ),
                {"tid": tid, "code": code},
            ).first()
            if row:
                db.execute(
                    text(
                        """
                        UPDATE foundation.sec_role
                        SET is_deleted=false, deleted_at=NULL, deleted_by=NULL,
                            role_name=:name, status='active', updated_at=:now
                        WHERE id=:id
                        """
                    ),
                    {"id": str(row[0]), "name": name, "now": now},
                )
                return str(row[0])
            rid = str(uuid4())
            db.execute(
                text(
                    """
                    INSERT INTO foundation.sec_role
                    (id, tenant_id, role_code, role_name, is_system_role, status,
                     created_at, updated_at, is_deleted, version)
                    VALUES (:id,:tid,:code,:name,true,'active',:now,:now,false,1)
                    """
                ),
                {"id": rid, "tid": tid, "code": code, "name": name, "now": now},
            )
            return rid

        def grant(tid: str, rid: str, pid: str) -> None:
            exists = db.execute(
                text(
                    "SELECT 1 FROM foundation.sec_role_permission WHERE role_id=:r AND permission_id=:p"
                ),
                {"r": rid, "p": pid},
            ).first()
            if exists:
                return
            db.execute(
                text(
                    """
                    INSERT INTO foundation.sec_role_permission
                    (id, tenant_id, role_id, permission_id, granted_at)
                    VALUES (:id,:tid,:r,:p,:now)
                    """
                ),
                {"id": str(uuid4()), "tid": tid, "r": rid, "p": pid, "now": now},
            )

        tenants = db.execute(
            text("SELECT id FROM foundation.sec_tenant WHERE is_deleted = false")
        ).fetchall()
        for (tenant_id,) in tenants:
            tid = str(tenant_id)
            for role_code, role_name, perms in ROLE_SPECS:
                rid = ensure_role(tid, role_code, role_name)
                for perm_code in perms:
                    grant(tid, rid, perm_ids[perm_code])
            for role_code in ("SUPER_ADMIN", "TENANT_ADMIN"):
                role = db.execute(
                    text(
                        """
                        SELECT id FROM foundation.sec_role
                        WHERE tenant_id=:tid AND role_code=:code
                          AND coalesce(is_deleted,false)=false LIMIT 1
                        """
                    ),
                    {"tid": tid, "code": role_code},
                ).first()
                if role:
                    for pid in perm_ids.values():
                        grant(tid, str(role[0]), pid)

        db.commit()
        print("Marketing schema/tables/permissions restored.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
