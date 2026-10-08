"""Resolve CRM notification recipients without service-layer foreign ORM."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from modules.foundation.models.security import SecUser
from modules.master_data.models.employee import MasterEmployee


class CrmUserLookupAdapter:
    def __init__(self, db: Session) -> None:
        self._db = db

    def resolve_employee_user_id(self, tenant_id: UUID, employee_id: UUID | None) -> UUID | None:
        if employee_id is None:
            return None
        user_id = self._db.scalar(
            select(SecUser.id).where(
                SecUser.tenant_id == tenant_id,
                SecUser.employee_id == employee_id,
                SecUser.is_deleted.is_(False),
            )
        )
        if user_id is not None:
            return user_id
        emp = self._db.get(MasterEmployee, employee_id)
        return emp.user_id if emp is not None else None

    def resolve_user_manager_user_id(self, tenant_id: UUID, user_id: UUID | None) -> UUID | None:
        if user_id is None:
            return None
        user = self._db.get(SecUser, user_id)
        employee = None
        if user is not None and user.employee_id is not None:
            employee = self._db.get(MasterEmployee, user.employee_id)
        if employee is None:
            employee = self._db.scalar(
                select(MasterEmployee).where(
                    MasterEmployee.tenant_id == tenant_id,
                    MasterEmployee.user_id == user_id,
                    MasterEmployee.is_deleted.is_(False),
                )
            )
        if employee is None or employee.reporting_manager_id is None:
            return None
        return self.resolve_employee_user_id(tenant_id, employee.reporting_manager_id)
