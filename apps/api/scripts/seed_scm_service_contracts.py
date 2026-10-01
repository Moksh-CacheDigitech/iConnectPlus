"""Seed demo SCM service rate contracts (Procurement → Service Contracts).

These power OVF "Service Visits" plans (projected visits × rate + consumables).

Usage (from apps/api):
  .venv\\Scripts\\python.exe -m scripts.seed_scm_service_contracts
  .venv\\Scripts\\python.exe -m scripts.seed_scm_service_contracts --company CDPL
"""

from __future__ import annotations

import argparse
import sys
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

from sqlalchemy import select

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from database.session import SessionLocal  # noqa: E402
from modules.foundation.domain.value_objects import TenantContext  # noqa: E402
from modules.foundation.models.security import SecUser  # noqa: E402
from modules.organization.models.branch import OrgBranch  # noqa: E402
from modules.organization.models.company import OrgCompany  # noqa: E402
from modules.procurement.models.service_contract import ProcServiceRateContract  # noqa: E402
from modules.procurement.service.service_contract_service import ServiceContractService  # noqa: E402

# Demo field partners / freelancers used on OVF service plans.
DEMO_CONTRACTS: list[dict] = [
    {
        "vendor_name": "FieldForce Services Pvt Ltd",
        "service_type": "site_visit",
        "region": "NCR / Delhi",
        "rate_per_visit": Decimal("3500.00"),
        "remarks": "Standard site survey & handover visit (NCR).",
    },
    {
        "vendor_name": "FieldForce Services Pvt Ltd",
        "service_type": "installation",
        "region": "NCR / Delhi",
        "rate_per_visit": Decimal("6500.00"),
        "remarks": "On-site install + basic config.",
    },
    {
        "vendor_name": "South Zone Tech Crew",
        "service_type": "installation",
        "region": "Bengaluru / Chennai",
        "rate_per_visit": Decimal("7200.00"),
        "remarks": "South India installation partner.",
    },
    {
        "vendor_name": "West Coast Field Partners",
        "service_type": "survey",
        "region": "Mumbai / Pune",
        "rate_per_visit": Decimal("4200.00"),
        "remarks": "Pre-sales / site survey.",
    },
    {
        "vendor_name": "West Coast Field Partners",
        "service_type": "maintenance",
        "region": "Mumbai / Pune",
        "rate_per_visit": Decimal("4800.00"),
        "remarks": "Post-go-live maintenance visit.",
    },
    {
        "vendor_name": "Apex Manpower Solutions",
        "service_type": "manpower",
        "region": "Pan India",
        "rate_per_visit": Decimal("2800.00"),
        "remarks": "Day-rate engineer manpower.",
    },
    {
        "vendor_name": "Iris Global Field Ops",
        "service_type": "site_visit",
        "region": "Hyderabad",
        "rate_per_visit": Decimal("3900.00"),
        "remarks": "Hyderabad metro site visits.",
    },
    {
        "vendor_name": "Iris Global Field Ops",
        "service_type": "other",
        "region": "Hyderabad",
        "rate_per_visit": Decimal("5500.00"),
        "remarks": "Specialist / ad-hoc field work.",
    },
]

PREFERRED_ACTORS = (
    "techbank@cachedigitech.com",
    "connectplus@cachedigitech.com",
    "admin@example.com",
    "admin@cachedigitech.com",
    "tenant.admin@example.com",
)


def require(row, label: str):
    if row is None:
        raise RuntimeError(f"{label} not found")
    return row


def resolve_actor(db, tenant_id) -> SecUser:
    for email in PREFERRED_ACTORS:
        user = db.scalar(
            select(SecUser).where(
                SecUser.tenant_id == tenant_id,
                SecUser.email == email,
                SecUser.is_deleted.is_(False),
            )
        )
        if user is not None:
            return user
    user = db.scalar(
        select(SecUser).where(
            SecUser.tenant_id == tenant_id,
            SecUser.is_deleted.is_(False),
        )
    )
    return require(user, "SecUser for tenant")


def ctx_for(user: SecUser, company_id, branch_id) -> TenantContext:
    return TenantContext(
        tenant_id=user.tenant_id,
        user_id=user.id,
        user_type=user.user_type or "internal",
        company_id=company_id,
        branch_id=branch_id,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed demo SCM service rate contracts.")
    parser.add_argument(
        "--company",
        default="CDPL",
        help="Org company_code (default CDPL)",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Soft-delete existing active demo contracts for this company first",
    )
    args = parser.parse_args()

    db = SessionLocal()
    try:
        org = require(
            db.scalar(
                select(OrgCompany).where(
                    OrgCompany.company_code == args.company,
                    OrgCompany.is_deleted.is_(False),
                )
            ),
            f"org company {args.company}",
        )
        branch = require(
            db.scalar(
                select(OrgBranch).where(
                    OrgBranch.company_id == org.id,
                    OrgBranch.is_deleted.is_(False),
                )
            ),
            f"branch for {args.company}",
        )
        actor = resolve_actor(db, org.tenant_id)
        ctx = ctx_for(actor, org.id, branch.id)
        svc = ServiceContractService(db)

        if args.reset:
            existing = list(
                db.scalars(
                    select(ProcServiceRateContract).where(
                        ProcServiceRateContract.company_id == org.id,
                        ProcServiceRateContract.is_deleted.is_(False),
                    )
                ).all()
            )
            for row in existing:
                row.is_deleted = True
                row.updated_by = actor.id
            db.flush()
            print(f"Soft-deleted {len(existing)} existing contract(s)")

        today = date.today()
        valid_from = today - timedelta(days=30)
        valid_to = today + timedelta(days=365)

        created: list[str] = []
        skipped = 0
        for spec in DEMO_CONTRACTS:
            already = db.scalar(
                select(ProcServiceRateContract).where(
                    ProcServiceRateContract.company_id == org.id,
                    ProcServiceRateContract.vendor_name == spec["vendor_name"],
                    ProcServiceRateContract.service_type == spec["service_type"],
                    ProcServiceRateContract.region == spec["region"],
                    ProcServiceRateContract.is_deleted.is_(False),
                )
            )
            if already is not None:
                skipped += 1
                continue
            row = svc.create_contract(
                ctx,
                vendor_name=spec["vendor_name"],
                service_type=spec["service_type"],
                rate_per_visit=spec["rate_per_visit"],
                valid_from=valid_from,
                valid_to=valid_to,
                region=spec["region"],
                remarks=spec["remarks"],
            )
            created.append(
                f"{row.contract_code} | {row.vendor_name} | {row.service_type} | INR {row.rate_per_visit}"
            )

        db.commit()

        active = svc.list_contracts(ctx, active_only=True)
        print(f"Company: {org.company_code} ({org.company_name})")
        print(f"Actor:   {actor.email}")
        print(f"Created: {len(created)}  Skipped(existing): {skipped}")
        for line in created:
            print(f"  + {line}")
        print(f"Active rate contracts now: {len(active)}")
        print("UI: Procurement → Service Contracts  (OVF Service Visits can pick these)")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
