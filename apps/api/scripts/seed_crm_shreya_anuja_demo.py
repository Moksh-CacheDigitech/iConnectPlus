"""Seed CRM demo deals + tasks for Shreya and Anuja (Cache Digitech CRM users).

Creates per user:
  - 2 sales accounts (crm_company)
  - 2 won opportunities (deal won)
  - 1 open opportunity (in pipeline)
  - 3 tasks assigned to them

Idempotent on opportunity_code / task_code / account customer_name markers.

Usage (from apps/api, or via docker):
  python -m scripts.seed_crm_shreya_anuja_demo
"""

from __future__ import annotations

import sys
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path
from uuid import UUID, uuid4

from sqlalchemy import select

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from database.session import SessionLocal  # noqa: E402
from modules.crm.domain.enums import OpportunityStatus  # noqa: E402
from modules.crm.models import CrmCompany, CrmOpportunity, CrmPipeline, CrmTask  # noqa: E402
from modules.crm.service.activity_service import TaskService  # noqa: E402
from modules.crm.service.company_service import CompanyService  # noqa: E402
from modules.crm.service.opportunity_service import OpportunityService  # noqa: E402
from modules.foundation.domain.value_objects import TenantContext  # noqa: E402
from modules.foundation.models.security import SecUser  # noqa: E402
from modules.master_data.models.employee import MasterEmployee  # noqa: E402

TARGET_EMAILS = (
    "shreya@cachedigitech.com",
    "anuja@cachedigitech.com",
)

# (code_suffix, opportunity_name, amount, days_ago_won)
WON_DEALS: list[tuple[str, str, Decimal, int]] = [
    ("WON-01", "Enterprise Firewall Refresh", Decimal("1850000.00"), 18),
    ("WON-02", "Microsoft 365 + Security Bundle", Decimal("920000.00"), 7),
]

# (code_suffix, opportunity_name, amount, stage)
OPEN_DEALS: list[tuple[str, str, Decimal, str]] = [
    ("OPEN-01", "Hybrid Cloud Migration Assessment", Decimal("1450000.00"), "proposal"),
]

# (code_suffix, title, priority, days_due, status)
TASKS: list[tuple[str, str, str, int, str]] = [
    ("TSK-01", "Send commercial proposal pack", "high", 2, "pending"),
    ("TSK-02", "Schedule technical discovery call", "medium", 4, "in_progress"),
    ("TSK-03", "Collect customer PO soft copy", "highest", 1, "pending"),
]

# (marker, customer_name, industry, city)
ACCOUNTS: list[tuple[str, str, str, str]] = [
    ("ACC-A", "Northwind Digital Pvt Ltd", "IT Services", "Noida"),
    ("ACC-B", "Summit Retail Technologies", "Retail", "Gurugram"),
]


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def ctx_for(user: SecUser, company_id: UUID, branch_id: UUID) -> TenantContext:
    return TenantContext(
        tenant_id=user.tenant_id,
        user_id=user.id,
        user_type=user.user_type or "employee",
        company_id=company_id,
        branch_id=branch_id,
        scoped_company_ids=(company_id,),
    )


def load_targets(db) -> list[tuple[SecUser, MasterEmployee]]:
    rows: list[tuple[SecUser, MasterEmployee]] = []
    for email in TARGET_EMAILS:
        user = db.scalar(
            select(SecUser).where(
                SecUser.email == email,
                SecUser.is_deleted.is_(False),
            )
        )
        if user is None:
            raise RuntimeError(f"User not found: {email}")
        emp = db.scalar(
            select(MasterEmployee).where(
                MasterEmployee.user_id == user.id,
                MasterEmployee.is_deleted.is_(False),
            )
        )
        if emp is None:
            raise RuntimeError(f"Employee row missing for {email}")
        rows.append((user, emp))
    return rows


