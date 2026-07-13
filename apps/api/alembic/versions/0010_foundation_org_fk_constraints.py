"""Add Foundation FK constraints to organization tables."""

from collections.abc import Sequence

from alembic import op

revision: str = "0010_foundation_org_fks"
down_revision: str | None = "0009_org_cc_pc"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE foundation.wf_instance
        ADD CONSTRAINT fk_wf_instance_company
        FOREIGN KEY (company_id) REFERENCES organization.org_company(id)
        ON DELETE RESTRICT ON UPDATE CASCADE
        """
    )
    op.execute(
        """
        ALTER TABLE config.cfg_setting
        ADD CONSTRAINT fk_cfg_setting_company
        FOREIGN KEY (company_id) REFERENCES organization.org_company(id)
        ON DELETE RESTRICT ON UPDATE CASCADE
        """
    )
    op.execute(
        """
        ALTER TABLE config.cfg_setting
        ADD CONSTRAINT fk_cfg_setting_branch
        FOREIGN KEY (branch_id) REFERENCES organization.org_branch(id)
        ON DELETE RESTRICT ON UPDATE CASCADE
        """
    )


def downgrade() -> None:
    op.execute(
        "ALTER TABLE config.cfg_setting DROP CONSTRAINT IF EXISTS fk_cfg_setting_branch"
    )
    op.execute(
        "ALTER TABLE config.cfg_setting DROP CONSTRAINT IF EXISTS fk_cfg_setting_company"
    )
    op.execute(
        "ALTER TABLE foundation.wf_instance DROP CONSTRAINT IF EXISTS fk_wf_instance_company"
    )
