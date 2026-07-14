"""Create PrjProjectPhase table."""

import sys
from collections.abc import Sequence
from pathlib import Path

from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from modules.project.models.project_phase import PrjProjectPhase  # noqa: F401

revision: str = "0225_prj_project_phase"
down_revision: str | None = "0224_prj_project"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    PrjProjectPhase.__table__.create(bind=op.get_bind(), checkfirst=True)


def downgrade() -> None:
    PrjProjectPhase.__table__.drop(bind=op.get_bind(), checkfirst=True)
