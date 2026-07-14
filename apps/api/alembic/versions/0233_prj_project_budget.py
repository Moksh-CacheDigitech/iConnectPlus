"""Create PrjProjectBudget table."""

import sys
from collections.abc import Sequence
from pathlib import Path

from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from modules.project.models.project_budget import PrjProjectBudget  # noqa: F401

revision: str = "0233_prj_project_budget"
down_revision: str | None = "0232_prj_resource_allocation"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    PrjProjectBudget.__table__.create(bind=op.get_bind(), checkfirst=True)


def downgrade() -> None:
    PrjProjectBudget.__table__.drop(bind=op.get_bind(), checkfirst=True)
