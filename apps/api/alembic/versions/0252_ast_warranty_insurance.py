"""Create asset policy tables."""

import sys
from collections.abc import Sequence
from pathlib import Path

from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from modules.asset.models.asset_warranty import AstAssetWarranty  # noqa: F401
from modules.asset.models.asset_insurance import AstAssetInsurance  # noqa: F401

revision: str = "0252_ast_warranty_insurance"
down_revision: str | None = "0251_ast_asset_location"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    AstAssetWarranty.__table__.create(bind=op.get_bind(), checkfirst=True)
    AstAssetInsurance.__table__.create(bind=op.get_bind(), checkfirst=True)


def downgrade() -> None:
    AstAssetInsurance.__table__.drop(bind=op.get_bind(), checkfirst=True)
    AstAssetWarranty.__table__.drop(bind=op.get_bind(), checkfirst=True)
