"""Create ecommerce schema."""

from collections.abc import Sequence

from alembic import op

revision: str = "0399_create_ecommerce_schema"
down_revision: str | None = "0398_seed_integration_workflows"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS ecommerce")


def downgrade() -> None:
    op.execute("DROP SCHEMA IF EXISTS ecommerce CASCADE")
