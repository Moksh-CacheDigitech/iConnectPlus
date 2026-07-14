"""Create RecRecruiter table."""

import sys
from collections.abc import Sequence
from pathlib import Path

from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from modules.recruitment.models.recruiter import RecRecruiter  # noqa: F401

revision: str = "0205_rec_recruiter"
down_revision: str | None = "0204_rec_recruitment_source"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    RecRecruiter.__table__.create(bind=op.get_bind(), checkfirst=True)


def downgrade() -> None:
    RecRecruiter.__table__.drop(bind=op.get_bind(), checkfirst=True)
