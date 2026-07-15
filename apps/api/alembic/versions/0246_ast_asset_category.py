"""Create AstAssetCategory table."""

import sys
from collections.abc import Sequence
from pathlib import Path

from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from modules.asset.models.asset_category import AstAssetCategory  # noqa: F401

revision: str = "0246_ast_asset_category"
down_revision: str | None = "0245_create_asset_schema"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    AstAssetCategory.__table__.create(bind=op.get_bind(), checkfirst=True)


def downgrade() -> None:
    AstAssetCategory.__table__.drop(bind=op.get_bind(), checkfirst=True)
