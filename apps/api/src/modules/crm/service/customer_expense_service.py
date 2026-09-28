"""Customer expense ledger: FOC replacements, urgent cables, free visits.

Every favour done for a customer is booked against the account so the next
deal can recover it; open entries are surfaced on that customer's
opportunities and adjusted against an OVF once recovered.
"""

from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import ConflictException, NotFoundException
from modules.crm.models import CrmCustomerExpense
from modules.crm.repository.customer_ledger_repository import CustomerExpenseRepository
from modules.crm.service.company_service import CompanyService
from modules.crm.service.crm_module_admin import CrmModuleAdminService
from modules.foundation.domain.value_objects import TenantContext

EXPENSE_CATEGORIES = ("foc_material", "replacement", "site_visit", "service", "cables", "other")


class CustomerExpenseService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._repo = CustomerExpenseRepository(db)
        self._companies = CompanyService(db)
        self._crm_admin = CrmModuleAdminService(db)

    def list(self, ctx: TenantContext, company_account_id: UUID) -> list[CrmCustomerExpense]:
        self._companies.get(ctx, company_account_id)
        return self._repo.list_for_account(ctx, company_account_id)

    def summary(self, ctx: TenantContext, company_account_id: UUID) -> dict[str, Any]:
        rows = self.list(ctx, company_account_id)
        open_rows = [r for r in rows if r.status == "open" and r.adjust_in_future]
        return {
            "company_account_id": company_account_id,
            "open_count": len(open_rows),
            "open_amount": sum((Decimal(str(r.amount)) for r in open_rows), Decimal("0")),
            "adjusted_amount": sum(
                (Decimal(str(r.amount)) for r in rows if r.status == "adjusted"), Decimal("0")
            ),
            "written_off_amount": sum(
                (Decimal(str(r.amount)) for r in rows if r.status == "written_off"), Decimal("0")
            ),
            "open_items": open_rows,
        }

    def summary_for_opportunity(self, ctx: TenantContext, opportunity_id: UUID) -> dict[str, Any]:
        """Older expenses already incurred on this customer, to recover in the deal."""
        from modules.crm.service.blueprint_service import OpportunityBlueprintService

        opp = OpportunityBlueprintService(self._db).get(ctx, opportunity_id)
        if opp.company_account_id is None:
            return {
                "company_account_id": None,
                "open_count": 0,
                "open_amount": Decimal("0"),
                "adjusted_amount": Decimal("0"),
                "written_off_amount": Decimal("0"),
                "open_items": [],
            }
        return self.summary(ctx, opp.company_account_id)

    def create(
        self,
        ctx: TenantContext,
        company_account_id: UUID,
        *,
        expense_date: date,
        category: str,
        description: str,
        amount: Decimal,
        opportunity_id: UUID | None = None,
        approved_by_name: str | None = None,
        approval_reference: str | None = None,
        adjust_in_future: bool = True,
    ) -> CrmCustomerExpense:
        account = self._companies.get(ctx, company_account_id)
        if category not in EXPENSE_CATEGORIES:
            raise ConflictException(f"category must be one of {', '.join(EXPENSE_CATEGORIES)}")
        text = (description or "").strip()
        if not text:
            raise ConflictException("Describe what was given to the customer")
        value = Decimal(str(amount)).quantize(Decimal("0.0001"))
        if value <= 0:
            raise ConflictException("Amount must be greater than zero")
        if expense_date > date.today():
            raise ConflictException("Expense date cannot be in the future")
        if not (approved_by_name or "").strip():
            raise ConflictException("Record who approved this expense")
        if opportunity_id is not None:
            from modules.crm.service.blueprint_service import OpportunityBlueprintService

            opp = OpportunityBlueprintService(self._db).get(ctx, opportunity_id)
            if opp.company_account_id != company_account_id:
                raise ConflictException("Opportunity belongs to a different customer account")
        return self._repo.create(
            ctx,
            company_id=account.company_id,
            branch_id=account.branch_id,
            company_account_id=company_account_id,
            opportunity_id=opportunity_id,
            expense_date=expense_date,
            category=category,
            description=text,
            amount=value,
            approved_by_name=approved_by_name.strip(),
            approval_reference=(approval_reference or "").strip() or None,
            adjust_in_future=bool(adjust_in_future),
            status="open",
        )

    def _get(self, ctx: TenantContext, expense_id: UUID) -> CrmCustomerExpense:
        row = self._repo.get(ctx, expense_id)
        if row is None:
            raise NotFoundException("Customer expense not found")
        self._companies.get(ctx, row.company_account_id)
        return row

    def mark_adjusted(
        self,
        ctx: TenantContext,
        expense_id: UUID,
        *,
        ovf_id: UUID,
        remark: str | None = None,
    ) -> CrmCustomerExpense:
        row = self._get(ctx, expense_id)
        if row.status != "open":
            raise ConflictException("Only open expenses can be adjusted")
        from modules.crm.service.ovf_service import OvfService

        ovf = OvfService(self._db).get(ctx, ovf_id)
        if ovf.company_account_id != row.company_account_id:
            raise ConflictException("OVF belongs to a different customer account")
        return self._repo.update(
            ctx,
            row,
            status="adjusted",
            adjusted_ovf_id=ovf.id,
            adjusted_at=datetime.now(timezone.utc),
            adjustment_remark=(remark or "").strip() or None,
        )

    def write_off(self, ctx: TenantContext, expense_id: UUID, *, remark: str) -> CrmCustomerExpense:
        self._crm_admin.ensure_admin(ctx)
        row = self._get(ctx, expense_id)
        if row.status != "open":
            raise ConflictException("Only open expenses can be written off")
        text = (remark or "").strip()
        if not text:
            raise ConflictException("Give a reason for writing the expense off")
        return self._repo.update(
            ctx,
            row,
            status="written_off",
            adjusted_at=datetime.now(timezone.utc),
            adjustment_remark=text,
        )
