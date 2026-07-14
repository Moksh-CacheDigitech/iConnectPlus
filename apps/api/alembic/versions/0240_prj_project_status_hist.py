"""Create PrjProjectStatusHistory table."""

import sys
from collections.abc import Sequence
from pathlib import Path

from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from modules.project.models.project_status_history import PrjProjectStatusHistory  # noqa: F401

revision: str = "0240_prj_project_status_hist"
down_revision: str | None = "0239_prj_project_comment"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    PrjProjectStatusHistory.__table__.create(bind=op.get_bind(), checkfirst=True)


def downgrade() -> None:
    PrjProjectStatusHistory.__table__.drop(bind=op.get_bind(), checkfirst=True)
