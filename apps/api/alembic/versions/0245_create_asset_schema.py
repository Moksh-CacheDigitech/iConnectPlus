"""Create asset schema."""

from collections.abc import Sequence

from alembic import op

revision: str = "0245_create_asset_schema"
down_revision: str | None = "0244_seed_project_workflows"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS asset")


def downgrade() -> None:
    op.execute("DROP SCHEMA IF EXISTS asset CASCADE")
