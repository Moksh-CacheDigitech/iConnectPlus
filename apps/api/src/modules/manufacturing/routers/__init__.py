"""Manufacturing REST routers."""

from decimal import Decimal
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.session import get_db
from modules.foundation.dependencies import require_permission
from modules.foundation.domain.value_objects import TenantContext
from modules.manufacturing.dependencies import (
    PaginationParams,
    extract_update_fields,
    get_pagination,
    paginate,
)
from modules.manufacturing.schemas import (
    BomCreateRequest,
    BomResponse,
    BomUpdateRequest,
    CloseOrderRequest,
    MachineCreateRequest,
    MachineResponse,
    MachineUpdateRequest,
    MaterialConfirmRequest,
    MaterialIssueCreateRequest,
    MaterialIssueResponse,
    MaterialReturnCreateRequest,
    MaterialReturnResponse,
    OperationUpdateRequest,
    ProductionOrderCreateRequest,
    ProductionOrderResponse,
    ProductionOrderUpdateRequest,
    ProductionReceiptCreateRequest,
    ProductionReceiptResponse,
    ReceiptConfirmRequest,
    ReportSummaryResponse,
    RoutingCreateRequest,
    RoutingResponse,
    RoutingUpdateRequest,
    ScrapCreateRequest,
    ScrapPostRequest,
    ScrapResponse,
    VariancePostRequest,
    VarianceResponse,
    WipResponse,
    WorkCenterCreateRequest,
    WorkCenterResponse,
    WorkCenterUpdateRequest,
)
from modules.manufacturing.service import (
    BomService,
    MachineService,
    ManufacturingReportService,
    MaterialIssueService,
    MaterialReturnService,
    ProductionOrderService,
    ProductionReceiptService,
    RoutingService,
    ScrapService,
    VarianceService,
    WipService,
    WorkCenterService,
)
from shared.schemas import APIResponse

boms_router = APIRouter(prefix="/boms", tags=["Manufacturing - BOM"])
routings_router = APIRouter(prefix="/routings", tags=["Manufacturing - Routing"])
work_centers_router = APIRouter(prefix="/work-centers", tags=["Manufacturing - Work Centers"])
machines_router = APIRouter(prefix="/machines", tags=["Manufacturing - Machines"])
orders_router = APIRouter(prefix="/production-orders", tags=["Manufacturing - Production Orders"])
issues_router = APIRouter(prefix="/material-issues", tags=["Manufacturing - Material Issues"])
returns_router = APIRouter(prefix="/material-returns", tags=["Manufacturing - Material Returns"])
receipts_router = APIRouter(prefix="/production-receipts", tags=["Manufacturing - Receipts"])
scrap_router = APIRouter(prefix="/scrap", tags=["Manufacturing - Scrap"])
wip_router = APIRouter(prefix="/wip", tags=["Manufacturing - WIP"])
variances_router = APIRouter(prefix="/variances", tags=["Manufacturing - Variances"])
reports_router = APIRouter(prefix="/reports", tags=["Manufacturing - Reports"])


@boms_router.get("", response_model=APIResponse[list[BomResponse]])
def list_boms(
    ctx: Annotated[TenantContext, Depends(require_permission("manufacturing.bom:read"))],
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends(get_pagination)],
    company_id: UUID | None = None,
    product_id: UUID | None = None,
):
    rows = BomService(db).list_boms(ctx, company_id, product_id)
    return APIResponse(
        message="BOMs retrieved",
        data=[BomResponse.model_validate(r) for r in paginate(rows, pagination)],
    )


@boms_router.post("", response_model=APIResponse[BomResponse])
def create_bom(
    body: BomCreateRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("manufacturing.bom:create"))],
    db: Annotated[Session, Depends(get_db)],
):
    data = body.model_dump()
    lines = data.pop("lines", [])
    row = BomService(db).create_bom(ctx, lines=lines, **data)
    db.commit()
    return APIResponse(message="BOM created", data=BomResponse.model_validate(row))


