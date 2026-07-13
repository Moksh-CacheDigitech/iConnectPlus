"""Create org_department, org_business_unit, org_location tables."""

import sys
from collections.abc import Sequence
from pathlib import Path

from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from modules.organization.models.hierarchy import OrgBusinessUnit, OrgDepartment, OrgLocation

revision: str = "0008_org_department_bu_location"
down_revision: str | None = "0007_org_branch"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()
    for table in (OrgDepartment.__table__, OrgBusinessUnit.__table__, OrgLocation.__table__):
        table.create(bind=bind, checkfirst=True)


def downgrade() -> None:
    bind = op.get_bind()
    for table in (OrgLocation.__table__, OrgBusinessUnit.__table__, OrgDepartment.__table__):
        table.drop(bind=bind, checkfirst=True)
