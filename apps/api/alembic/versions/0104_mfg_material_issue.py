"""Create MfgMaterialIssue table."""

import sys
from collections.abc import Sequence
from pathlib import Path

from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from modules.manufacturing.models.material_issue import MfgMaterialIssue  # noqa: F401

revision: str = "0104_mfg_material_issue"
down_revision: str | None = "0103_mfg_production_operation"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    MfgMaterialIssue.__table__.create(bind=op.get_bind(), checkfirst=True)


def downgrade() -> None:
    MfgMaterialIssue.__table__.drop(bind=op.get_bind(), checkfirst=True)
