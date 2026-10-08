"""Manufacturing finance posting via platform IFinancePosting."""

from decimal import Decimal
from uuid import UUID

from sqlalchemy.orm import Session

from modules.foundation.domain.value_objects import TenantContext
from modules.manufacturing.models.material_issue import MfgMaterialIssue
from modules.manufacturing.models.material_return import MfgMaterialReturn
from modules.manufacturing.models.production_receipt import MfgProductionReceipt
from modules.manufacturing.models.scrap import MfgScrap
from modules.manufacturing.models.variance import MfgVariance
from modules.platform.compat.audit_facade import PlatformAuditFacade
from modules.platform.helpers.system_journal import post_two_line_system_journal


class ManufacturingPostingService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._audit = PlatformAuditFacade(db)

    def _post_pair(
        self,
        ctx: TenantContext,
        *,
        company_id: UUID,
        branch_id: UUID,
        journal_date,
        description: str,
        fiscal_year_id: UUID | None,
        debit_account_id: UUID,
        credit_account_id: UUID,
        amount: Decimal,
        debit_desc: str,
        credit_desc: str,
        idempotency_key: str,
        source_document_id: UUID,
        source_document_type: str,
    ) -> UUID:
        if amount.quantize(Decimal("0.0001")) <= 0:
            raise ValueError("Posting amount must be positive")
        return post_two_line_system_journal(
            self._db,
            ctx,
            company_id=company_id,
            branch_id=branch_id,
            description=description,
            amount=amount,
            debit_account_id=debit_account_id,
            credit_account_id=credit_account_id,
            idempotency_key=idempotency_key,
            source_module="manufacturing",
            source_document_type=source_document_type,
            source_document_id=source_document_id,
            debit_desc=debit_desc,
            credit_desc=credit_desc,
            journal_date=journal_date,
            fiscal_year_id=fiscal_year_id,
        )

    def post_material_issue(
        self,
        ctx: TenantContext,
        issue: MfgMaterialIssue,
        *,
        amount: Decimal,
        wip_account_id: UUID,
        inventory_account_id: UUID,
        fiscal_year_id: UUID | None = None,
    ) -> UUID:
        jid = self._post_pair(
            ctx,
            company_id=issue.company_id,
            branch_id=issue.branch_id,
            journal_date=issue.document_date,
            description=f"MFG material issue {issue.document_number}",
            fiscal_year_id=fiscal_year_id,
            debit_account_id=wip_account_id,
            credit_account_id=inventory_account_id,
            amount=amount,
            debit_desc="WIP material",
            credit_desc="Inventory issue",
            idempotency_key=f"mfg.material_issue:{issue.id}",
            source_document_id=issue.id,
            source_document_type="mfg_material_issue",
        )
        issue.finance_journal_id = jid
        self._audit.log_entity_change(
            tenant_id=ctx.tenant_id,
            entity_name="mfg_material_issue",
            entity_id=issue.id,
            operation="finance_post",
            performed_by=ctx.user_id,
            new_value={"journal_id": str(jid)},
        )
        return jid

    def post_material_return(
        self,
        ctx: TenantContext,
        ret: MfgMaterialReturn,
        *,
        amount: Decimal,
        wip_account_id: UUID,
        inventory_account_id: UUID,
        fiscal_year_id: UUID | None = None,
    ) -> UUID:
        jid = self._post_pair(
            ctx,
            company_id=ret.company_id,
            branch_id=ret.branch_id,
            journal_date=ret.document_date,
            description=f"MFG material return {ret.document_number}",
            fiscal_year_id=fiscal_year_id,
            debit_account_id=inventory_account_id,
            credit_account_id=wip_account_id,
            amount=amount,
            debit_desc="Inventory return",
            credit_desc="WIP relief",
            idempotency_key=f"mfg.material_return:{ret.id}",
            source_document_id=ret.id,
            source_document_type="mfg_material_return",
        )
        ret.finance_journal_id = jid
        return jid

    def post_production_receipt(
        self,
        ctx: TenantContext,
        receipt: MfgProductionReceipt,
        *,
        amount: Decimal,
        fg_account_id: UUID,
        wip_account_id: UUID,
        fiscal_year_id: UUID | None = None,
    ) -> UUID:
        jid = self._post_pair(
            ctx,
            company_id=receipt.company_id,
            branch_id=receipt.branch_id,
            journal_date=receipt.document_date,
            description=f"MFG production receipt {receipt.document_number}",
            fiscal_year_id=fiscal_year_id,
            debit_account_id=fg_account_id,
            credit_account_id=wip_account_id,
            amount=amount,
            debit_desc="FG inventory",
            credit_desc="WIP relief",
            idempotency_key=f"mfg.production_receipt:{receipt.id}",
            source_document_id=receipt.id,
            source_document_type="mfg_production_receipt",
        )
        receipt.finance_journal_id = jid
        return jid

    def post_scrap(
        self,
        ctx: TenantContext,
        scrap: MfgScrap,
        *,
        amount: Decimal,
        scrap_expense_account_id: UUID,
        wip_account_id: UUID,
        fiscal_year_id: UUID | None = None,
    ) -> UUID:
        jid = self._post_pair(
            ctx,
            company_id=scrap.company_id,
            branch_id=scrap.branch_id,
            journal_date=scrap.document_date,
            description=f"MFG scrap {scrap.document_number}",
            fiscal_year_id=fiscal_year_id,
            debit_account_id=scrap_expense_account_id,
            credit_account_id=wip_account_id,
            amount=amount,
            debit_desc="Scrap expense",
            credit_desc="WIP / inventory credit",
            idempotency_key=f"mfg.scrap:{scrap.id}",
            source_document_id=scrap.id,
            source_document_type="mfg_scrap",
        )
        scrap.finance_journal_id = jid
        return jid

    def post_variance(
        self,
        ctx: TenantContext,
        variance: MfgVariance,
        *,
        amount: Decimal,
        variance_account_id: UUID,
        wip_account_id: UUID,
        fiscal_year_id: UUID | None = None,
        journal_date=None,
    ) -> UUID:
        amt = abs(amount)
        if amount >= 0:
            debit, credit = variance_account_id, wip_account_id
        else:
            debit, credit = wip_account_id, variance_account_id
        jid = self._post_pair(
            ctx,
            company_id=variance.company_id,
            branch_id=variance.branch_id,
            journal_date=journal_date,
            description=f"MFG variance {variance.variance_type}",
            fiscal_year_id=fiscal_year_id,
            debit_account_id=debit,
            credit_account_id=credit,
            amount=amt,
            debit_desc="Variance",
            credit_desc="WIP offset",
            idempotency_key=f"mfg.variance:{variance.id}",
            source_document_id=variance.id,
            source_document_type="mfg_variance",
        )
        variance.finance_journal_id = jid
        return jid
