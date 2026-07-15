"""Create service schema."""

from collections.abc import Sequence

from alembic import op

revision: str = "0267_create_service_schema"
down_revision: str | None = "0266_seed_asset_workflows"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS service")


def downgrade() -> None:
    op.execute("DROP SCHEMA IF EXISTS service CASCADE")
