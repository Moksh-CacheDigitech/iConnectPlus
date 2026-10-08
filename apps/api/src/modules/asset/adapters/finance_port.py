"""Finance port — routes asset money effects through platform IFinancePosting."""

from datetime import date
from decimal import Decimal
from uuid import UUID

from sqlalchemy.orm import Session

from modules.asset.models import AstAssetDepreciation, AstAssetDisposal, AstAssetRevaluation
from modules.foundation.domain.value_objects import TenantContext
from modules.platform.adapters.finance_adapter import FinancePostingAdapter
from modules.platform.dto import JournalLineDraft, SystemJournalDraft


class AssetFinanceAdapter:
    def __init__(self, db: Session) -> None:
        self._finance = FinancePostingAdapter(db)

    def _post_amount(
        self,
        ctx: TenantContext,
        *,
        company_id: UUID,
        branch_id: UUID | None,
        journal_date: date | None,
        description: str,
        amount: Decimal,
        debit_account_id: UUID,
        credit_account_id: UUID,
        fiscal_year_id: UUID | None,
        debit_desc: str,
        credit_desc: str,
        idempotency_key: str,
        source_document_id: UUID,
        source_document_type: str,
    ) -> UUID:
        amount = amount.quantize(Decimal("0.0001"))
        resolved_branch_id = branch_id if branch_id is not None else ctx.branch_id
        if resolved_branch_id is None:
            msg = "branch_id is required for asset finance posting"
            raise ValueError(msg)
        result = self._finance.post_system_journal(
            ctx,
            SystemJournalDraft(
                company_id=company_id,
                branch_id=resolved_branch_id,
                description=description,
                lines=(
                    JournalLineDraft(
                        account_id=debit_account_id,
                        debit_amount=amount,
                        credit_amount=Decimal("0"),
                        description=debit_desc,
                        line_number=1,
                    ),
                    JournalLineDraft(
                        account_id=credit_account_id,
                        debit_amount=Decimal("0"),
                        credit_amount=amount,
                        description=credit_desc,
                        line_number=2,
                    ),
                ),
                idempotency_key=idempotency_key,
                journal_date=journal_date or date.today(),
                fiscal_year_id=fiscal_year_id,
                source_module="asset",
                source_document_type=source_document_type,
                source_document_id=source_document_id,
            ),
        )
        return result.journal_id

    def post_depreciation(
        self,
        ctx: TenantContext,
        row: AstAssetDepreciation,
        *,
        amount: Decimal,
        debit_account_id: UUID,
        credit_account_id: UUID,
        fiscal_year_id: UUID | None = None,
    ) -> UUID:
        return self._post_amount(
            ctx,
            company_id=row.company_id,
            branch_id=getattr(row, "branch_id", None),
            journal_date=date(row.period_year, row.period_month, 1),
            description=f"Asset depreciation {row.document_number}",
            amount=amount,
            debit_account_id=debit_account_id,
            credit_account_id=credit_account_id,
            fiscal_year_id=fiscal_year_id,
            debit_desc="Depreciation expense",
            credit_desc="Accumulated depreciation",
            idempotency_key=f"asset.depreciation:{row.id}",
            source_document_id=row.id,
            source_document_type="asset_depreciation",
        )

    def post_disposal(
        self,
        ctx: TenantContext,
        row: AstAssetDisposal,
        *,
        amount: Decimal,
        debit_account_id: UUID,
        credit_account_id: UUID,
        fiscal_year_id: UUID | None = None,
    ) -> UUID:
        return self._post_amount(
            ctx,
            company_id=row.company_id,
            branch_id=row.branch_id,
            journal_date=row.disposal_date,
            description=f"Asset disposal {row.document_number}",
            amount=amount,
            debit_account_id=debit_account_id,
            credit_account_id=credit_account_id,
            fiscal_year_id=fiscal_year_id,
            debit_desc="Asset disposal debit",
            credit_desc="Asset disposal credit",
            idempotency_key=f"asset.disposal:{row.id}",
            source_document_id=row.id,
            source_document_type="asset_disposal",
        )

    def post_revaluation(
        self,
        ctx: TenantContext,
        row: AstAssetRevaluation,
        *,
        amount: Decimal,
        debit_account_id: UUID,
        credit_account_id: UUID,
        fiscal_year_id: UUID | None = None,
    ) -> UUID:
        return self._post_amount(
            ctx,
            company_id=row.company_id,
            branch_id=row.branch_id,
            journal_date=row.revaluation_date,
            description=f"Asset revaluation {row.document_number}",
            amount=amount,
            debit_account_id=debit_account_id,
            credit_account_id=credit_account_id,
            fiscal_year_id=fiscal_year_id,
            debit_desc="Asset revaluation debit",
            credit_desc="Asset revaluation credit",
            idempotency_key=f"asset.revaluation:{row.id}",
            source_document_id=row.id,
            source_document_type="asset_revaluation",
        )
