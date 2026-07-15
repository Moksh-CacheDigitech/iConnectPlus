"""Create AstAssetComponent table."""

import sys
from collections.abc import Sequence
from pathlib import Path

from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from modules.asset.models.asset_component import AstAssetComponent  # noqa: F401

revision: str = "0248_ast_asset_component"
down_revision: str | None = "0247_ast_asset"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    AstAssetComponent.__table__.create(bind=op.get_bind(), checkfirst=True)


def downgrade() -> None:
    AstAssetComponent.__table__.drop(bind=op.get_bind(), checkfirst=True)
