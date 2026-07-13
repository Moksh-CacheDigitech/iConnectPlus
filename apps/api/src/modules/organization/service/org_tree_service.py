"""Organization tree service."""

from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import NotFoundException
from modules.foundation.domain.value_objects import TenantContext
from modules.organization.repository.branch_repository import BranchRepository
from modules.organization.repository.company_repository import CompanyRepository
from modules.organization.repository.hierarchy_repository import DepartmentRepository
from modules.organization.service.org_scope_validator import OrgScopeValidator


class OrgTreeService:
    def __init__(self, db: Session) -> None:
        self._companies = CompanyRepository(db)
        self._branches = BranchRepository(db)
        self._departments = DepartmentRepository(db)
        self._scope = OrgScopeValidator(db)

    def get_tree(self, ctx: TenantContext, company_id: UUID | None = None) -> dict:
        if company_id:
            self._scope.validate_company_access(ctx, company_id)
            company = self._companies.get_by_id(ctx, company_id)
            if company is None:
                raise NotFoundException("Company not found")
            companies = [company]
        else:
            companies = self._companies.list_companies(ctx)

        tree: list[dict] = []
        for company in companies:
            branches = self._branches.list_branches(ctx, company_id=company.id)
            branch_nodes = []
            for branch in branches:
                departments = self._departments.list_departments(
                    ctx, company_id=company.id, branch_id=branch.id
                )
                dept_nodes: list[dict] = [
                    {
                        "id": str(d.id),
                        "code": d.department_code,
                        "name": d.department_name,
                        "parent_id": str(d.parent_department_id)
                        if d.parent_department_id
                        else None,
                        "children": [],
                    }
                    for d in departments
                ]
                branch_nodes.append(
                    {
                        "id": str(branch.id),
                        "code": branch.branch_code,
                        "name": branch.branch_name,
                        "departments": self._build_dept_tree(dept_nodes),
                    }
                )
            tree.append(
                {
                    "id": str(company.id),
                    "code": company.company_code,
                    "name": company.company_name,
                    "branches": branch_nodes,
                }
            )
        return {"companies": tree}

    @staticmethod
    def _build_dept_tree(flat: list[dict]) -> list[dict]:
        by_id = {n["id"]: n for n in flat}
        roots: list[dict] = []
        for node in flat:
            parent_id = node.get("parent_id")
            if parent_id and parent_id in by_id:
                by_id[parent_id]["children"].append(node)
            else:
                roots.append(node)
        return roots
