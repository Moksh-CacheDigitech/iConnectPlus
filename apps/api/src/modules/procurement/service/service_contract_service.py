"""Service POs on per-visit rate contracts.

A rate contract fixes what a freelancer / field partner charges per visit.
A service plan prices an OVF's projected visits (plus consumables) off that
contract and, while the OVF is still a draft, adds the cost as vendor lines so
the margin is right from day one. Visits are logged as they happen; any visit
beyond the projection is raised on the OVF as an execution expense for the
sales owner to approve.
"""

from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from core.exceptions import AppException, ConflictException, ForbiddenException, NotFoundException
from modules.foundation.domain.value_objects import TenantContext
from modules.procurement.adapters.crm_adapter import ProcurementCrmAdapter
from modules.procurement.models.service_contract import ProcServicePlan, ProcServiceRateContract, ProcServiceVisit
from modules.procurement.service.procurement_scope_validator import ProcurementScopeValidator

SERVICE_TYPES = ("site_visit", "installation", "survey", "maintenance", "manpower", "other")
_MONEY = Decimal("0.0001")


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _money(value: Any) -> Decimal:
    return Decimal(str(value or 0)).quantize(_MONEY)


def plan_total(visits: int, rate: Decimal, consumables: Decimal) -> Decimal:
    return (Decimal(visits) * Decimal(str(rate)) + Decimal(str(consumables or 0))).quantize(_MONEY)