def ensure_pipeline(db, tenant_id: UUID, company_id: UUID, actor_id: UUID) -> CrmPipeline:
    pipeline = db.scalar(
        select(CrmPipeline).where(
            CrmPipeline.tenant_id == tenant_id,
            CrmPipeline.company_id == company_id,
            CrmPipeline.pipeline_code == "STD",
            CrmPipeline.is_deleted.is_(False),
        )
    )
    if pipeline:
        return pipeline
    pipeline = CrmPipeline(
        id=uuid4(),
        tenant_id=tenant_id,
        company_id=company_id,
        pipeline_code="STD",
        pipeline_name="Standard Pipeline",
        stages_json=[
            {"code": "qualification", "name": "Qualification"},
            {"code": "discovery", "name": "Discovery"},
            {"code": "proposal", "name": "Proposal"},
            {"code": "negotiation", "name": "Negotiation"},
            {"code": "won", "name": "Won"},
            {"code": "lost", "name": "Lost"},
        ],
        status="active",
        created_by=actor_id,
        updated_by=actor_id,
    )
    db.add(pipeline)
    db.flush()
    return pipeline


def code_prefix(employee_code: str) -> str:
    return f"DEMO-{employee_code}"


def ensure_accounts(
    db,
    ctx: TenantContext,
    *,
    branch_id: UUID,
    employee: MasterEmployee,
) -> list[CrmCompany]:
    svc = CompanyService(db)
    out: list[CrmCompany] = []
    prefix = code_prefix(employee.employee_code)
    for marker, name, industry, city in ACCOUNTS:
        existing = db.scalar(
            select(CrmCompany).where(
                CrmCompany.company_id == ctx.company_id,
                CrmCompany.customer_name == name,
                CrmCompany.created_by == ctx.user_id,
                CrmCompany.is_deleted.is_(False),
            )
        )
        if existing:
            out.append(existing)
            continue
        row = svc.create(
            ctx,
            branch_id=branch_id,
            customer_name=name,
            industry=industry,
            source="demo",
            account_type="Customer",
            account_owner_id=employee.id,
            first_name=employee.first_name,
            last_name=employee.last_name,
            customer_email=f"procurement@{marker.lower()}.demo.local",
            phone="+91-98765-00000",
            billing_street="Plot 12, Sector Demo",
            billing_city=city,
            billing_state="Uttar Pradesh" if city == "Noida" else "Haryana",
            billing_code="201301" if city == "Noida" else "122001",
            billing_country="India",
            description=f"{prefix} demo account ({marker})",
            rating="Hot",
        )
        out.append(row)
    return out


def ensure_won_deals(
    db,
    ctx: TenantContext,
    *,
    branch_id: UUID,
    employee: MasterEmployee,
    pipeline: CrmPipeline,
    accounts: list[CrmCompany],
) -> list[CrmOpportunity]:
    svc = OpportunityService(db)
    out: list[CrmOpportunity] = []
    prefix = code_prefix(employee.employee_code)
    for idx, (suffix, name, amount, days_ago) in enumerate(WON_DEALS):
        code = f"{prefix}-{suffix}"
        existing = db.scalar(
            select(CrmOpportunity).where(
                CrmOpportunity.company_id == ctx.company_id,
                CrmOpportunity.opportunity_code == code,
                CrmOpportunity.is_deleted.is_(False),
            )
        )
        account = accounts[idx % len(accounts)]
        if existing:
            out.append(existing)
            continue
        won_at = utcnow() - timedelta(days=days_ago)
        row = svc.create(
            ctx,
            branch_id=branch_id,
            opportunity_code=code,
            opportunity_name=name,
            document_date=date.today() - timedelta(days=days_ago + 20),
            pipeline_id=pipeline.id,
            owner_employee_id=employee.id,
            company_account_id=account.id,
            expected_revenue=amount,
            probability_percent=Decimal("100"),
            expected_close_date=date.today() - timedelta(days=days_ago),
            current_stage="won",
            status=OpportunityStatus.WON.value,
            deal_won_amount=amount,
            forecast_amount=amount,
            notes=f"Demo deal won for {employee.first_name}",
            has_hardware=True,
            has_software=idx == 1,
            has_services=True,
            project_title=name,
        )
        # create() may overwrite status/stage defaults; force won fields.
        svc._repo.update(
            ctx,
            row.id,
            status=OpportunityStatus.WON.value,
            current_stage="won",
            probability_percent=Decimal("100"),
            forecast_amount=amount,
            deal_won_amount=amount,
            won_at=won_at,
            expected_revenue=amount,
        )
        out.append(svc.get(ctx, row.id))
    return out


