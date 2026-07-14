"""Create PrjResourcePlan table."""

import sys
from collections.abc import Sequence
from pathlib import Path

from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from modules.project.models.resource_plan import PrjResourcePlan  # noqa: F401

revision: str = "0231_prj_resource_plan"
down_revision: str | None = "0230_prj_timesheet_entry"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    PrjResourcePlan.__table__.create(bind=op.get_bind(), checkfirst=True)


def downgrade() -> None:
    PrjResourcePlan.__table__.drop(bind=op.get_bind(), checkfirst=True)