@boms_router.get("/{bom_id}", response_model=APIResponse[BomResponse])
def get_bom(
    bom_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("manufacturing.bom:read"))],
    db: Annotated[Session, Depends(get_db)],
):
    row = BomService(db).get_bom(ctx, bom_id)
    return APIResponse(message="BOM retrieved", data=BomResponse.model_validate(row))


@boms_router.patch("/{bom_id}", response_model=APIResponse[BomResponse])
def update_bom(
    bom_id: UUID,
    body: BomUpdateRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("manufacturing.bom:update"))],
    db: Annotated[Session, Depends(get_db)],
):
    row = BomService(db).update_bom(ctx, bom_id, **extract_update_fields(body))
    db.commit()
    return APIResponse(message="BOM updated", data=BomResponse.model_validate(row))


@boms_router.post("/{bom_id}/submit", response_model=APIResponse[BomResponse])
def submit_bom(
    bom_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("manufacturing.bom:submit"))],
    db: Annotated[Session, Depends(get_db)],
):
    row = BomService(db).submit(ctx, bom_id)
    db.commit()
    return APIResponse(message="BOM submitted", data=BomResponse.model_validate(row))


@boms_router.post("/{bom_id}/approve", response_model=APIResponse[BomResponse])
def approve_bom(
    bom_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("manufacturing.bom:approve"))],
    db: Annotated[Session, Depends(get_db)],
):
    row = BomService(db).approve_activate(ctx, bom_id)
    db.commit()
    return APIResponse(message="BOM approved/activated", data=BomResponse.model_validate(row))


@routings_router.get("", response_model=APIResponse[list[RoutingResponse]])
def list_routings(
    ctx: Annotated[TenantContext, Depends(require_permission("manufacturing.routing:read"))],
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends(get_pagination)],
    company_id: UUID | None = None,
):
    rows = RoutingService(db).list_routings(ctx, company_id)
    return APIResponse(
        message="Routings retrieved",
        data=[RoutingResponse.model_validate(r) for r in paginate(rows, pagination)],
    )


@routings_router.post("", response_model=APIResponse[RoutingResponse])
def create_routing(
    body: RoutingCreateRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("manufacturing.routing:create"))],
    db: Annotated[Session, Depends(get_db)],
):
    data = body.model_dump()
    ops = data.pop("operations", [])
    row = RoutingService(db).create_routing(ctx, operations=ops, **data)
    db.commit()
    return APIResponse(message="Routing created", data=RoutingResponse.model_validate(row))


@routings_router.patch("/{routing_id}", response_model=APIResponse[RoutingResponse])
def update_routing(
    routing_id: UUID,
    body: RoutingUpdateRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("manufacturing.routing:update"))],
    db: Annotated[Session, Depends(get_db)],
):
    row = RoutingService(db).update_routing(ctx, routing_id, **extract_update_fields(body))
    db.commit()
    return APIResponse(message="Routing updated", data=RoutingResponse.model_validate(row))


@routings_router.post("/{routing_id}/activate", response_model=APIResponse[RoutingResponse])
def activate_routing(
    routing_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("manufacturing.routing:update"))],
    db: Annotated[Session, Depends(get_db)],
):
    row = RoutingService(db).activate(ctx, routing_id)
    db.commit()
    return APIResponse(message="Routing activated", data=RoutingResponse.model_validate(row))


@work_centers_router.get("", response_model=APIResponse[list[WorkCenterResponse]])
def list_work_centers(
    ctx: Annotated[TenantContext, Depends(require_permission("manufacturing.work_center:read"))],
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends(get_pagination)],
    company_id: UUID | None = None,
):
    rows = WorkCenterService(db).list_work_centers(ctx, company_id)
    return APIResponse(
        message="Work centers retrieved",
        data=[WorkCenterResponse.model_validate(r) for r in paginate(rows, pagination)],
    )


@work_centers_router.post("", response_model=APIResponse[WorkCenterResponse])
def create_work_center(
    body: WorkCenterCreateRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("manufacturing.work_center:create"))],
    db: Annotated[Session, Depends(get_db)],
):
    row = WorkCenterService(db).create_work_center(ctx, **body.model_dump())
    db.commit()
    return APIResponse(message="Work center created", data=WorkCenterResponse.model_validate(row))


