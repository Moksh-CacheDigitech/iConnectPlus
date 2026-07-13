"""Discount rule service."""

from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import NotFoundException
from modules.foundation.domain.value_objects import TenantContext
from modules.foundation.service.audit_service import AuditService
from modules.sales.domain.exceptions import InvalidDocumentState
from modules.sales.repository.pricing_repository import PricingRepository
from modules.sales.service.governance_service import SalesGovernanceService
from modules.sales.service.sales_scope_validator import SalesScopeValidator


class DiscountService:
    def __init__(self, db: Session) -> None:
        self._repo = PricingRepository(db)
        self._scope = SalesScopeValidator(db)
        self._governance = SalesGovernanceService(db)
        self._audit = AuditService(db)

    def list_rules(self, ctx: TenantContext, company_id: UUID | None = None):
        cid = self._scope.resolve_company_id(ctx, company_id)
        return self._repo.list_discount_rules(ctx, cid)

    def get_rule(self, ctx: TenantContext, rule_id: UUID):
        row = self._repo.get_discount_rule(ctx, rule_id)
        if row is None:
            raise NotFoundException("Discount rule not found")
        self._scope.validate_company_access(ctx, row.company_id)
        return row

    def create_rule(self, ctx: TenantContext, company_id: UUID | None = None, **fields):
        cid = self._scope.resolve_company_id(ctx, company_id)
        if fields.get("branch_id"):
            self._scope.validate_branch_access(ctx, fields["branch_id"])
        row = self._repo.create_discount_rule(ctx, company_id=cid, **fields)
        self._audit.log_entity_change(
            tenant_id=ctx.tenant_id,
            entity_name="sales_discount_rule",
            entity_id=row.id,
            operation="create",
            performed_by=ctx.user_id,
        )
        return row

    def update_rule(self, ctx: TenantContext, rule_id: UUID, **fields):
        self.get_rule(ctx, rule_id)
        updated = self._repo.update_discount_rule(ctx, rule_id, **fields)
        if updated is None:
            raise NotFoundException("Discount rule not found")
        return updated

    def delete_rule(self, ctx: TenantContext, rule_id: UUID) -> None:
        self.get_rule(ctx, rule_id)
        if not self._repo.soft_delete_discount_rule(ctx, rule_id):
            raise NotFoundException("Discount rule not found")

    def submit(self, ctx: TenantContext, rule_id: UUID):
        rule = self.get_rule(ctx, rule_id)
        if rule.status != "draft":
            raise InvalidDocumentState("Only draft discount rules can be submitted")
        instance = self._governance.submit_for_approval(
            ctx, entity_name="sales_discount_rule", entity_id=rule_id
        )
        return self._repo.update_discount_rule(
            ctx,
            rule_id,
            workflow_instance_id=instance.id,
            status="draft",
        )

    def approve(self, ctx: TenantContext, rule_id: UUID):
        rule = self.get_rule(ctx, rule_id)
        if rule.workflow_instance_id is None:
            raise InvalidDocumentState("Discount rule has no workflow instance")

        def on_approved():
            self._repo.update_discount_rule(ctx, rule_id, status="active")

        return self._governance.approve(
            ctx,
            instance_id=rule.workflow_instance_id,
            entity_name="sales_discount_rule",
            entity_id=rule_id,
            on_approved=on_approved,
        )
