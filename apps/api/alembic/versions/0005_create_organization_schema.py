"""Create organization PostgreSQL schema."""

from collections.abc import Sequence

from alembic import op

revision: str = "0005_create_organization_schema"
down_revision: str | None = "0004_seed_permissions_roles"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS organization")


def downgrade() -> None:
    op.execute("DROP SCHEMA IF EXISTS organization CASCADE")