@work_centers_router.patch("/{work_center_id}", response_model=APIResponse[WorkCenterResponse])
def update_work_center(
    work_center_id: UUID,
    body: WorkCenterUpdateRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("manufacturing.work_center:update"))],
    db: Annotated[Session, Depends(get_db)],
):
    row = WorkCenterService(db).update_work_center(
        ctx, work_center_id, **extract_update_fields(body)
    )
    db.commit()
    return APIResponse(message="Work center updated", data=WorkCenterResponse.model_validate(row))


@machines_router.get("", response_model=APIResponse[list[MachineResponse]])
def list_machines(
    ctx: Annotated[TenantContext, Depends(require_permission("manufacturing.machine:read"))],
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends(get_pagination)],
    company_id: UUID | None = None,
):
    rows = MachineService(db).list_machines(ctx, company_id)
    return APIResponse(
        message="Machines retrieved",
        data=[MachineResponse.model_validate(r) for r in paginate(rows, pagination)],
    )


@machines_router.post("", response_model=APIResponse[MachineResponse])
def create_machine(
    body: MachineCreateRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("manufacturing.machine:create"))],
    db: Annotated[Session, Depends(get_db)],
):
    row = MachineService(db).create_machine(ctx, **body.model_dump())
    db.commit()
    return APIResponse(message="Machine created", data=MachineResponse.model_validate(row))


@machines_router.patch("/{machine_id}", response_model=APIResponse[MachineResponse])
def update_machine(
    machine_id: UUID,
    body: MachineUpdateRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("manufacturing.machine:update"))],
    db: Annotated[Session, Depends(get_db)],
):
    row = MachineService(db).update_machine(ctx, machine_id, **extract_update_fields(body))
    db.commit()
    return APIResponse(message="Machine updated", data=MachineResponse.model_validate(row))


@orders_router.get("", response_model=APIResponse[list[ProductionOrderResponse]])
def list_orders(
    ctx: Annotated[TenantContext, Depends(require_permission("manufacturing.production_order:read"))],
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends(get_pagination)],
    company_id: UUID | None = None,
):
    rows = ProductionOrderService(db).list_orders(ctx, company_id)
    return APIResponse(
        message="Production orders retrieved",
        data=[ProductionOrderResponse.model_validate(r) for r in paginate(rows, pagination)],
    )


@orders_router.post("", response_model=APIResponse[ProductionOrderResponse])
def create_order(
    body: ProductionOrderCreateRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("manufacturing.production_order:create"))],
    db: Annotated[Session, Depends(get_db)],
):
    data = body.model_dump()
    data["planned_qty"] = Decimal(str(data["planned_qty"]))
    row = ProductionOrderService(db).create_order(ctx, **data)
    db.commit()
    return APIResponse(message="Production order created", data=ProductionOrderResponse.model_validate(row))


@orders_router.get("/{order_id}", response_model=APIResponse[ProductionOrderResponse])
def get_order(
    order_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("manufacturing.production_order:read"))],
    db: Annotated[Session, Depends(get_db)],
):
    row = ProductionOrderService(db).get_order(ctx, order_id)
    return APIResponse(message="Production order retrieved", data=ProductionOrderResponse.model_validate(row))


@orders_router.patch("/{order_id}", response_model=APIResponse[ProductionOrderResponse])
def update_order(
    order_id: UUID,
    body: ProductionOrderUpdateRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("manufacturing.production_order:update"))],
    db: Annotated[Session, Depends(get_db)],
):
    row = ProductionOrderService(db).update_order(ctx, order_id, **extract_update_fields(body))
    db.commit()
    return APIResponse(message="Production order updated", data=ProductionOrderResponse.model_validate(row))


def _order_action(db, ctx, order_id, action: str, **kwargs):
    svc = ProductionOrderService(db)
    row = getattr(svc, action)(ctx, order_id, **kwargs)
    db.commit()
    return APIResponse(
        message=f"Production order {action}",
        data=ProductionOrderResponse.model_validate(row),
    )


