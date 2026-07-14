"""Create MfgMaterialReturn table."""

import sys
from collections.abc import Sequence
from pathlib import Path

from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from modules.manufacturing.models.material_return import MfgMaterialReturn  # noqa: F401

revision: str = "0106_mfg_material_return"
down_revision: str | None = "0105_mfg_material_issue_line"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    MfgMaterialReturn.__table__.create(bind=op.get_bind(), checkfirst=True)


def downgrade() -> None:
    MfgMaterialReturn.__table__.drop(bind=op.get_bind(), checkfirst=True)
