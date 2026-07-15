"""Create integration schema."""

from collections.abc import Sequence

from alembic import op

revision: str = "0377_create_integration_schema"
down_revision: str | None = "0376_seed_analytics_workflows"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS integration")


def downgrade() -> None:
    op.execute("DROP SCHEMA IF EXISTS integration CASCADE")