@orders_router.post("/{order_id}/release", response_model=APIResponse[ProductionOrderResponse])
def release_order(
    order_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("manufacturing.production_order:release"))],
    db: Annotated[Session, Depends(get_db)],
):
    return _order_action(db, ctx, order_id, "release")


@orders_router.post("/{order_id}/start", response_model=APIResponse[ProductionOrderResponse])
def start_order(
    order_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("manufacturing.production_order:update"))],
    db: Annotated[Session, Depends(get_db)],
):
    return _order_action(db, ctx, order_id, "start")


@orders_router.post("/{order_id}/complete", response_model=APIResponse[ProductionOrderResponse])
def complete_order(
    order_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("manufacturing.production_order:complete"))],
    db: Annotated[Session, Depends(get_db)],
):
    return _order_action(db, ctx, order_id, "complete")


@orders_router.post("/{order_id}/close", response_model=APIResponse[ProductionOrderResponse])
def close_order(
    order_id: UUID,
    body: CloseOrderRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("manufacturing.production_order:close"))],
    db: Annotated[Session, Depends(get_db)],
):
    return _order_action(db, ctx, order_id, "close", **body.model_dump())


@orders_router.post("/{order_id}/cancel", response_model=APIResponse[ProductionOrderResponse])
def cancel_order(
    order_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("manufacturing.production_order:cancel"))],
    db: Annotated[Session, Depends(get_db)],
):
    return _order_action(db, ctx, order_id, "cancel")


@orders_router.patch(
    "/{order_id}/operations/{operation_id}",
    response_model=APIResponse[ProductionOrderResponse],
)
def update_operation(
    order_id: UUID,
    operation_id: UUID,
    body: OperationUpdateRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("manufacturing.production_order:update"))],
    db: Annotated[Session, Depends(get_db)],
):
    row = ProductionOrderService(db).update_operation(
        ctx, order_id, operation_id, **extract_update_fields(body)
    )
    db.commit()
    return APIResponse(message="Operation updated", data=ProductionOrderResponse.model_validate(row))


@issues_router.get("", response_model=APIResponse[list[MaterialIssueResponse]])
def list_issues(
    ctx: Annotated[TenantContext, Depends(require_permission("manufacturing.material_issue:read"))],
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends(get_pagination)],
    company_id: UUID | None = None,
):
    rows = MaterialIssueService(db).list_issues(ctx, company_id)
    return APIResponse(
        message="Material issues retrieved",
        data=[MaterialIssueResponse.model_validate(r) for r in paginate(rows, pagination)],
    )


@issues_router.post("", response_model=APIResponse[MaterialIssueResponse])
def create_issue(
    body: MaterialIssueCreateRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("manufacturing.material_issue:create"))],
    db: Annotated[Session, Depends(get_db)],
):
    data = body.model_dump()
    lines = data.pop("lines")
    row = MaterialIssueService(db).create_issue(ctx, lines=lines, **data)
    db.commit()
    return APIResponse(message="Material issue created", data=MaterialIssueResponse.model_validate(row))


@issues_router.post("/{issue_id}/confirm", response_model=APIResponse[MaterialIssueResponse])
def confirm_issue(
    issue_id: UUID,
    body: MaterialConfirmRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("manufacturing.material_issue:confirm"))],
    db: Annotated[Session, Depends(get_db)],
):
    row = MaterialIssueService(db).confirm(ctx, issue_id, **body.model_dump())
    db.commit()
    return APIResponse(message="Material issue confirmed", data=MaterialIssueResponse.model_validate(row))


@returns_router.get("", response_model=APIResponse[list[MaterialReturnResponse]])
def list_returns(
    ctx: Annotated[TenantContext, Depends(require_permission("manufacturing.material_return:read"))],
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends(get_pagination)],
    company_id: UUID | None = None,
):
    rows = MaterialReturnService(db).list_returns(ctx, company_id)
    return APIResponse(
        message="Material returns retrieved",
        data=[MaterialReturnResponse.model_validate(r) for r in paginate(rows, pagination)],
    )


