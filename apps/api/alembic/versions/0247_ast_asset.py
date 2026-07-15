"""Create AstAsset table."""

import sys
from collections.abc import Sequence
from pathlib import Path

from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from modules.asset.models.asset import AstAsset  # noqa: F401

revision: str = "0247_ast_asset"
down_revision: str | None = "0246_ast_asset_category"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    AstAsset.__table__.create(bind=op.get_bind(), checkfirst=True)


def downgrade() -> None:
    AstAsset.__table__.drop(bind=op.get_bind(), checkfirst=True)
