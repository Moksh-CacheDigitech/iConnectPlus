"""Create org_cost_center and org_profit_center tables."""

import sys
from collections.abc import Sequence
from pathlib import Path

from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from modules.organization.models.hierarchy import OrgCostCenter, OrgProfitCenter

revision: str = "0009_org_cc_pc"
down_revision: str | None = "0008_org_department_bu_location"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()
    for table in (OrgCostCenter.__table__, OrgProfitCenter.__table__):
        table.create(bind=bind, checkfirst=True)


def downgrade() -> None:
    bind = op.get_bind()
    for table in (OrgProfitCenter.__table__, OrgCostCenter.__table__):
        table.drop(bind=bind, checkfirst=True)