@returns_router.post("", response_model=APIResponse[MaterialReturnResponse])
def create_return(
    body: MaterialReturnCreateRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("manufacturing.material_return:create"))],
    db: Annotated[Session, Depends(get_db)],
):
    data = body.model_dump()
    lines = data.pop("lines")
    row = MaterialReturnService(db).create_return(ctx, lines=lines, **data)
    db.commit()
    return APIResponse(message="Material return created", data=MaterialReturnResponse.model_validate(row))


@returns_router.post("/{return_id}/confirm", response_model=APIResponse[MaterialReturnResponse])
def confirm_return(
    return_id: UUID,
    body: MaterialConfirmRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("manufacturing.material_return:confirm"))],
    db: Annotated[Session, Depends(get_db)],
):
    row = MaterialReturnService(db).confirm(ctx, return_id, **body.model_dump())
    db.commit()
    return APIResponse(message="Material return confirmed", data=MaterialReturnResponse.model_validate(row))


@receipts_router.get("", response_model=APIResponse[list[ProductionReceiptResponse]])
def list_receipts(
    ctx: Annotated[TenantContext, Depends(require_permission("manufacturing.production_receipt:read"))],
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends(get_pagination)],
    company_id: UUID | None = None,
):
    rows = ProductionReceiptService(db).list_receipts(ctx, company_id)
    return APIResponse(
        message="Production receipts retrieved",
        data=[ProductionReceiptResponse.model_validate(r) for r in paginate(rows, pagination)],
    )


@receipts_router.post("", response_model=APIResponse[ProductionReceiptResponse])
def create_receipt(
    body: ProductionReceiptCreateRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("manufacturing.production_receipt:create"))],
    db: Annotated[Session, Depends(get_db)],
):
    data = body.model_dump()
    lines = data.pop("lines")
    row = ProductionReceiptService(db).create_receipt(ctx, lines=lines, **data)
    db.commit()
    return APIResponse(
        message="Production receipt created",
        data=ProductionReceiptResponse.model_validate(row),
    )


@receipts_router.post("/{receipt_id}/confirm", response_model=APIResponse[ProductionReceiptResponse])
def confirm_receipt(
    receipt_id: UUID,
    body: ReceiptConfirmRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("manufacturing.production_receipt:confirm"))],
    db: Annotated[Session, Depends(get_db)],
):
    row = ProductionReceiptService(db).confirm(ctx, receipt_id, **body.model_dump())
    db.commit()
    return APIResponse(
        message="Production receipt confirmed",
        data=ProductionReceiptResponse.model_validate(row),
    )


@scrap_router.get("", response_model=APIResponse[list[ScrapResponse]])
def list_scraps(
    ctx: Annotated[TenantContext, Depends(require_permission("manufacturing.scrap:read"))],
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends(get_pagination)],
    company_id: UUID | None = None,
):
    rows = ScrapService(db).list_scraps(ctx, company_id)
    return APIResponse(
        message="Scrap retrieved",
        data=[ScrapResponse.model_validate(r) for r in paginate(rows, pagination)],
    )


@scrap_router.post("", response_model=APIResponse[ScrapResponse])
def create_scrap(
    body: ScrapCreateRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("manufacturing.scrap:create"))],
    db: Annotated[Session, Depends(get_db)],
):
    row = ScrapService(db).create_scrap(ctx, **body.model_dump())
    db.commit()
    return APIResponse(message="Scrap created", data=ScrapResponse.model_validate(row))


@scrap_router.post("/{scrap_id}/submit", response_model=APIResponse[ScrapResponse])
def submit_scrap(
    scrap_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("manufacturing.scrap:submit"))],
    db: Annotated[Session, Depends(get_db)],
):
    row = ScrapService(db).submit(ctx, scrap_id)
    db.commit()
    return APIResponse(message="Scrap submitted", data=ScrapResponse.model_validate(row))


@scrap_router.post("/{scrap_id}/approve", response_model=APIResponse[ScrapResponse])
def approve_scrap(
    scrap_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("manufacturing.scrap:approve"))],
    db: Annotated[Session, Depends(get_db)],
):
    row = ScrapService(db).approve(ctx, scrap_id)
    db.commit()
    return APIResponse(message="Scrap approved", data=ScrapResponse.model_validate(row))


