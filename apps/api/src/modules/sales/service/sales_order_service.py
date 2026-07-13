"""Sales order service."""

from decimal import Decimal
from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import ForbiddenException, NotFoundException
from modules.foundation.domain.enums import WorkflowStatus
from modules.foundation.domain.value_objects import TenantContext
from modules.foundation.service.audit_service import AuditService
from modules.foundation.service.rbac_service import RBACService
from modules.inventory.adapters.sales_adapter import SalesInventoryAdapter
from modules.sales.domain.enums import OrderStatus, SalesEntityType
from modules.sales.domain.exceptions import InvalidDocumentState
from modules.sales.domain.value_objects import LineTotals
from modules.sales.models.order import SalesOrderHeader
from modules.sales.repository.credit_repository import CreditRepository
from modules.sales.repository.order_repository import OrderRepository
from modules.sales.service.document_number_service import DocumentNumberService
from modules.sales.service.engines.credit_check_engine import CreditCheckEngine
from modules.sales.service.engines.order_engine import OrderEngine
from modules.sales.service.governance_service import SalesGovernanceService
from modules.sales.service.sales_scope_validator import SalesScopeValidator


class SalesOrderService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._repo = OrderRepository(db)
        self._credit_repo = CreditRepository(db)
        self._scope = SalesScopeValidator(db)
        self._engine = OrderEngine()
        self._credit_engine = CreditCheckEngine()
        self._numbers = DocumentNumberService(db)
        self._governance = SalesGovernanceService(db)
        self._rbac = RBACService(db)
        self._inventory = SalesInventoryAdapter(db)
        self._audit = AuditService(db)

    def list_orders(self, ctx: TenantContext, company_id: UUID | None = None):
        cid = self._scope.resolve_company_id(ctx, company_id)
        return self._repo.list_orders(ctx, cid)

    def get_order(self, ctx: TenantContext, order_id: UUID) -> SalesOrderHeader:
        row = self._repo.get_order(ctx, order_id)
        if row is None:
            raise NotFoundException("Sales order not found")
        self._scope.validate_company_access(ctx, row.company_id)
        self._scope.validate_branch_access(ctx, row.branch_id)
        return row

    def create(
        self,
        ctx: TenantContext,
        *,
        branch_id: UUID,
        document_date,
        customer_id: UUID,
        currency_code: str,
        company_id: UUID | None = None,
        exchange_rate: float = 1.0,
        requested_delivery_date=None,
        quotation_header_id: UUID | None = None,
        price_list_id: UUID | None = None,
    ):
        cid = self._scope.resolve_company_id(ctx, company_id)
        self._scope.validate_branch_access(ctx, branch_id)
        doc_number = self._numbers.generate(
            SalesEntityType.ORDER,
            cid,
            model=SalesOrderHeader,
            code_column="document_number",
        )
        row = self._repo.create_order(
            ctx,
            company_id=cid,
            branch_id=branch_id,
            document_number=doc_number,
            document_date=document_date,
            requested_delivery_date=requested_delivery_date,
            customer_id=customer_id,
            quotation_header_id=quotation_header_id,
            price_list_id=price_list_id,
            currency_code=currency_code,
            exchange_rate=exchange_rate,
            status=OrderStatus.DRAFT.value,
            workflow_status=WorkflowStatus.PENDING.value,
        )
        self._audit.log_entity_change(
            tenant_id=ctx.tenant_id,
            entity_name="sales_order_header",
            entity_id=row.id,
            operation="create",
            performed_by=ctx.user_id,
        )
        return row

    def add_line(self, ctx: TenantContext, order_id: UUID, **fields):
        order = self.get_order(ctx, order_id)
        if order.status != OrderStatus.DRAFT.value:
            raise InvalidDocumentState("Lines can only be added to draft orders")
        line = self._repo.add_line(ctx, order, **fields)
        totals = LineTotals.compute(
            quantity=Decimal(str(line.quantity)),
            unit_price=Decimal(str(line.unit_price)),
            discount_amount=Decimal(str(line.discount_amount)),
            tax_rate=Decimal(str(line.tax_rate)),
        )
        line.tax_amount = float(totals.tax_amount)
        line.line_total = float(totals.line_total)
        order = self.get_order(ctx, order_id)
        self._refresh_totals(order)
        self._db.flush()
        return line

    def _refresh_totals(self, order: SalesOrderHeader) -> None:
        active = [ln for ln in order.lines if not getattr(ln, "is_deleted", False)]
        subtotal = Decimal("0")
        discount = Decimal("0")
        tax = Decimal("0")
        for line in active:
            subtotal += Decimal(str(line.quantity)) * Decimal(str(line.unit_price))
            discount += Decimal(str(line.discount_amount))
            tax += Decimal(str(line.tax_amount))
        order.subtotal_amount = float(subtotal.quantize(Decimal("0.0001")))
        order.discount_amount = float(discount.quantize(Decimal("0.0001")))
        order.tax_amount = float(tax.quantize(Decimal("0.0001")))
        order.total_amount = float((subtotal - discount + tax).quantize(Decimal("0.0001")))

    def submit(self, ctx: TenantContext, order_id: UUID):
        order = self.get_order(ctx, order_id)
        if order.status != OrderStatus.DRAFT.value:
            raise InvalidDocumentState("Only draft orders can be submitted")
        instance = self._governance.submit_for_approval(
            ctx, entity_name="sales_order_header", entity_id=order_id
        )
        return self._repo.update_order(
            ctx,
            order_id,
            workflow_status=WorkflowStatus.IN_PROGRESS.value,
            workflow_instance_id=instance.id,
        )

    def confirm(
        self,
        ctx: TenantContext,
        order_id: UUID,
        *,
        credit_override: bool = False,
        warehouse_id: UUID | None = None,
    ):
        order = self.get_order(ctx, order_id)
        self._engine.validate_confirmable(order)
        if credit_override and not self._rbac.has_permission(
            ctx.user_id, ctx.tenant_id, "sales.order:credit_override"
        ):
            raise ForbiddenException("Credit override permission required")
        credit = self._credit_repo.get_by_customer(
            ctx, order.company_id, order.customer_id, branch_id=None
        )
        if credit is not None:
            self._credit_engine.check(
                credit,
                additional_amount=Decimal(str(order.total_amount)),
                raise_on_fail=not credit_override,
            )
        reservation_status = None
        if warehouse_id is not None:
            self._inventory.reserve_order(ctx, order_id, warehouse_id)
            reservation_status = "reserved"
        updated = self._repo.update_order(
            ctx,
            order_id,
            status=OrderStatus.CONFIRMED.value,
            workflow_status=WorkflowStatus.APPROVED.value,
            reservation_status=reservation_status,
        )
        self._audit.log_entity_change(
            tenant_id=ctx.tenant_id,
            entity_name="sales_order_header",
            entity_id=order_id,
            operation="confirm",
            performed_by=ctx.user_id,
        )
        return updated

    def cancel(self, ctx: TenantContext, order_id: UUID):
        order = self.get_order(ctx, order_id)
        if order.status in {
            OrderStatus.DELIVERED.value,
            OrderStatus.CLOSED.value,
            OrderStatus.CANCELLED.value,
        }:
            raise InvalidDocumentState("Order cannot be cancelled in its current state")
        if order.reservation_status == "reserved":
            self._inventory.release_order(ctx, order_id)
        return self._repo.update_order(
            ctx,
            order_id,
            status=OrderStatus.CANCELLED.value,
            reservation_status="released",
        )

    def delete(self, ctx: TenantContext, order_id: UUID) -> None:
        order = self.get_order(ctx, order_id)
        if order.status != OrderStatus.DRAFT.value:
            raise InvalidDocumentState("Only draft orders can be deleted")
        if not self._repo.soft_delete_order(ctx, order_id):
            raise NotFoundException("Sales order not found")
