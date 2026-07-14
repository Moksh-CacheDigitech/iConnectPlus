"""Create RecJobPosting table."""

import sys
from collections.abc import Sequence
from pathlib import Path

from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from modules.recruitment.models.job_posting import RecJobPosting  # noqa: F401

revision: str = "0203_rec_job_posting"
down_revision: str | None = "0202_rec_job_requisition"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    RecJobPosting.__table__.create(bind=op.get_bind(), checkfirst=True)


def downgrade() -> None:
    RecJobPosting.__table__.drop(bind=op.get_bind(), checkfirst=True)