@scrap_router.post("/{scrap_id}/post", response_model=APIResponse[ScrapResponse])
def post_scrap(
    scrap_id: UUID,
    body: ScrapPostRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("manufacturing.scrap:post"))],
    db: Annotated[Session, Depends(get_db)],
):
    row = ScrapService(db).post(ctx, scrap_id, **body.model_dump())
    db.commit()
    return APIResponse(message="Scrap posted", data=ScrapResponse.model_validate(row))


@wip_router.get("", response_model=APIResponse[list[WipResponse]])
def list_wip(
    ctx: Annotated[TenantContext, Depends(require_permission("manufacturing.wip:read"))],
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends(get_pagination)],
    company_id: UUID | None = None,
):
    rows = WipService(db).list_wip(ctx, company_id)
    return APIResponse(
        message="WIP retrieved",
        data=[WipResponse.model_validate(r) for r in paginate(rows, pagination)],
    )


@variances_router.get("", response_model=APIResponse[list[VarianceResponse]])
def list_variances(
    ctx: Annotated[TenantContext, Depends(require_permission("manufacturing.variance:read"))],
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends(get_pagination)],
    company_id: UUID | None = None,
):
    rows = VarianceService(db).list_variances(ctx, company_id)
    return APIResponse(
        message="Variances retrieved",
        data=[VarianceResponse.model_validate(r) for r in paginate(rows, pagination)],
    )


@variances_router.post("/{variance_id}/post", response_model=APIResponse[VarianceResponse])
def post_variance(
    variance_id: UUID,
    body: VariancePostRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("manufacturing.variance:post"))],
    db: Annotated[Session, Depends(get_db)],
):
    row = VarianceService(db).post(ctx, variance_id, **body.model_dump())
    db.commit()
    return APIResponse(message="Variance posted", data=VarianceResponse.model_validate(row))


@reports_router.get("/bom-summary", response_model=APIResponse[ReportSummaryResponse])
def bom_summary(
    ctx: Annotated[TenantContext, Depends(require_permission("manufacturing.report:read"))],
    db: Annotated[Session, Depends(get_db)],
    company_id: UUID | None = None,
):
    data = ManufacturingReportService(db).bom_summary(ctx, company_id)
    return APIResponse(message="BOM summary", data=ReportSummaryResponse(**data))


@reports_router.get("/wo-summary", response_model=APIResponse[ReportSummaryResponse])
def wo_summary(
    ctx: Annotated[TenantContext, Depends(require_permission("manufacturing.report:read"))],
    db: Annotated[Session, Depends(get_db)],
    company_id: UUID | None = None,
):
    data = ManufacturingReportService(db).wo_summary(ctx, company_id)
    return APIResponse(message="WO summary", data=ReportSummaryResponse(**data))


@reports_router.get("/wip-summary", response_model=APIResponse[ReportSummaryResponse])
def wip_summary(
    ctx: Annotated[TenantContext, Depends(require_permission("manufacturing.report:read"))],
    db: Annotated[Session, Depends(get_db)],
    company_id: UUID | None = None,
):
    data = ManufacturingReportService(db).wip_summary(ctx, company_id)
    return APIResponse(message="WIP summary", data=ReportSummaryResponse(**data))


@reports_router.get("/scrap-summary", response_model=APIResponse[ReportSummaryResponse])
def scrap_summary(
    ctx: Annotated[TenantContext, Depends(require_permission("manufacturing.report:read"))],
    db: Annotated[Session, Depends(get_db)],
    company_id: UUID | None = None,
):
    data = ManufacturingReportService(db).scrap_summary(ctx, company_id)
    return APIResponse(message="Scrap summary", data=ReportSummaryResponse(**data))


@reports_router.get("/machine-utilization", response_model=APIResponse[ReportSummaryResponse])
def machine_utilization(
    ctx: Annotated[TenantContext, Depends(require_permission("manufacturing.report:read"))],
    db: Annotated[Session, Depends(get_db)],
    company_id: UUID | None = None,
):
    data = ManufacturingReportService(db).machine_utilization(ctx, company_id)
    return APIResponse(message="Machine utilization", data=ReportSummaryResponse(**data))
