"""Finance port — project costs through platform IFinancePosting."""

from decimal import Decimal
from uuid import UUID

from sqlalchemy.orm import Session

from modules.foundation.domain.value_objects import TenantContext
from modules.platform.helpers.system_journal import post_two_line_system_journal
from modules.project.models import PrjProjectCost


class ProjectFinanceAdapter:
    def __init__(self, db: Session) -> None:
        self._db = db

    def post_project_cost(
        self,
        ctx: TenantContext,
        cost: PrjProjectCost,
        *,
        amount: Decimal,
        debit_account_id: UUID,
        credit_account_id: UUID,
        fiscal_year_id: UUID | None = None,
    ) -> UUID:
        return post_two_line_system_journal(
            self._db,
            ctx,
            company_id=cost.company_id,
            branch_id=cost.branch_id,
            description=f"Project cost {cost.document_number}",
            amount=amount,
            debit_account_id=debit_account_id,
            credit_account_id=credit_account_id,
            idempotency_key=f"project.cost:{cost.id}",
            source_module="project",
            source_document_type="project_cost",
            source_document_id=cost.id,
            debit_desc="Project cost expense",
            credit_desc="Project cost offset",
            journal_date=cost.cost_date,
            fiscal_year_id=fiscal_year_id,
        )
