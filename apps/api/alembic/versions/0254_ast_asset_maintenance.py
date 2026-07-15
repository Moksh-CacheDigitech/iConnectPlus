"""Create AstAssetMaintenance table."""

import sys
from collections.abc import Sequence
from pathlib import Path

from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from modules.asset.models.asset_maintenance import AstAssetMaintenance  # noqa: F401

revision: str = "0254_ast_asset_maintenance"
down_revision: str | None = "0253_ast_maint_plan"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    AstAssetMaintenance.__table__.create(bind=op.get_bind(), checkfirst=True)


def downgrade() -> None:
    AstAssetMaintenance.__table__.drop(bind=op.get_bind(), checkfirst=True)
