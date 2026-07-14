"""Create HrSeparation table."""

import sys
from collections.abc import Sequence
from pathlib import Path

from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from modules.hr.models.separation import HrSeparation  # noqa: F401

revision: str = "0176_hr_separation"
down_revision: str | None = "0175_hr_training_attendance"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    HrSeparation.__table__.create(bind=op.get_bind(), checkfirst=True)


def downgrade() -> None:
    HrSeparation.__table__.drop(bind=op.get_bind(), checkfirst=True)
