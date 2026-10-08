"""Finance port — GRC charges through platform IFinancePosting."""

from decimal import Decimal
from uuid import UUID

from sqlalchemy.orm import Session

from modules.finance.repository.tax_repository import TaxRepository
from modules.foundation.domain.value_objects import TenantContext
from modules.grc.models import GrcCorrectiveAction, GrcIncident
from modules.platform.helpers.system_journal import post_two_line_system_journal


class GrcFinanceAdapter:
    def __init__(self, db: Session) -> None:
        self._db = db

    def tax_register_line_count(self, ctx: TenantContext, company_id: UUID) -> int:
        return TaxRepository(self._db).count_register_lines(ctx, company_id)

    def post_incident_cost(
        self,
        ctx: TenantContext,
        row: GrcIncident,
        *,
        amount: Decimal,
        debit_account_id: UUID,
        credit_account_id: UUID,
        fiscal_year_id: UUID | None = None,
    ) -> UUID:
        return self._post_cost(
            ctx,
            company_id=row.company_id,
            branch_id=row.branch_id,
            document_label=f"Incident {row.incident_number}",
            amount=amount,
            debit_account_id=debit_account_id,
            credit_account_id=credit_account_id,
            fiscal_year_id=fiscal_year_id,
            idempotency_key=f"grc.incident:{row.id}",
            source_document_id=row.id,
            source_document_type="grc_incident",
        )

    def post_capa_cost(
        self,
        ctx: TenantContext,
        row: GrcCorrectiveAction,
        *,
        amount: Decimal,
        debit_account_id: UUID,
        credit_account_id: UUID,
        fiscal_year_id: UUID | None = None,
    ) -> UUID:
        return self._post_cost(
            ctx,
            company_id=row.company_id,
            branch_id=row.branch_id,
            document_label=f"CAPA {row.capa_number}",
            amount=amount,
            debit_account_id=debit_account_id,
            credit_account_id=credit_account_id,
            fiscal_year_id=fiscal_year_id,
            idempotency_key=f"grc.capa:{row.id}",
            source_document_id=row.id,
            source_document_type="grc_capa",
        )

    def _post_cost(
        self,
        ctx: TenantContext,
        *,
        company_id: UUID,
        branch_id: UUID | None,
        document_label: str,
        amount: Decimal,
        debit_account_id: UUID,
        credit_account_id: UUID,
        fiscal_year_id: UUID | None,
        idempotency_key: str,
        source_document_id: UUID,
        source_document_type: str,
    ) -> UUID:
        resolved_branch_id = branch_id if branch_id is not None else ctx.branch_id
        if resolved_branch_id is None:
            raise ValueError("branch_id is required for GRC finance posting")
        return post_two_line_system_journal(
            self._db,
            ctx,
            company_id=company_id,
            branch_id=resolved_branch_id,
            description=f"GRC charge {document_label}",
            amount=amount,
            debit_account_id=debit_account_id,
            credit_account_id=credit_account_id,
            idempotency_key=idempotency_key,
            source_module="grc",
            source_document_type=source_document_type,
            source_document_id=source_document_id,
            debit_desc="GRC charge debit",
            credit_desc="GRC charge credit",
            fiscal_year_id=fiscal_year_id,
        )
