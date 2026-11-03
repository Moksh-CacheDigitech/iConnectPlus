"""Placeholder for CRM quote revision payload migration already applied on shared DB.

The live revision file is not in this checkout; this stub keeps Alembic's graph loadable
so later revisions (e.g. drop marketing) can run. No-op on upgrade/downgrade.
"""

from collections.abc import Sequence

revision: str = "0651_crm_quote_revision_payload"
down_revision: str | Sequence[str] | None = "0649_crm_lead_presales_call_gate"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