class ServiceContractService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._scope = ProcurementScopeValidator(db)
        self._crm = ProcurementCrmAdapter(db)

    def _company(self, ctx: TenantContext, company_id: UUID | None = None) -> UUID:
        cid = self._scope.resolve_company_id(ctx, company_id)
        if cid is None:
            raise ForbiddenException("Company context required")
        return cid

    def _branch(self, ctx: TenantContext, company_id: UUID) -> UUID:
        if ctx.branch_id is not None:
            return ctx.branch_id
        from modules.organization.repository.branch_repository import BranchRepository

        branches = BranchRepository(self._db).list_branches(ctx, company_id=company_id)
        if not branches:
            raise ConflictException("No branch is configured for this company")
        return branches[0].id

    # -- contracts ------------------------------------------------------------
    def list_contracts(self, ctx: TenantContext, *, active_only: bool = False) -> list[ProcServiceRateContract]:
        cid = self._company(ctx)
        stmt = select(ProcServiceRateContract).where(
            ProcServiceRateContract.tenant_id == ctx.tenant_id,
            ProcServiceRateContract.company_id == cid,
            ProcServiceRateContract.is_deleted.is_(False),
        )
        rows = list(self._db.scalars(stmt.order_by(ProcServiceRateContract.created_at.desc())).all())
        if active_only:
            today = date.today()
            rows = [r for r in rows if self._is_valid(r, today)]
        return rows

    @staticmethod
    def _is_valid(row: ProcServiceRateContract, on: date) -> bool:
        return row.status == "active" and row.valid_from <= on and (row.valid_to is None or row.valid_to >= on)

    def _get_contract(self, ctx: TenantContext, contract_id: UUID) -> ProcServiceRateContract:
        row = self._db.get(ProcServiceRateContract, contract_id)
        if row is None or row.is_deleted or row.tenant_id != ctx.tenant_id:
            raise NotFoundException("Rate contract not found")
        self._scope.validate_company_access(ctx, row.company_id)
        return row

    def _next_code(self, company_id: UUID) -> str:
        prefix = f"SRC-{date.today().year}-"
        count = self._db.scalar(
            select(func.count())
            .select_from(ProcServiceRateContract)
            .where(
                ProcServiceRateContract.company_id == company_id,
                ProcServiceRateContract.contract_code.like(f"{prefix}%"),
            )
        )
        return f"{prefix}{int(count or 0) + 1}"

    def create_contract(
        self,
        ctx: TenantContext,
        *,
        vendor_name: str,
        service_type: str,
        rate_per_visit: Decimal,
        valid_from: date,
        valid_to: date | None = None,
        region: str | None = None,
        vendor_id: UUID | None = None,
        remarks: str | None = None,
    ) -> ProcServiceRateContract:
        cid = self._company(ctx)
        if service_type not in SERVICE_TYPES:
            raise ConflictException(f"service_type must be one of {', '.join(SERVICE_TYPES)}")
        if _money(rate_per_visit) <= 0:
            raise ConflictException("Rate per visit must be greater than zero")
        if valid_to is not None and valid_to < valid_from:
            raise ConflictException("Contract end date is before its start date")
        name = (vendor_name or "").strip()
        if not name:
            raise ConflictException("Vendor / freelancer name is required")
        row = ProcServiceRateContract(
            contract_code=self._next_code(cid),
            vendor_id=vendor_id,
            vendor_name=name[:255],
            service_type=service_type,
            region=(region or "").strip() or None,
            rate_per_visit=_money(rate_per_visit),
            valid_from=valid_from,
            valid_to=valid_to,
            status="active",
            remarks=(remarks or "").strip() or None,
            tenant_id=ctx.tenant_id,
            company_id=cid,
            branch_id=self._branch(ctx, cid),
            created_by=ctx.user_id,
            updated_by=ctx.user_id,
        )
        self._db.add(row)
        self._db.flush()
        return row

    def update_contract(self, ctx: TenantContext, contract_id: UUID, **fields: Any) -> ProcServiceRateContract:
        row = self._get_contract(ctx, contract_id)
        if "service_type" in fields and fields["service_type"] not in SERVICE_TYPES:
            raise ConflictException(f"service_type must be one of {', '.join(SERVICE_TYPES)}")
        if "status" in fields and fields["status"] not in ("active", "inactive"):
            raise ConflictException("status must be 'active' or 'inactive'")
        if "rate_per_visit" in fields:
            if _money(fields["rate_per_visit"]) <= 0:
                raise ConflictException("Rate per visit must be greater than zero")
            fields["rate_per_visit"] = _money(fields["rate_per_visit"])
        for key, value in fields.items():
            setattr(row, key, value)
        if row.valid_to is not None and row.valid_to < row.valid_from:
            raise ConflictException("Contract end date is before its start date")
        row.updated_by = ctx.user_id
        row.updated_at = _now()
        row.version = int(row.version or 1) + 1
        self._db.flush()
        return row

    # -- plans ------------------------------------------------------------------
    def list_plans(self, ctx: TenantContext, ovf_id: UUID) -> list[dict[str, Any]]:
        stmt = select(ProcServicePlan).where(
            ProcServicePlan.tenant_id == ctx.tenant_id,
            ProcServicePlan.ovf_id == ovf_id,
            ProcServicePlan.is_deleted.is_(False),
        )
        return [self._plan_dto(ctx, row) for row in self._db.scalars(stmt.order_by(ProcServicePlan.created_at)).all()]

    def _plan_dto(self, ctx: TenantContext, plan: ProcServicePlan) -> dict[str, Any]:
        contract = self._db.get(ProcServiceRateContract, plan.rate_contract_id)
        extra = max(plan.visits_done - plan.projected_visits, 0)
        return {
            "id": plan.id,
            "ovf_id": plan.ovf_id,
            "rate_contract_id": plan.rate_contract_id,
            "contract_code": contract.contract_code if contract else None,
            "vendor_name": contract.vendor_name if contract else None,
            "service_type": contract.service_type if contract else None,
            "description": plan.description,
            "projected_visits": plan.projected_visits,
            "visits_done": plan.visits_done,
            "visits_remaining": max(plan.projected_visits - plan.visits_done, 0),
            "extra_visits": extra,
            "rate_per_visit": plan.rate_per_visit,
            "consumables_amount": plan.consumables_amount,
            "planned_total": plan.planned_total,
            "actual_cost": plan_total(plan.visits_done, plan.rate_per_visit, plan.consumables_amount),
            "added_to_ovf": plan.added_to_ovf,
            "status": plan.status,
        }

    def create_plan(
        self,
        ctx: TenantContext,
        *,
        ovf_id: UUID,
        rate_contract_id: UUID,
        projected_visits: int,
        consumables_amount: Decimal = Decimal("0"),
        description: str | None = None,
        add_to_ovf: bool = True,
    ) -> dict[str, Any]:
        ovf = self._crm.get_ovf_brief(ctx, ovf_id)
        if ovf is None:
            raise NotFoundException("OVF not found")
        contract = self._get_contract(ctx, rate_contract_id)
        if not self._is_valid(contract, date.today()):
            raise ConflictException(f"Rate contract {contract.contract_code} is not active today")
        if projected_visits <= 0:
            raise ConflictException("Projected visits must be greater than zero")
        consumables = _money(consumables_amount)
        if consumables < 0:
            raise ConflictException("Consumables cannot be negative")
        plan = ProcServicePlan(
            ovf_id=ovf_id,
            rate_contract_id=contract.id,
            description=(description or "").strip() or None,
            projected_visits=int(projected_visits),
            rate_per_visit=contract.rate_per_visit,
            consumables_amount=consumables,
            planned_total=plan_total(projected_visits, contract.rate_per_visit, consumables),
            tenant_id=ctx.tenant_id,
            company_id=contract.company_id,
            branch_id=contract.branch_id,
            created_by=ctx.user_id,
            updated_by=ctx.user_id,
        )
        self._db.add(plan)
        self._db.flush()
        if add_to_ovf and ovf["editable"]:
            label = f"{contract.service_type.replace('_', ' ').title()} visits - {contract.vendor_name}"
            self._crm.add_ovf_vendor_line(
                ctx,
                ovf_id,
                product_name=label[:255],
                description=f"{projected_visits} visits x Rs {contract.rate_per_visit:,.2f} ({contract.contract_code})",
                distributor_name=contract.vendor_name,
                qty=Decimal(projected_visits),
                unit_price=contract.rate_per_visit,
                gst_pct=Decimal("18"),
            )
            if consumables > 0:
                self._crm.add_ovf_vendor_line(
                    ctx,
                    ovf_id,
                    product_name="Service consumables (LAN cable, connectors, survey)",
                    description=f"For {contract.contract_code}",
                    distributor_name=contract.vendor_name,
                    qty=Decimal("1"),
                    unit_price=consumables,
                    gst_pct=Decimal("18"),
                )
            plan.added_to_ovf = True
            self._db.flush()
        return self._plan_dto(ctx, plan)

    def _get_plan(self, ctx: TenantContext, plan_id: UUID) -> ProcServicePlan:
        plan = self._db.get(ProcServicePlan, plan_id)
        if plan is None or plan.is_deleted or plan.tenant_id != ctx.tenant_id:
            raise NotFoundException("Service plan not found")
        self._scope.validate_company_access(ctx, plan.company_id)
        return plan

    def close_plan(self, ctx: TenantContext, plan_id: UUID) -> dict[str, Any]:
        plan = self._get_plan(ctx, plan_id)
        plan.status = "closed"
        plan.updated_by = ctx.user_id
        plan.updated_at = _now()
        self._db.flush()
        return self._plan_dto(ctx, plan)

    # -- visits -----------------------------------------------------------------
    def list_visits(self, ctx: TenantContext, plan_id: UUID) -> list[ProcServiceVisit]:
        self._get_plan(ctx, plan_id)
        stmt = select(ProcServiceVisit).where(
            ProcServiceVisit.plan_id == plan_id, ProcServiceVisit.is_deleted.is_(False)
        )
        return list(self._db.scalars(stmt.order_by(ProcServiceVisit.visit_date.desc())).all())

    def log_visit(
        self,
        ctx: TenantContext,
        plan_id: UUID,
        *,
        visit_date: date,
        site: str | None = None,
        engineer_name: str | None = None,
        remarks: str | None = None,
    ) -> ProcServiceVisit:
        plan = self._get_plan(ctx, plan_id)
        if plan.status != "open":
            raise ConflictException("This service plan is closed")
        if visit_date > date.today():
            raise ConflictException("Visit date cannot be in the future")
        plan.visits_done += 1
        beyond = plan.visits_done > plan.projected_visits
        visit = ProcServiceVisit(
            plan_id=plan.id,
            visit_date=visit_date,
            site=(site or "").strip() or None,
            engineer_name=(engineer_name or "").strip() or None,
            remarks=(remarks or "").strip() or None,
            status="done",
            beyond_projection=beyond,
            tenant_id=plan.tenant_id,
            company_id=plan.company_id,
            branch_id=plan.branch_id,
            created_by=ctx.user_id,
            updated_by=ctx.user_id,
        )
        self._db.add(visit)
        self._db.flush()
        if beyond:
            contract = self._db.get(ProcServiceRateContract, plan.rate_contract_id)
            try:
                with self._db.begin_nested():
                    expense = self._crm.raise_ovf_expense(
                        ctx,
                        plan.ovf_id,
                        expense_type="site_visit",
                        raised_by_team="operations",
                        description=(
                            f"Visit {plan.visits_done} of {plan.projected_visits} planned "
                            f"({contract.contract_code if contract else 'rate contract'})"
                            f"{f' at {visit.site}' if visit.site else ''} on {visit_date.isoformat()}"
                        ),
                        amount=plan.rate_per_visit,
                        incurred_on=visit_date,
                    )
                visit.expense_id = expense.id
            except AppException:
                # OVF not yet approved / already closed - the visit stays flagged for review.
                pass
            self._db.flush()
        return visit

    def cancel_visit(self, ctx: TenantContext, visit_id: UUID) -> ProcServiceVisit:
        visit = self._db.get(ProcServiceVisit, visit_id)
        if visit is None or visit.is_deleted or visit.tenant_id != ctx.tenant_id:
            raise NotFoundException("Visit not found")
        plan = self._get_plan(ctx, visit.plan_id)
        if visit.status == "cancelled":
            return visit
        if visit.expense_id is not None:
            raise ConflictException("An expense was raised for this visit - reject it on the OVF instead")
        visit.status = "cancelled"
        plan.visits_done = max(plan.visits_done - 1, 0)
        visit.updated_by = ctx.user_id
        visit.updated_at = _now()
        self._db.flush()
        return visit
