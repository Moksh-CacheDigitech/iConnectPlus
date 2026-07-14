"""Routing application service."""

from decimal import Decimal
from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import NotFoundException
from modules.foundation.domain.value_objects import TenantContext
from modules.foundation.service.audit_service import AuditService
from modules.manufacturing.domain.enums import MfgEntityType, RoutingStatus
from modules.manufacturing.models.routing import MfgRouting
from modules.manufacturing.repository.routing_repository import RoutingRepository
from modules.manufacturing.service.document_number_service import DocumentNumberService
from modules.manufacturing.service.engines import RoutingEngine
from modules.manufacturing.service.mfg_scope_validator import MfgScopeValidator


class RoutingService:
    def __init__(self, db: Session) -> None:
        self._repo = RoutingRepository(db)
        self._numbers = DocumentNumberService(db)
        self._engine = RoutingEngine()
        self._scope = MfgScopeValidator(db)
        self._audit = AuditService(db)

    def list_routings(self, ctx: TenantContext, company_id: UUID | None = None):
        cid = self._scope.resolve_company_id(ctx, company_id)
        return self._repo.list_routings(ctx, cid)

    def get_routing(self, ctx: TenantContext, routing_id: UUID) -> MfgRouting:
        row = self._repo.get(ctx, routing_id)
        if row is None:
            raise NotFoundException("Routing not found")
        return row

    def create_routing(
        self,
        ctx: TenantContext,
        *,
        company_id: UUID,
        operations: list[dict],
        routing_name: str | None = None,
        product_id: UUID | None = None,
        branch_id: UUID | None = None,
        notes: str | None = None,
    ) -> MfgRouting:
        self._scope.validate_company_access(ctx, company_id)
        code = self._numbers.generate(
            MfgEntityType.ROUTING, company_id, model=MfgRouting, code_column="routing_code"
        )
        routing = self._repo.create(
            ctx,
            company_id=company_id,
            branch_id=branch_id,
            routing_code=code,
            routing_name=routing_name,
            product_id=product_id,
            notes=notes,
            status=RoutingStatus.DRAFT.value,
        )
        for i, op in enumerate(operations, start=1):
            self._repo.add_operation(
                ctx,
                routing,
                operation_seq=op.get("operation_seq", i),
                operation_code=op["operation_code"],
                operation_name=op.get("operation_name"),
                work_center_id=op["work_center_id"],
                setup_time_minutes=Decimal(str(op.get("setup_time_minutes", 0))),
                run_time_minutes=Decimal(str(op.get("run_time_minutes", 0))),
                status=op.get("status", "active"),
            )
        return self.get_routing(ctx, routing.id)

    def update_routing(self, ctx: TenantContext, routing_id: UUID, **fields) -> MfgRouting:
        self.get_routing(ctx, routing_id)
        self._repo.update(ctx, routing_id, **fields)
        return self.get_routing(ctx, routing_id)

    def activate(self, ctx: TenantContext, routing_id: UUID) -> MfgRouting:
        routing = self.get_routing(ctx, routing_id)
        self._engine.validate_activatable(routing)
        self._repo.update(ctx, routing_id, status=RoutingStatus.ACTIVE.value)
        self._audit.log_entity_change(
            tenant_id=ctx.tenant_id,
            entity_name="mfg_routing",
            entity_id=routing_id,
            operation="activate",
            performed_by=ctx.user_id,
        )
        return self.get_routing(ctx, routing_id)
