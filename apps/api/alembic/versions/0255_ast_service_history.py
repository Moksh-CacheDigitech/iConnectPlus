"""Create AstAssetServiceHistory table."""

import sys
from collections.abc import Sequence
from pathlib import Path

from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from modules.asset.models.asset_service_history import AstAssetServiceHistory  # noqa: F401

revision: str = "0255_ast_service_history"
down_revision: str | None = "0254_ast_asset_maintenance"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    AstAssetServiceHistory.__table__.create(bind=op.get_bind(), checkfirst=True)


def downgrade() -> None:
    AstAssetServiceHistory.__table__.drop(bind=op.get_bind(), checkfirst=True)
