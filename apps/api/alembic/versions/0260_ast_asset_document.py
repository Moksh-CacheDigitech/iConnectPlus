"""Create AstAssetDocument table."""

import sys
from collections.abc import Sequence
from pathlib import Path

from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from modules.asset.models.asset_document import AstAssetDocument  # noqa: F401

revision: str = "0260_ast_asset_document"
down_revision: str | None = "0259_ast_asset_audit"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    AstAssetDocument.__table__.create(bind=op.get_bind(), checkfirst=True)


def downgrade() -> None:
    AstAssetDocument.__table__.drop(bind=op.get_bind(), checkfirst=True)
