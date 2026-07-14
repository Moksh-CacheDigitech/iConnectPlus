"""Create PrjResourceAllocation table."""

import sys
from collections.abc import Sequence
from pathlib import Path

from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from modules.project.models.resource_allocation import PrjResourceAllocation  # noqa: F401

revision: str = "0232_prj_resource_allocation"
down_revision: str | None = "0231_prj_resource_plan"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    PrjResourceAllocation.__table__.create(bind=op.get_bind(), checkfirst=True)


def downgrade() -> None:
    PrjResourceAllocation.__table__.drop(bind=op.get_bind(), checkfirst=True)
