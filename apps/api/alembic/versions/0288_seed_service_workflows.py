"""Seed service workflow definitions per ERD_16."""

from collections.abc import Sequence
from datetime import datetime, timezone
from uuid import uuid4

import sqlalchemy as sa
from alembic import op

revision: str = "0288_seed_service_workflows"
down_revision: str | None = "0287_seed_service_permissions"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

WORKFLOWS: list[tuple[str, str, str, list[tuple[int, str, str, str]]]] = [
    (
        "SVC_REQUEST_APPROVAL",
        "Service Request Approval",
        "svc_service_request",
        [
            (1, "SERVICE_COORDINATOR", "Coordinator Submit", "role"),
            (2, "SERVICE_MANAGER", "Service Manager Approval", "role"),
        ],
    ),
    (
        "SVC_WORK_ORDER_APPROVAL",
        "Service Work Order Approval",
        "svc_service_work_order",
        [
            (1, "SERVICE_COORDINATOR", "Coordinator Submit", "role"),
            (2, "SERVICE_MANAGER", "Service Manager Approval", "role"),
        ],
    ),
    (
        "SVC_COMPLETION_APPROVAL",
        "Service Completion Approval",
        "svc_service_resolution",
        [
            (1, "SERVICE_ENGINEER", "Engineer Submit", "role"),
            (2, "SERVICE_MANAGER", "Service Manager Approval", "role"),
        ],
    ),
    (
        "SVC_SLA_ESCALATION",
        "Service SLA Escalation",
        "svc_service_escalation",
        [
            (1, "SERVICE_ENGINEER", "Agent Escalation", "role"),
            (2, "SERVICE_COORDINATOR", "Supervisor Escalation", "role"),
            (3, "SERVICE_MANAGER", "Manager Escalation", "role"),
        ],
    ),
    (
        "SVC_CONTRACT_APPROVAL",
        "Service Contract Approval",
        "svc_service_contract",
        [
            (1, "SERVICE_MANAGER", "Service Manager Submit", "role"),
            (2, "SERVICE_ADMIN", "Service Admin Approval", "role"),
        ],
    ),
]


def upgrade() -> None:
    conn = op.get_bind()
    now = datetime.now(timezone.utc)
    tenants = conn.execute(
        sa.text("SELECT id FROM foundation.sec_tenant WHERE is_deleted = false")
    ).fetchall()
    for (tenant_id,) in tenants:
        tid = str(tenant_id)
        for workflow_code, workflow_name, document_type, steps in WORKFLOWS:
            exists = conn.execute(
                sa.text(
                    """
                    SELECT id FROM foundation.wf_definition
                    WHERE tenant_id = :tid AND workflow_code = :code AND version_no = 1
                    """
                ),
                {"tid": tid, "code": workflow_code},
            ).first()
            if exists:
                wf_id = str(exists[0])
            else:
                wf_id = str(uuid4())
                conn.execute(
                    sa.text(
                        """
                        INSERT INTO foundation.wf_definition
                        (id, tenant_id, workflow_code, workflow_name, module,
                         document_type, version_no, is_active, created_at, updated_at)
                        VALUES (:id, :tid, :code, :name, 'service', :doc, 1, true, :now, :now)
                        """
                    ),
                    {
                        "id": wf_id,
                        "tid": tid,
                        "code": workflow_code,
                        "name": workflow_name,
                        "doc": document_type,
                        "now": now,
                    },
                )
            for step_order, step_code, step_name, approver_type in steps:
                step_exists = conn.execute(
                    sa.text(
                        """
                        SELECT 1 FROM foundation.wf_step
                        WHERE workflow_id = :wid AND step_order = :ord
                        """
                    ),
                    {"wid": wf_id, "ord": step_order},
                ).first()
                if step_exists:
                    continue
                conn.execute(
                    sa.text(
                        """
                        INSERT INTO foundation.wf_step
                        (id, tenant_id, workflow_id, step_order, step_code, step_name,
                         approver_type, is_parallel, created_at, updated_at)
                        VALUES (:id, :tid, :wid, :ord, :code, :name, :atype, false, :now, :now)
                        """
                    ),
                    {
                        "id": str(uuid4()),
                        "tid": tid,
                        "wid": wf_id,
                        "ord": step_order,
                        "code": step_code,
                        "name": step_name,
                        "atype": approver_type,
                        "now": now,
                    },
                )


def downgrade() -> None:
    conn = op.get_bind()
    for workflow_code, _, _, _ in WORKFLOWS:
        conn.execute(
            sa.text(
                """
                DELETE FROM foundation.wf_step
                WHERE workflow_id IN (
                    SELECT id FROM foundation.wf_definition WHERE workflow_code = :code
                )
                """
            ),
            {"code": workflow_code},
        )
        conn.execute(
            sa.text("DELETE FROM foundation.wf_definition WHERE workflow_code = :code"),
            {"code": workflow_code},
        )