def ensure_open_deals(
    db,
    ctx: TenantContext,
    *,
    branch_id: UUID,
    employee: MasterEmployee,
    pipeline: CrmPipeline,
    accounts: list[CrmCompany],
) -> list[CrmOpportunity]:
    svc = OpportunityService(db)
    out: list[CrmOpportunity] = []
    prefix = code_prefix(employee.employee_code)
    for idx, (suffix, name, amount, stage) in enumerate(OPEN_DEALS):
        code = f"{prefix}-{suffix}"
        existing = db.scalar(
            select(CrmOpportunity).where(
                CrmOpportunity.company_id == ctx.company_id,
                CrmOpportunity.opportunity_code == code,
                CrmOpportunity.is_deleted.is_(False),
            )
        )
        if existing:
            out.append(existing)
            continue
        account = accounts[idx % len(accounts)]
        row = svc.create(
            ctx,
            branch_id=branch_id,
            opportunity_code=code,
            opportunity_name=name,
            document_date=date.today() - timedelta(days=5),
            pipeline_id=pipeline.id,
            owner_employee_id=employee.id,
            company_account_id=account.id,
            expected_revenue=amount,
            probability_percent=Decimal("60"),
            expected_close_date=date.today() + timedelta(days=21),
            current_stage=stage,
            status=OpportunityStatus.OPEN.value,
            notes=f"Open pipeline demo for {employee.first_name}",
            has_software=True,
            has_services=True,
            project_title=name,
        )
        out.append(row)
    return out


def ensure_tasks(
    db,
    ctx: TenantContext,
    *,
    branch_id: UUID,
    employee: MasterEmployee,
    opportunities: list[CrmOpportunity],
    accounts: list[CrmCompany],
) -> list[CrmTask]:
    svc = TaskService(db)
    out: list[CrmTask] = []
    for idx, (_suffix, title, priority, days_due, status) in enumerate(TASKS):
        demo_title = f"[{employee.employee_code}] {title}"
        existing = db.scalar(
            select(CrmTask).where(
                CrmTask.company_id == ctx.company_id,
                CrmTask.title == demo_title,
                CrmTask.created_by == ctx.user_id,
                CrmTask.is_deleted.is_(False),
            )
        )
        if existing:
            out.append(existing)
            continue
        opp = opportunities[idx % len(opportunities)] if opportunities else None
        account = accounts[idx % len(accounts)]
        row = svc.create(
            ctx,
            branch_id=branch_id,
            title=demo_title,
            description=f"Demo CRM task for {employee.first_name} {employee.last_name}",
            account_name=account.customer_name,
            opportunity_name=opp.opportunity_name if opp else None,
            opportunity_id=opp.id if opp else None,
            owner_employee_id=employee.id,
            assigned_to_employee_id=employee.id,
            due_at=utcnow() + timedelta(days=days_due),
            reminder_date=date.today() + timedelta(days=max(days_due - 1, 0)),
            priority=priority,
            status=status,
            email=employee.email,
        )
        out.append(row)
    return out


def main() -> None:
    db = SessionLocal()
    try:
        targets = load_targets(db)
        created_summary: list[str] = []
        for user, employee in targets:
            company_id = employee.company_id
            branch_id = employee.branch_id
            if company_id is None or branch_id is None:
                raise RuntimeError(f"{user.email} employee missing company/branch")
            pipeline = ensure_pipeline(db, user.tenant_id, company_id, user.id)
            ctx = ctx_for(user, company_id, branch_id)
            accounts = ensure_accounts(db, ctx, branch_id=branch_id, employee=employee)
            won = ensure_won_deals(
                db,
                ctx,
                branch_id=branch_id,
                employee=employee,
                pipeline=pipeline,
                accounts=accounts,
            )
            open_deals = ensure_open_deals(
                db,
                ctx,
                branch_id=branch_id,
                employee=employee,
                pipeline=pipeline,
                accounts=accounts,
            )
            tasks = ensure_tasks(
                db,
                ctx,
                branch_id=branch_id,
                employee=employee,
                opportunities=[*won, *open_deals],
                accounts=accounts,
            )
            created_summary.append(
                f"{user.email}: accounts={len(accounts)} won={len(won)} "
                f"open={len(open_deals)} tasks={len(tasks)}"
            )
        db.commit()
        print("CRM demo seed complete for Shreya & Anuja")
        for line in created_summary:
            print(" ", line)
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
