"""Create IntDataTransformation table."""

import sys
from collections.abc import Sequence
from pathlib import Path

from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from modules.integration.models.data_transformation import IntDataTransformation  # noqa: F401

revision: str = "0389_int_data_transformation"
down_revision: str | None = "0388_int_data_mapping"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    IntDataTransformation.__table__.create(bind=op.get_bind(), checkfirst=True)


def downgrade() -> None:
    IntDataTransformation.__table__.drop(bind=op.get_bind(), checkfirst=True)
