"""Add cross-module employee FK constraints."""

from collections.abc import Sequence

from alembic import op

revision: str = "0020_cross_module_employee_fk"
down_revision: str | None = "0019_master_warehouse_asset"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE foundation.sec_user
        ADD CONSTRAINT fk_sec_user_employee
        FOREIGN KEY (employee_id) REFERENCES master.master_employee(id)
        ON DELETE RESTRICT ON UPDATE CASCADE
        """
    )
    op.execute(
        """
        ALTER TABLE organization.org_department
        ADD CONSTRAINT fk_org_department_head_employee
        FOREIGN KEY (head_employee_id) REFERENCES master.master_employee(id)
        ON DELETE RESTRICT ON UPDATE CASCADE
        """
    )
    op.execute(
        """
        ALTER TABLE organization.org_business_unit
        ADD CONSTRAINT fk_org_business_unit_manager_employee
        FOREIGN KEY (manager_employee_id) REFERENCES master.master_employee(id)
        ON DELETE RESTRICT ON UPDATE CASCADE
        """
    )


def downgrade() -> None:
    op.execute(
        "ALTER TABLE organization.org_business_unit "
        "DROP CONSTRAINT IF EXISTS fk_org_business_unit_manager_employee"
    )
    op.execute(
        "ALTER TABLE organization.org_department "
        "DROP CONSTRAINT IF EXISTS fk_org_department_head_employee"
    )
    op.execute(
        "ALTER TABLE foundation.sec_user DROP CONSTRAINT IF EXISTS fk_sec_user_employee"
    )
