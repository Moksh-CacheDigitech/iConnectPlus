"""Create AstAssetMaintenancePlan table."""

import sys
from collections.abc import Sequence
from pathlib import Path

from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from modules.asset.models.asset_maintenance_plan import AstAssetMaintenancePlan  # noqa: F401

revision: str = "0253_ast_maint_plan"
down_revision: str | None = "0252_ast_warranty_insurance"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    AstAssetMaintenancePlan.__table__.create(bind=op.get_bind(), checkfirst=True)


def downgrade() -> None:
    AstAssetMaintenancePlan.__table__.drop(bind=op.get_bind(), checkfirst=True)
