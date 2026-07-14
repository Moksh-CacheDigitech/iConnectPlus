"""Create RecReferenceCheck table."""

import sys
from collections.abc import Sequence
from pathlib import Path

from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from modules.recruitment.models.reference_check import RecReferenceCheck  # noqa: F401

revision: str = "0215_rec_reference_check"
down_revision: str | None = "0214_rec_background_verif"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    RecReferenceCheck.__table__.create(bind=op.get_bind(), checkfirst=True)


def downgrade() -> None:
    RecReferenceCheck.__table__.drop(bind=op.get_bind(), checkfirst=True)
