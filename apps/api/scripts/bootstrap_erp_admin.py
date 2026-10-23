"""Create or repair an ERP admin login (email + password, SUPER_ADMIN, linked employee).

Sets ``sec_user.user_type = super_admin`` in the database. ERP admin status is
stored only in the DB — not in environment variables.

Usage (from apps/api):
  python -m scripts.bootstrap_erp_admin --email you@company.com --password 'Secret@123'
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from sqlalchemy import func, select

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from database.session import SessionLocal  # noqa: E402
from modules.foundation.models.security import SecRole, SecTenant, SecUser, SecUserRole  # noqa: E402
from modules.foundation.service.org_context_service import OrgContextService  # noqa: E402
from modules.foundation.service.user_service import UserService  # noqa: E402
from modules.master_data.published import EmployeeCommands, EmployeeRead  # noqa: E402
from security.field_crypto import pii_lookup  # noqa: E402
from security.password import PasswordHasher  # noqa: E402


def _tenant_for(db, email: str) -> SecTenant:
    user = db.scalar(select(SecUser).where(func.lower(SecUser.email) == email))
    if user is not None:
        return db.get(SecTenant, user.tenant_id)
    tenant = db.scalar(
        select(SecTenant).where(SecTenant.tenant_code == "BOOTSTRAP", SecTenant.is_deleted.is_(False))
    )
    if tenant is None:
        raise SystemExit("BOOTSTRAP tenant not found - run the base seed first")
    return tenant


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--email", required=True)
    parser.add_argument("--password", required=True)
    parser.add_argument("--name", default="")
    args = parser.parse_args()

    email = args.email.strip().lower()

    db = SessionLocal()
    try:
        tenant = _tenant_for(db, email)
        users = UserService(db)
        user = db.scalar(
            select(SecUser)
            .where(SecUser.tenant_id == tenant.id, func.lower(SecUser.email) == email)
            .order_by(SecUser.is_deleted.asc())
            .limit(1)
        )
        if user is None:
            created = users.create_user(
                tenant_id=tenant.id,
                email=email,
                password=args.password,
                display_name=args.name.strip() or email.split("@")[0].title(),
                user_type="super_admin",
            )
            user = db.get(SecUser, created.id)
            print(f"Created login {email}")

        user.password_hash = PasswordHasher.hash_password(args.password)
        user.is_deleted = False
        user.deleted_at = None
        user.deleted_by = None
        user.status = "active"
        user.user_type = "super_admin"
        user.failed_login_count = 0
        user.locked_until = None
        user.must_change_password = False
        if args.name.strip():
            user.display_name = args.name.strip()

        role = db.scalar(
            select(SecRole).where(
                SecRole.tenant_id == tenant.id,
                SecRole.role_code == "SUPER_ADMIN",
                SecRole.is_deleted.is_(False),
            )
        )
        if role is not None and db.scalar(
            select(SecUserRole.id).where(SecUserRole.user_id == user.id, SecUserRole.role_id == role.id)
        ) is None:
            users.assign_role(tenant_id=tenant.id, user_id=user.id, role_id=role.id, assigned_by=None)

        employee = db.scalar(
            select(EmployeeRead).where(
                EmployeeRead.tenant_id == tenant.id,
                EmployeeRead.is_deleted.is_(False),
                EmployeeRead.email_lookup == pii_lookup(email),
            )
        )
        if employee is not None:
            if employee.user_id != user.id:
                EmployeeCommands(db).link_user(employee.id, user.id)
            user.employee_id = employee.id
            OrgContextService(db).ensure_default_scope(
                tenant_id=tenant.id,
                user_id=user.id,
                company_id=employee.company_id,
                branch_id=employee.branch_id,
            )
        else:
            company, branch = OrgContextService(db).get_tenant_primary_org(tenant.id)
            if company is not None:
                OrgContextService(db).ensure_default_scope(
                    tenant_id=tenant.id,
                    user_id=user.id,
                    company_id=company.id,
                    branch_id=branch.id if branch else None,
                )

        db.commit()
        linked = f", employee {employee.employee_code}" if employee is not None else ""
        print(f"ERP admin ready: {email} (tenant {tenant.tenant_code}{linked})")
    finally:
        db.close()


if __name__ == "__main__":
    main()
