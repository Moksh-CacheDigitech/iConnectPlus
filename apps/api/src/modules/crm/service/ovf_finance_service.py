"""OVF after approval: receipts, full-payment close, execution expenses, live margin.

The OVF margin approved by Management is frozen in ``margin_at_approval_*``.
From then on the live margin keeps absorbing:

* 1% a month on the receivable still unpaid past ``payment_due_date``,
* 1% a month on stock bought for the deal that is still in the warehouse
  (``holding_cost``, pushed in by procurement),
* approved execution expenses (cables, MATAD, extra visits...),

until Finance marks the full payment received, which closes the OVF.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from core.exceptions import ConflictException, ForbiddenException, NotFoundException
from modules.crm.models import CrmOpportunity, CrmOvf, CrmOvfExpense, CrmOvfPayment
from modules.crm.repository.ovf_repository import (
    OvfExpenseRepository,
    OvfLineRepository,
    OvfPaymentRepository,
    OvfRepository,
)
from modules.crm.service.blueprint_service import log_state_history
from modules.crm.service.crm_module_admin import CrmModuleAdminService
from modules.crm.service.crm_notification_service import notify_crm_user, resolve_employee_user_id
from modules.crm.service.engines import margin_engine
from modules.foundation.domain.value_objects import TenantContext

EXPENSE_TYPES = ("operations", "purchase", "cables", "matad", "site_visit", "foc", "installation", "other")
EXPENSE_TEAMS = ("scm", "operations", "sales", "presales", "finance", "other")

# OVF states from which the live margin is tracked (post Management approval).
_LIVE_STATES = ("approved", "shared_scm", "deal_won")


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _money(value: Any) -> Decimal:
    return Decimal(str(value or 0)).quantize(Decimal("0.0001"))


class OvfFinanceService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._repo = OvfRepository(db)
        self._lines = OvfLineRepository(db)
        self._payments = OvfPaymentRepository(db)
        self._expenses = OvfExpenseRepository(db)
        self._crm_admin = CrmModuleAdminService(db)

    # -- shared -----------------------------------------------------------
    def _get(self, ctx: TenantContext, ovf_id: UUID) -> CrmOvf:
        from modules.crm.service.ovf_service import OvfService

        return OvfService(self._db).get(ctx, ovf_id)

    def _totals(self, ctx: TenantContext, ovf_id: UUID) -> dict[str, Decimal]:
        lines = self._lines.list_for_ovf(ctx, ovf_id)
        customer_net = Decimal("0")
        customer_gross = Decimal("0")
        vendor_net = Decimal("0")
        for ln in lines:
            total = Decimal(str(ln.line_total or 0))
            if ln.side == "customer_po":
                customer_net += total
                customer_gross += total * (Decimal("1") + Decimal(str(ln.gst_pct or 0)) / Decimal("100"))
            elif ln.side == "vendor":
                vendor_net += total
        return {
            "customer_net": _money(customer_net),
            "customer_gross": _money(customer_gross),
            "vendor_net": _money(vendor_net),
        }

    def _log(self, ctx: TenantContext, ovf: CrmOvf, action: str, remark: str | None) -> None:
        log_state_history(
            self._db,
            ctx,
            company_id=ovf.company_id,
            branch_id=ovf.branch_id,
            entity_type="ovf",
            entity_id=ovf.id,
            from_state=ovf.blueprint_state,
            to_state=ovf.blueprint_state,
            action=action,
            remark=remark,
        )

    def _opportunity(self, ovf: CrmOvf) -> CrmOpportunity | None:
        return self._db.get(CrmOpportunity, ovf.opportunity_id)

    def _is_finance_user(self, ctx: TenantContext) -> bool:
        if self._crm_admin.is_admin(ctx):
            return True
        from modules.crm.service.approval_step_owner_service import ApprovalStepOwnerService

        return ctx.user_id in set(ApprovalStepOwnerService(self._db).list_user_ids(ctx, "po_finance"))

    def _is_owner_or_admin(self, ctx: TenantContext, ovf: CrmOvf) -> bool:
        if self._crm_admin.is_admin(ctx):
            return True
        opp = self._opportunity(ovf)
        if opp is None:
            return False
        owner_user = resolve_employee_user_id(self._db, ctx.tenant_id, opp.owner_employee_id)
        return owner_user is not None and owner_user == ctx.user_id

    # -- live margin --------------------------------------------------------
    def _receipts(self, ctx: TenantContext, ovf: CrmOvf) -> list[tuple[date, Decimal]]:
        rows = self._payments.list_for_ovf(ctx, ovf.id)
        receipts = [(row.received_date, Decimal(str(row.amount))) for row in rows]
        if not receipts and ovf.payment_received_date is not None:
            # Legacy single-date entry: treat it as the full receivable settled that day.
            receipts = [(ovf.payment_received_date, self._totals(ctx, ovf.id)["customer_gross"])]
        return receipts

    def live_snapshot(self, ctx: TenantContext, ovf: CrmOvf, *, as_of: date | None = None) -> dict[str, Any]:
        today = as_of or date.today()
        if ovf.closed_at is not None and ovf.payment_received_date is not None:
            today = min(today, ovf.payment_received_date)
        totals = self._totals(ctx, ovf.id)
        receipts = self._receipts(ctx, ovf)
        overdue = margin_engine.compute_overdue_finance_cost(
            totals["customer_gross"], ovf.payment_due_date, receipts, today
        )
        margin = margin_engine.compute_ovf_margin(
            customer_total=totals["customer_net"],
            vendor_total=totals["vendor_net"],
            freight=ovf.freight,
            additional_charges=ovf.additional_charges,
            finance_cost_pct=ovf.finance_cost_pct,
            execution_expenses=ovf.execution_expense_total,
            early_payment_discount_pct=ovf.early_payment_discount_pct,
            overdue_finance_cost=overdue.cost,
            holding_cost=ovf.holding_cost,
        )
        received = sum((amount for d, amount in receipts if d <= today), Decimal("0"))
        return {
            "as_of": today,
            "customer_total": totals["customer_net"],
            "customer_receivable": totals["customer_gross"],
            "vendor_total": totals["vendor_net"],
            "received_amount": _money(received),
            "outstanding_amount": overdue.outstanding,
            "overdue_days": overdue.overdue_days,
            "overdue_finance_cost": overdue.cost,
            "holding_cost": _money(ovf.holding_cost),
            "execution_expense_total": _money(ovf.execution_expense_total),
            "early_payment_saving": margin.early_payment_saving,
            "planned_finance_cost": margin.finance_amount,
            "live_margin_amount": margin.margin_amount,
            "live_margin_pct": margin.margin_pct,
        }

    def refresh_live_margin(self, ctx: TenantContext, ovf_id: UUID, *, as_of: date | None = None) -> CrmOvf:
        ovf = self._get(ctx, ovf_id)
        snap = self.live_snapshot(ctx, ovf, as_of=as_of)
        ovf.overdue_finance_cost = snap["overdue_finance_cost"]
        ovf.live_margin_amount = snap["live_margin_amount"]
        ovf.live_margin_pct = snap["live_margin_pct"]
        ovf.live_margin_as_of = _utcnow()
        self._db.flush()
        return ovf

    def snapshot_margin_at_approval(self, ctx: TenantContext, ovf_id: UUID) -> None:
        ovf = self._get(ctx, ovf_id)
        ovf.margin_at_approval_amount = ovf.total_margin_amount
        ovf.margin_at_approval_pct = ovf.total_margin_pct
        self._db.flush()
        self.refresh_live_margin(ctx, ovf_id)

    def set_holding_cost(self, ctx: TenantContext, ovf_id: UUID, amount: Decimal) -> None:
        ovf = self._get(ctx, ovf_id)
        if ovf.closed_at is not None:
            return
        ovf.holding_cost = _money(amount)
        self._db.flush()
        self.refresh_live_margin(ctx, ovf_id)

    def get_live_status(self, ctx: TenantContext, ovf_id: UUID) -> dict[str, Any]:
        ovf = self._get(ctx, ovf_id)
        snap = self.live_snapshot(ctx, ovf)
        today = date.today()
        delivery_overdue = bool(
            ovf.expected_delivery_date
            and ovf.actual_delivery_date is None
            and today > ovf.expected_delivery_date
        )
        return {
            "ovf_id": ovf.id,
            "ovf_no": ovf.ovf_no,
            "margin_at_approval_amount": ovf.margin_at_approval_amount,
            "margin_at_approval_pct": ovf.margin_at_approval_pct,
            "full_payment_received": bool(ovf.full_payment_received),
            "closed_at": ovf.closed_at,
            "payment_due_date": ovf.payment_due_date,
            "payment_received_date": ovf.payment_received_date,
            "expected_delivery_date": ovf.expected_delivery_date,
            "actual_delivery_date": ovf.actual_delivery_date,
            "delivery_overdue": delivery_overdue,
            "margin_erosion": (
                _money(Decimal(str(ovf.margin_at_approval_amount)) - snap["live_margin_amount"])
                if ovf.margin_at_approval_amount is not None
                else None
            ),
            **snap,
        }

    def refresh_all_open(self, ctx: TenantContext) -> int:
        """Nightly: re-price every approved, not-yet-closed OVF of the tenant."""
        stmt = select(CrmOvf.id).where(
            CrmOvf.tenant_id == ctx.tenant_id,
            CrmOvf.is_deleted.is_(False),
            CrmOvf.closed_at.is_(None),
            CrmOvf.blueprint_state.in_(_LIVE_STATES),
        )
        count = 0
        for ovf_id in self._db.scalars(stmt).all():
            self.refresh_live_margin(ctx, ovf_id)
            count += 1
        return count

    # -- payments ---------------------------------------------------------
    def list_payments(self, ctx: TenantContext, ovf_id: UUID) -> list[CrmOvfPayment]:
        self._get(ctx, ovf_id)
        return self._payments.list_for_ovf(ctx, ovf_id)

    def add_payment(
        self,
        ctx: TenantContext,
        ovf_id: UUID,
        *,
        amount: Decimal,
        received_date: date,
        reference: str | None = None,
        remark: str | None = None,
    ) -> CrmOvfPayment:
        ovf = self._get(ctx, ovf_id)
        if not self._is_finance_user(ctx):
            raise ForbiddenException("Only Finance (customer PO finance owners) can record customer receipts")
        if ovf.closed_at is not None:
            raise ConflictException("OVF is closed - full payment was already received")
        value = _money(amount)
        if value <= 0:
            raise ConflictException("Receipt amount must be greater than zero")
        if received_date > date.today():
            raise ConflictException("Receipt date cannot be in the future")
        row = self._payments.create(
            ctx,
            company_id=ovf.company_id,
            branch_id=ovf.branch_id,
            ovf_id=ovf.id,
            amount=value,
            received_date=received_date,
            reference=(reference or "").strip() or None,
            remark=(remark or "").strip() or None,
        )
        self._log(ctx, ovf, "payment_received", f"amount={value}, date={received_date.isoformat()}")
        self.refresh_live_margin(ctx, ovf_id)
        return row

    def void_payment(self, ctx: TenantContext, payment_id: UUID) -> None:
        row = self._payments.get(ctx, payment_id)
        if row is None:
            raise NotFoundException("Payment not found")
        ovf = self._get(ctx, row.ovf_id)
        if not self._is_finance_user(ctx):
            raise ForbiddenException("Only Finance can void customer receipts")
        if ovf.closed_at is not None:
            raise ConflictException("OVF is closed - reopening is not supported")
        self._payments.soft_delete(ctx, row)
        self._log(ctx, ovf, "payment_voided", f"amount={row.amount}")
        self.refresh_live_margin(ctx, ovf.id)

    def mark_full_payment(
        self,
        ctx: TenantContext,
        ovf_id: UUID,
        *,
        received_date: date,
        remark: str | None = None,
    ) -> CrmOvf:
        ovf = self._get(ctx, ovf_id)
        if not self._is_finance_user(ctx):
            raise ForbiddenException("Only Finance can mark the full payment received")
        if ovf.closed_at is not None:
            raise ConflictException("Full payment is already recorded for this OVF")
        if ovf.blueprint_state not in _LIVE_STATES:
            raise ConflictException("Full payment can only be recorded on an approved OVF")
        if received_date > date.today():
            raise ConflictException("Payment date cannot be in the future")
        due = ovf.payment_due_date
        if due is not None and received_date > due and not (remark or ovf.payment_delay_reason):
            raise ConflictException("Payment landed after the due date - record why before closing it off")

        totals = self._totals(ctx, ovf.id)
        paid = sum((Decimal(str(r.amount)) for r in self._payments.list_for_ovf(ctx, ovf.id)), Decimal("0"))
        balance = totals["customer_gross"] - paid
        if balance > Decimal("0.5"):
            # Record the final instalment so the receipt ledger matches the receivable.
            self._payments.create(
                ctx,
                company_id=ovf.company_id,
                branch_id=ovf.branch_id,
                ovf_id=ovf.id,
                amount=_money(balance),
                received_date=received_date,
                reference=None,
                remark="Balance on full payment",
            )

        ovf.payment_received_date = received_date
        ovf.full_payment_received = True
        ovf.full_payment_marked_by = ctx.user_id
        if remark and not ovf.payment_delay_reason:
            ovf.payment_delay_reason = remark.strip()
        self._db.flush()
        self.refresh_live_margin(ctx, ovf_id, as_of=received_date)
        ovf = self._get(ctx, ovf_id)
        ovf.closed_at = _utcnow()
        self._db.flush()
        self._log(
            ctx,
            ovf,
            "full_payment_received",
            f"date={received_date.isoformat()}, final_margin={ovf.live_margin_amount}",
        )
        return ovf

    # -- execution expenses -----------------------------------------------
    def list_expenses(self, ctx: TenantContext, ovf_id: UUID) -> list[CrmOvfExpense]:
        self._get(ctx, ovf_id)
        return self._expenses.list_for_ovf(ctx, ovf_id)

    def raise_expense(
        self,
        ctx: TenantContext,
        ovf_id: UUID,
        *,
        expense_type: str,
        raised_by_team: str,
        description: str,
        amount: Decimal,
        incurred_on: date | None = None,
    ) -> CrmOvfExpense:
        ovf = self._get(ctx, ovf_id)
        if ovf.closed_at is not None:
            raise ConflictException("OVF is closed - execution expenses can no longer be added")
        if ovf.blueprint_state not in _LIVE_STATES:
            raise ConflictException("Execution expenses start once the OVF is approved")
        if expense_type not in EXPENSE_TYPES:
            raise ConflictException(f"expense_type must be one of {', '.join(EXPENSE_TYPES)}")
        if raised_by_team not in EXPENSE_TEAMS:
            raise ConflictException(f"raised_by_team must be one of {', '.join(EXPENSE_TEAMS)}")
        text = (description or "").strip()
        if not text:
            raise ConflictException("Describe what the expense was for")
        value = _money(amount)
        if value <= 0:
            raise ConflictException("Expense amount must be greater than zero")
        row = self._expenses.create(
            ctx,
            company_id=ovf.company_id,
            branch_id=ovf.branch_id,
            ovf_id=ovf.id,
            expense_type=expense_type,
            raised_by_team=raised_by_team,
            description=text,
            amount=value,
            incurred_on=incurred_on,
            status="pending",
        )
        self._log(ctx, ovf, "expense_raised", f"{expense_type} {value}: {text[:120]}")
        opp = self._opportunity(ovf)
        owner_user = resolve_employee_user_id(self._db, ctx.tenant_id, opp.owner_employee_id if opp else None)
        if owner_user is not None and owner_user != ctx.user_id:
            notify_crm_user(
                self._db,
                tenant_id=ctx.tenant_id,
                recipient_user_id=owner_user,
                event_type="crm.ovf.expense_raised",
                title=f"Approve execution expense - OVF {ovf.ovf_no}",
                body=(
                    f"{raised_by_team.upper()} added ₹{value:,.2f} ({expense_type.replace('_', ' ')}) "
                    f"against OVF {ovf.ovf_no}: {text[:160]}. It reduces the deal margin once you approve it."
                ),
                entity_type="ovf",
                entity_id=ovf.id,
                href=f"/crm/ovf/{ovf.id}",
                digest_key=f"ovf:{ovf.id}:expense:{row.id}",
                created_by=ctx.user_id,
            )
        return row

    def decide_expense(
        self,
        ctx: TenantContext,
        expense_id: UUID,
        *,
        decision: str,
        remark: str | None = None,
    ) -> CrmOvfExpense:
        row = self._expenses.get(ctx, expense_id)
        if row is None:
            raise NotFoundException("Expense not found")
        ovf = self._get(ctx, row.ovf_id)
        if decision not in ("approved", "rejected"):
            raise ConflictException("decision must be 'approved' or 'rejected'")
        if row.status != "pending":
            raise ConflictException("Expense has already been decided")
        if not self._is_owner_or_admin(ctx, ovf):
            raise ForbiddenException("Only the opportunity owner or a CRM admin can approve execution expenses")
        if decision == "rejected" and not (remark or "").strip():
            raise ConflictException("Give a reason when rejecting an expense")
        self._expenses.update(
            ctx,
            row,
            status=decision,
            decided_by=ctx.user_id,
            decided_at=_utcnow(),
            decision_remark=(remark or "").strip() or None,
        )
        self._recompute_expense_total(ctx, ovf)
        self._log(ctx, ovf, f"expense_{decision}", f"{row.expense_type} {row.amount}")
        return row

    def _recompute_expense_total(self, ctx: TenantContext, ovf: CrmOvf) -> None:
        approved = sum(
            (Decimal(str(e.amount)) for e in self._expenses.list_for_ovf(ctx, ovf.id) if e.status == "approved"),
            Decimal("0"),
        )
        ovf.execution_expense_total = _money(approved)
        self._db.flush()
        self.refresh_live_margin(ctx, ovf.id)

    # -- incentive feed -----------------------------------------------------
    def sales_performance(self, ctx: TenantContext, company_id: UUID) -> list[dict[str, Any]]:
        """Per salesperson: approved vs live margin, penalties, receivables, open deals."""
        if not self._crm_admin.is_admin(ctx):
            raise ForbiddenException("Sales performance is visible to CRM admins / management only")
        from modules.master_data.models.employee import MasterEmployee

        stmt = (
            select(CrmOvf, CrmOpportunity.owner_employee_id)
            .join(CrmOpportunity, CrmOpportunity.id == CrmOvf.opportunity_id)
            .where(
                CrmOvf.tenant_id == ctx.tenant_id,
                CrmOvf.company_id == company_id,
                CrmOvf.is_deleted.is_(False),
                CrmOvf.blueprint_state.in_(_LIVE_STATES),
            )
        )
        buckets: dict[UUID | None, dict[str, Any]] = defaultdict(
            lambda: {
                "ovf_count": 0,
                "open_ovf_count": 0,
                "margin_at_approval": Decimal("0"),
                "live_margin": Decimal("0"),
                "overdue_finance_cost": Decimal("0"),
                "holding_cost": Decimal("0"),
                "execution_expenses": Decimal("0"),
                "outstanding_receivable": Decimal("0"),
            }
        )
        for ovf, owner_id in self._db.execute(stmt).all():
            snap = self.live_snapshot(ctx, ovf)
            b = buckets[owner_id]
            b["ovf_count"] += 1
            if ovf.closed_at is None:
                b["open_ovf_count"] += 1
            b["margin_at_approval"] += Decimal(str(ovf.margin_at_approval_amount or ovf.total_margin_amount or 0))
            b["live_margin"] += snap["live_margin_amount"]
            b["overdue_finance_cost"] += snap["overdue_finance_cost"]
            b["holding_cost"] += snap["holding_cost"]
            b["execution_expenses"] += snap["execution_expense_total"]
            b["outstanding_receivable"] += snap["outstanding_amount"]

        names: dict[UUID, str] = {}
        owner_ids = [oid for oid in buckets if oid is not None]
        if owner_ids:
            for emp in self._db.scalars(select(MasterEmployee).where(MasterEmployee.id.in_(owner_ids))).all():
                names[emp.id] = f"{emp.first_name} {emp.last_name or ''}".strip()
        rows = []
        for owner_id, b in buckets.items():
            rows.append(
                {
                    "owner_employee_id": owner_id,
                    "owner_name": names.get(owner_id) if owner_id else "Unassigned",
                    **{k: (_money(v) if isinstance(v, Decimal) else v) for k, v in b.items()},
                    "margin_erosion": _money(b["margin_at_approval"] - b["live_margin"]),
                }
            )
        rows.sort(key=lambda r: r["margin_erosion"], reverse=True)
        return rows
