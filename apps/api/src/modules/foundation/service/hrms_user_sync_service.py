"""ERP logins sourced from HRMS onboarded employees (replaces directory sync)."""

from __future__ import annotations

import secrets
from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from core.exceptions import ConflictException
from modules.foundation.domain.erp_modules import ADMIN_USER_TYPES
from modules.foundation.models.security import SecUser
from modules.foundation.repository.session_repository import SessionRepository
from modules.foundation.service.hrms_user_directory import EXITED_STATUSES, is_onboarded_employee
from modules.foundation.service.org_context_service import OrgContextService
from modules.foundation.service.user_service import UserService
from modules.master_data.published import EmployeeCommands, EmployeeRead


@dataclass(frozen=True)
class HrmsUserSyncResult:
    employee_count: int
    created: int
    linked: int
    updated: int
    deactivated: int
    skipped: int


class HrmsUserSyncService:
    """Create / link one ERP login per onboarded HRMS employee across all entities."""

    def __init__(self, db: Session) -> None:
        self._db = db
        self._users = UserService(db)
        self._org = OrgContextService(db)
        self._sessions = SessionRepository(db)
        self._employees = EmployeeCommands(db)

    @staticmethod
    def _placeholder_password() -> str:
        # Unusable until the employee resets it (forgot password / ERP admin temporary password).
        return f"Hr0!{secrets.token_urlsafe(24)}"

    def _find_user_by_email(self, tenant_id: UUID, email: str) -> SecUser | None:
        return self._db.scalar(
            select(SecUser)
            .where(SecUser.tenant_id == tenant_id, func.lower(SecUser.email) == email)
            .order_by(SecUser.is_deleted.asc(), SecUser.created_at.asc())
            .limit(1)
        )

    def _login_for(
        self,
        *,
        tenant_id: UUID,
        email: str,
        employees: list[EmployeeRead],
        actor_user_id: UUID | None,
    ) -> tuple[SecUser | None, bool]:
        """Return (user, created) for one employee email."""
        for emp in employees:
            if emp.user_id is None:
                continue
            linked = self._db.get(SecUser, emp.user_id)
            if linked is not None and not linked.is_deleted:
                return linked, False

        user = self._find_user_by_email(tenant_id, email)
        if user is not None:
            return user, False

        first = employees[0]
        name = f"{first.first_name} {first.last_name}".replace(" .", "").strip() or email
        try:
            created = self._users.create_user(
                tenant_id=tenant_id,
                email=email,
                password=self._placeholder_password(),
                display_name=name,
                user_type="employee",
                created_by=actor_user_id,
            )
        except ConflictException:
            return self._find_user_by_email(tenant_id, email), False
        return self._db.get(SecUser, created.id), True

    def sync(self, *, tenant_id: UUID, actor_user_id: UUID | None) -> HrmsUserSyncResult:
        employees = list(
            self._db.scalars(
                select(EmployeeRead).where(
                    EmployeeRead.tenant_id == tenant_id,
                    EmployeeRead.is_deleted.is_(False),
                )
            ).all()
        )
        # Stable order so an employee present in several entities always maps the same way.
        onboarded = sorted(
            (emp for emp in employees if is_onboarded_employee(emp)),
            key=lambda emp: (emp.date_of_joining, emp.employee_code, str(emp.id)),
        )
        by_email: dict[str, list[EmployeeRead]] = {}
        for emp in onboarded:
            by_email.setdefault(emp.email.strip().lower(), []).append(emp)

        created = linked = updated = skipped = 0
        valid_user_ids: set[UUID] = set()

        for email, group in by_email.items():
            user, was_created = self._login_for(
                tenant_id=tenant_id, email=email, employees=group, actor_user_id=actor_user_id
            )
            if user is None:
                skipped += 1
                continue
            created += int(was_created)
            valid_user_ids.add(user.id)

            changed = False
            if user.is_deleted:
                user.is_deleted = False
                user.deleted_at = None
                user.deleted_by = None
                changed = True
            if user.status == "inactive":
                user.status = "active"
                changed = True
            first = group[0]
            hr_name = f"{first.first_name} {first.last_name}".replace(" .", "").strip()
            if hr_name and user.display_name != hr_name:
                user.display_name = hr_name
                changed = True

            for emp in group:
                if emp.user_id is None:
                    self._employees.link_user(emp.id, user.id, updated_by=actor_user_id)
                    linked += 1
            if user.employee_id is None or user.employee_id not in {e.id for e in group}:
                user.employee_id = first.id
                changed = True
            updated += int(changed and not was_created)

            self._org.ensure_default_scope(
                tenant_id=tenant_id,
                user_id=user.id,
                company_id=first.company_id,
                branch_id=first.branch_id,
            )

        deactivated = self._deactivate_exited(
            tenant_id=tenant_id,
            employees=employees,
            keep=valid_user_ids,
            actor_user_id=actor_user_id,
        )
        self._db.flush()
        return HrmsUserSyncResult(
            employee_count=len(onboarded),
            created=created,
            linked=linked,
            updated=updated,
            deactivated=deactivated,
            skipped=skipped,
        )

    def _deactivate_exited(
        self,
        *,
        tenant_id: UUID,
        employees: list[EmployeeRead],
        keep: set[UUID],
        actor_user_id: UUID | None,
    ) -> int:
        """Exited employees lose ERP sign-in unless another onboarded record still uses the login."""
        count = 0
        for emp in employees:
            if emp.status not in EXITED_STATUSES or emp.user_id is None or emp.user_id in keep:
                continue
            user = self._db.get(SecUser, emp.user_id)
            if user is None or user.is_deleted or user.status == "inactive":
                continue
            # Preserve ERP admins managed in the database (not env allowlists).
            if user.user_type in ADMIN_USER_TYPES:
                continue
            user.status = "inactive"
            self._sessions.revoke_all_for_user(tenant_id, user.id, revoked_by=actor_user_id)
            count += 1
        return count
