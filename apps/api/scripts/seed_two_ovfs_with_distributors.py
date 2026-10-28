"""Create 2 CRM OVFs shared to procurement SCM with distributor on every vendor line.

Uses the same sales-chain builder as seed_many_scm_ovfs, then sets
crm_ovf_line.distributor_name from the CRM distributor dropdown options
before approve + share_to_scm.
"""

from __future__ import annotations

import sys
from pathlib import Path

from sqlalchemy import select

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from database.session import SessionLocal  # noqa: E402
from modules.crm.models import CrmLeadSource, CrmPipeline  # noqa: E402
from modules.crm.models.ovf import CrmOvf  # noqa: E402
from modules.crm.service.ovf_service import OvfService  # noqa: E402
from modules.foundation.models.security import SecUser  # noqa: E402
from modules.master_data.models.employee import MasterEmployee  # noqa: E402
from modules.organization.models.branch import OrgBranch  # noqa: E402
from modules.organization.models.company import OrgCompany  # noqa: E402
from scripts.seed_many_scm_ovfs import (  # noqa: E402
    DEMO_DEALS,
    ctx_for,
    create_shared_ovf,
    ensure_products,
    pick_user,
    require,
)

# Match apps/web lead-distributor dropdown (normalized names).
DISTRIBUTOR_BY_INDEX = (
    "Ingram Micro",
    "Redington",
)


def main() -> None:
    db = SessionLocal()
    try:
        org = require(
            db.scalar(
                select(OrgCompany).where(
                    OrgCompany.company_code == "CDPL",
                    OrgCompany.is_deleted.is_(False),
                )
            ),
            "org company CDPL",
        )
        branch = require(
            db.scalar(
                select(OrgBranch).where(
                    OrgBranch.company_id == org.id,
                    OrgBranch.branch_code == "HQ",
                    OrgBranch.is_deleted.is_(False),
                )
            ),
            "HQ branch",
        )
        sales_user = db.scalar(
            select(SecUser).where(
                SecUser.email == "techbank@cachedigitech.com",
                SecUser.is_deleted.is_(False),
            )
        ) or pick_user(db, "sales.user@example.com")
        employee = require(
            db.scalar(
                select(MasterEmployee).where(
                    MasterEmployee.company_id == org.id,
                    MasterEmployee.user_id == sales_user.id,
                    MasterEmployee.is_deleted.is_(False),
                )
            )
            or db.scalar(
                select(MasterEmployee).where(
                    MasterEmployee.company_id == org.id,
                    MasterEmployee.is_deleted.is_(False),
                )
            ),
            "master employee",
        )
        lead_source = require(
            db.scalar(
                select(CrmLeadSource).where(
                    CrmLeadSource.company_id == org.id,
                    CrmLeadSource.is_deleted.is_(False),
                )
            ),
            "lead source",
        )
        pipeline = require(
            db.scalar(
                select(CrmPipeline).where(
                    CrmPipeline.company_id == org.id,
                    CrmPipeline.is_deleted.is_(False),
                )
            ),
            "pipeline",
        )
        sales_ctx = ctx_for(sales_user, org.id, branch.id)
        products = ensure_products(db, sales_ctx, org.id)
        ovfs = OvfService(db)

        # Continue numbering past existing SCM-01..05 seeds.
        start_index = 6
        created: list[tuple[str, str, str]] = []

        for offset in range(2):
            index = start_index + offset
            deal = dict(DEMO_DEALS[offset % len(DEMO_DEALS)])
            distributor = DISTRIBUTOR_BY_INDEX[offset]
            deal["distributor"] = distributor
            print(f"[{offset + 1}/2] {deal['account']} distributor={distributor} ...", flush=True)

            # Build chain up to OVF create by temporarily wrapping share.
            # create_shared_ovf always shares; patch line distributors after create
            # by intercepting: run create path manually via monkeypatch of share_to_scm.
            original_share = OvfService.share_to_scm

            def share_with_distributors(self, ctx, ovf_id, _dist=distributor, _orig=original_share):
                for line in self._lines.list_for_ovf(ctx, ovf_id):
                    if line.side != "vendor":
                        continue
                    self._lines.update(ctx, line.id, distributor_name=_dist)
                    print(f"    vendor line '{line.product_name}' -> {_dist}")
                return _orig(self, ctx, ovf_id)

            OvfService.share_to_scm = share_with_distributors  # type: ignore[method-assign]
            try:
                ovf_no, state = create_shared_ovf(
                    db=db,
                    index=index,
                    deal=deal,
                    org=org,
                    branch=branch,
                    sales_ctx=sales_ctx,
                    sales_user=sales_user,
                    employee=employee,
                    lead_source=lead_source,
                    pipeline=pipeline,
                    products=products,
                )
            finally:
                OvfService.share_to_scm = original_share  # type: ignore[method-assign]

            db.commit()
            created.append((ovf_no, state, distributor))
            print(f"    -> {ovf_no} ({state})")

        print()
        print("Created:")
        for ovf_no, state, dist in created:
            print(f"  {ovf_no}  {state}  distributor={dist}")
            row = db.scalar(select(CrmOvf).where(CrmOvf.ovf_no == ovf_no, CrmOvf.is_deleted.is_(False)))
            if row:
                for line in ovfs._lines.list_for_ovf(sales_ctx, row.id):
                    if line.side == "vendor":
                        print(f"      [{line.side}] {line.product_name}: {line.distributor_name}")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
