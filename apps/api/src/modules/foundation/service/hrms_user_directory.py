"""Which ERP logins are backed by an onboarded HRMS employee."""

from __future__ import annotations

import re
from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from core.config import settings
from modules.master_data.published import EmployeeRead

# Employee lifecycle states that count as onboarded (draft / onboarding are not yet hired).
ONBOARDED_STATUSES = frozenset({"active", "probation", "on_leave", "notice_period"})
EXITED_STATUSES = frozenset({"resigned", "terminated", "ex_employee"})


@dataclass(frozen=True)
class HrmsLink:
    employee_code: str
    valid: bool


def is_valid_employee_code(code: str | None) -> bool:
    value = (code or "").strip()
    if not value:
        return False
    return re.fullmatch(settings.hrms_employee_code_pattern, value) is not None


def is_onboarded_employee(employee: EmployeeRead) -> bool:
    return (
        not employee.is_deleted
        and employee.status in ONBOARDED_STATUSES
        and is_valid_employee_code(employee.employee_code)
        and bool((employee.email or "").strip())
    )


class HrmsUserDirectory:
    def __init__(self, db: Session) -> None:
        self._db = db

    def links_by_user(self, tenant_id: UUID) -> dict[UUID, HrmsLink]:
        rows = self._db.scalars(
            select(EmployeeRead).where(
                EmployeeRead.tenant_id == tenant_id,
                EmployeeRead.is_deleted.is_(False),
                EmployeeRead.user_id.is_not(None),
            )
        ).all()
        out: dict[UUID, HrmsLink] = {}
        for emp in rows:
            if emp.user_id is None:
                continue
            valid = is_onboarded_employee(emp)
            current = out.get(emp.user_id)
            if current is None or (valid and not current.valid):
                out[emp.user_id] = HrmsLink(employee_code=emp.employee_code, valid=valid)
        return out

    def valid_user_ids(self, tenant_id: UUID) -> set[UUID]:
        return {uid for uid, link in self.links_by_user(tenant_id).items() if link.valid}

    def is_valid_user(self, tenant_id: UUID, user_id: UUID) -> bool:
        return user_id in self.valid_user_ids(tenant_id)
