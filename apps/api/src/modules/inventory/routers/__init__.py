"""Inventory REST routers."""

from decimal import Decimal
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.session import get_db
from modules.foundation.dependencies import require_permission
from modules.foundation.domain.value_objects import TenantContext
from modules.inventory.dependencies import (
    PaginationParams,
    extract_update_fields,
    get_pagination,
    paginate,
)
from modules.inventory.schemas import (
    AdjustmentCreateRequest,
    AdjustmentPostRequest,
    AdjustmentResponse,
    BatchCreateRequest,
    BatchResponse,
    BatchUpdateRequest,
    BinCreateRequest,
    BinResponse,
    BinUpdateRequest,
    CycleCountCreateRequest,
    CycleCountResponse,
    LedgerEntryResponse,
    ReorderPolicyCreateRequest,
    ReorderPolicyResponse,
    ReorderPolicyUpdateRequest,
    ReportSummaryResponse,
    ReservationCreateRequest,
    ReservationResponse,
    SerialCreateRequest,
    SerialResponse,
    SerialUpdateRequest,
    StockBalanceResponse,
    TransferCreateRequest,
    TransferResponse,
    ValuationLayerResponse,
    ValuationRunResponse,
)
from modules.inventory.service import (
    AdjustmentService,
    BatchService,
    BinService,
    CycleCountService,
    ReorderPolicyService,
    ReservationService,
    SerialService,
    StockBalanceService,
    TransferService,
    ValuationService,
)
from shared.schemas import APIResponse

stock_router = APIRouter(prefix="/stock", tags=["Inventory - Stock"])
bins_router = APIRouter(prefix="/bins", tags=["Inventory - Bins"])
batches_router = APIRouter(prefix="/batches", tags=["Inventory - Batches"])
serials_router = APIRouter(prefix="/serials", tags=["Inventory - Serials"])
reservations_router = APIRouter(prefix="/reservations", tags=["Inventory - Reservations"])
transfers_router = APIRouter(prefix="/transfers", tags=["Inventory - Transfers"])
adjustments_router = APIRouter(prefix="/adjustments", tags=["Inventory - Adjustments"])
cycle_counts_router = APIRouter(prefix="/cycle-counts", tags=["Inventory - Cycle Counts"])
policies_router = APIRouter(prefix="/policies", tags=["Inventory - Policies"])
valuation_router = APIRouter(prefix="/valuation", tags=["Inventory - Valuation"])
reports_router = APIRouter(prefix="/reports", tags=["Inventory - Reports"])


@stock_router.get("", response_model=APIResponse[list[StockBalanceResponse]])
def list_stock(
    ctx: Annotated[TenantContext, Depends(require_permission("inventory.stock:read"))],
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends(get_pagination)],
    company_id: UUID | None = None,
    warehouse_id: UUID | None = None,
    product_id: UUID | None = None,
):
    rows = StockBalanceService(db).list_stock(
        ctx, company_id, warehouse_id=warehouse_id, product_id=product_id
    )
    page = paginate(rows, pagination)
    return APIResponse(
        message="Stock balances retrieved",
        data=[StockBalanceResponse.model_validate(r) for r in page],
    )


@stock_router.get("/ledger", response_model=APIResponse[list[LedgerEntryResponse]])
def list_ledger(
    ctx: Annotated[TenantContext, Depends(require_permission("inventory.stock:read"))],
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends(get_pagination)],
    company_id: UUID | None = None,
    warehouse_id: UUID | None = None,
    product_id: UUID | None = None,
):
    rows = StockBalanceService(db).list_ledger(
        ctx, company_id, warehouse_id=warehouse_id, product_id=product_id
    )
    page = paginate(rows, pagination)
    return APIResponse(
        message="Stock ledger retrieved",
        data=[LedgerEntryResponse.model_validate(r) for r in page],
    )


@stock_router.get("/{balance_id}", response_model=APIResponse[StockBalanceResponse])
def get_stock(
    balance_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("inventory.stock:read"))],
    db: Annotated[Session, Depends(get_db)],
):
    row = StockBalanceService(db).get_balance(ctx, balance_id)
    return APIResponse(
        message="Stock balance retrieved",
        data=StockBalanceResponse.model_validate(row),
    )


@bins_router.get("", response_model=APIResponse[list[BinResponse]])
def list_bins(
    ctx: Annotated[TenantContext, Depends(require_permission("inventory.bin:read"))],
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends(get_pagination)],
    company_id: UUID | None = None,
    warehouse_id: UUID | None = None,
):
    rows = BinService(db).list_bins(ctx, company_id, warehouse_id)
    return APIResponse(
        message="Bins retrieved",
        data=[BinResponse.model_validate(r) for r in paginate(rows, pagination)],
    )


@bins_router.post("", response_model=APIResponse[BinResponse])
def create_bin(
    body: BinCreateRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("inventory.bin:create"))],
    db: Annotated[Session, Depends(get_db)],
):
    row = BinService(db).create_bin(ctx, **body.model_dump())
    db.commit()
    return APIResponse(message="Bin created", data=BinResponse.model_validate(row))


@bins_router.get("/{bin_id}", response_model=APIResponse[BinResponse])
def get_bin(
    bin_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("inventory.bin:read"))],
    db: Annotated[Session, Depends(get_db)],
):
    row = BinService(db).get_bin(ctx, bin_id)
    return APIResponse(message="Bin retrieved", data=BinResponse.model_validate(row))


@bins_router.patch("/{bin_id}", response_model=APIResponse[BinResponse])
def update_bin(
    bin_id: UUID,
    body: BinUpdateRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("inventory.bin:update"))],
    db: Annotated[Session, Depends(get_db)],
):
    row = BinService(db).update_bin(ctx, bin_id, **extract_update_fields(body))
    db.commit()
    return APIResponse(message="Bin updated", data=BinResponse.model_validate(row))


@batches_router.get("", response_model=APIResponse[list[BatchResponse]])
def list_batches(
    ctx: Annotated[TenantContext, Depends(require_permission("inventory.batch:read"))],
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends(get_pagination)],
    company_id: UUID | None = None,
    product_id: UUID | None = None,
):
    rows = BatchService(db).list_batches(ctx, company_id, product_id)
    return APIResponse(
        message="Batches retrieved",
        data=[BatchResponse.model_validate(r) for r in paginate(rows, pagination)],
    )


@batches_router.post("", response_model=APIResponse[BatchResponse])
def create_batch(
    body: BatchCreateRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("inventory.batch:create"))],
    db: Annotated[Session, Depends(get_db)],
):
    row = BatchService(db).create_batch(ctx, **body.model_dump())
    db.commit()
    return APIResponse(message="Batch created", data=BatchResponse.model_validate(row))


@batches_router.patch("/{batch_id}", response_model=APIResponse[BatchResponse])
def update_batch(
    batch_id: UUID,
    body: BatchUpdateRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("inventory.batch:update"))],
    db: Annotated[Session, Depends(get_db)],
):
    row = BatchService(db).update_batch(ctx, batch_id, **extract_update_fields(body))
    db.commit()
    return APIResponse(message="Batch updated", data=BatchResponse.model_validate(row))


@serials_router.get("", response_model=APIResponse[list[SerialResponse]])
def list_serials(
    ctx: Annotated[TenantContext, Depends(require_permission("inventory.serial:read"))],
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends(get_pagination)],
    company_id: UUID | None = None,
    product_id: UUID | None = None,
):
    rows = SerialService(db).list_serials(ctx, company_id, product_id)
    return APIResponse(
        message="Serials retrieved",
        data=[SerialResponse.model_validate(r) for r in paginate(rows, pagination)],
    )


@serials_router.post("", response_model=APIResponse[SerialResponse])
def create_serial(
    body: SerialCreateRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("inventory.serial:create"))],
    db: Annotated[Session, Depends(get_db)],
):
    row = SerialService(db).create_serial(ctx, **body.model_dump())
    db.commit()
    return APIResponse(message="Serial created", data=SerialResponse.model_validate(row))


@serials_router.patch("/{serial_id}", response_model=APIResponse[SerialResponse])
def update_serial(
    serial_id: UUID,
    body: SerialUpdateRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("inventory.serial:update"))],
    db: Annotated[Session, Depends(get_db)],
):
    row = SerialService(db).update_serial(ctx, serial_id, **extract_update_fields(body))
    db.commit()
    return APIResponse(message="Serial updated", data=SerialResponse.model_validate(row))


@reservations_router.get("", response_model=APIResponse[list[ReservationResponse]])
def list_reservations(
    ctx: Annotated[TenantContext, Depends(require_permission("inventory.reservation:read"))],
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends(get_pagination)],
    company_id: UUID | None = None,
):
    rows = ReservationService(db).list_reservations(ctx, company_id)
    return APIResponse(
        message="Reservations retrieved",
        data=[ReservationResponse.model_validate(r) for r in paginate(rows, pagination)],
    )


@reservations_router.post("", response_model=APIResponse[ReservationResponse])
def create_reservation(
    body: ReservationCreateRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("inventory.reservation:create"))],
    db: Annotated[Session, Depends(get_db)],
):
    data = body.model_dump()
    qty = Decimal(str(data.pop("quantity")))
    row = ReservationService(db).create_reservation(ctx, quantity=qty, **data)
    db.commit()
    return APIResponse(message="Reservation created", data=ReservationResponse.model_validate(row))


@reservations_router.post(
    "/{reservation_id}/release", response_model=APIResponse[ReservationResponse]
)
def release_reservation(
    reservation_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("inventory.reservation:release"))],
    db: Annotated[Session, Depends(get_db)],
):
    row = ReservationService(db).release(ctx, reservation_id)
    db.commit()
    return APIResponse(message="Reservation released", data=ReservationResponse.model_validate(row))


@transfers_router.get("", response_model=APIResponse[list[TransferResponse]])
def list_transfers(
    ctx: Annotated[TenantContext, Depends(require_permission("inventory.transfer:read"))],
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends(get_pagination)],
    company_id: UUID | None = None,
):
    rows = TransferService(db).list_transfers(ctx, company_id)
    return APIResponse(
        message="Transfers retrieved",
        data=[TransferResponse.model_validate(r) for r in paginate(rows, pagination)],
    )


@transfers_router.post("", response_model=APIResponse[TransferResponse])
def create_transfer(
    body: TransferCreateRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("inventory.transfer:create"))],
    db: Annotated[Session, Depends(get_db)],
):
    data = body.model_dump()
    lines = data.pop("lines", [])
    row = TransferService(db).create_transfer(ctx, lines=lines, **data)
    db.commit()
    return APIResponse(message="Transfer created", data=TransferResponse.model_validate(row))


@transfers_router.get("/{transfer_id}", response_model=APIResponse[TransferResponse])
def get_transfer(
    transfer_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("inventory.transfer:read"))],
    db: Annotated[Session, Depends(get_db)],
):
    row = TransferService(db).get_transfer(ctx, transfer_id)
    return APIResponse(message="Transfer retrieved", data=TransferResponse.model_validate(row))


def _transfer_action(db, ctx, transfer_id, action: str):
    svc = TransferService(db)
    fn = getattr(svc, action)
    row = fn(ctx, transfer_id)
    db.commit()
    return APIResponse(message=f"Transfer {action}", data=TransferResponse.model_validate(row))


@transfers_router.post("/{transfer_id}/submit", response_model=APIResponse[TransferResponse])
def submit_transfer(
    transfer_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("inventory.transfer:submit"))],
    db: Annotated[Session, Depends(get_db)],
):
    return _transfer_action(db, ctx, transfer_id, "submit")


@transfers_router.post("/{transfer_id}/approve", response_model=APIResponse[TransferResponse])
def approve_transfer(
    transfer_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("inventory.transfer:approve"))],
    db: Annotated[Session, Depends(get_db)],
):
    return _transfer_action(db, ctx, transfer_id, "approve")


@transfers_router.post("/{transfer_id}/ship", response_model=APIResponse[TransferResponse])
def ship_transfer(
    transfer_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("inventory.transfer:ship"))],
    db: Annotated[Session, Depends(get_db)],
):
    return _transfer_action(db, ctx, transfer_id, "ship")


@transfers_router.post("/{transfer_id}/receive", response_model=APIResponse[TransferResponse])
def receive_transfer(
    transfer_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("inventory.transfer:receive"))],
    db: Annotated[Session, Depends(get_db)],
):
    return _transfer_action(db, ctx, transfer_id, "receive")


@adjustments_router.get("", response_model=APIResponse[list[AdjustmentResponse]])
def list_adjustments(
    ctx: Annotated[TenantContext, Depends(require_permission("inventory.adjustment:read"))],
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends(get_pagination)],
    company_id: UUID | None = None,
):
    rows = AdjustmentService(db).list_adjustments(ctx, company_id)
    return APIResponse(
        message="Adjustments retrieved",
        data=[AdjustmentResponse.model_validate(r) for r in paginate(rows, pagination)],
    )


@adjustments_router.post("", response_model=APIResponse[AdjustmentResponse])
def create_adjustment(
    body: AdjustmentCreateRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("inventory.adjustment:create"))],
    db: Annotated[Session, Depends(get_db)],
):
    data = body.model_dump()
    lines = data.pop("lines", [])
    row = AdjustmentService(db).create_adjustment(ctx, lines=lines, **data)
    db.commit()
    return APIResponse(message="Adjustment created", data=AdjustmentResponse.model_validate(row))


@adjustments_router.post("/{adjustment_id}/submit", response_model=APIResponse[AdjustmentResponse])
def submit_adjustment(
    adjustment_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("inventory.adjustment:submit"))],
    db: Annotated[Session, Depends(get_db)],
):
    row = AdjustmentService(db).submit(ctx, adjustment_id)
    db.commit()
    return APIResponse(message="Adjustment submitted", data=AdjustmentResponse.model_validate(row))


@adjustments_router.post("/{adjustment_id}/approve", response_model=APIResponse[AdjustmentResponse])
def approve_adjustment(
    adjustment_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("inventory.adjustment:approve"))],
    db: Annotated[Session, Depends(get_db)],
):
    row = AdjustmentService(db).approve(ctx, adjustment_id)
    db.commit()
    return APIResponse(message="Adjustment approved", data=AdjustmentResponse.model_validate(row))


@adjustments_router.post("/{adjustment_id}/post", response_model=APIResponse[AdjustmentResponse])
def post_adjustment(
    adjustment_id: UUID,
    body: AdjustmentPostRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("inventory.adjustment:post"))],
    db: Annotated[Session, Depends(get_db)],
):
    row = AdjustmentService(db).post(ctx, adjustment_id, **body.model_dump())
    db.commit()
    return APIResponse(message="Adjustment posted", data=AdjustmentResponse.model_validate(row))


@cycle_counts_router.get("", response_model=APIResponse[list[CycleCountResponse]])
def list_cycle_counts(
    ctx: Annotated[TenantContext, Depends(require_permission("inventory.cycle_count:read"))],
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends(get_pagination)],
    company_id: UUID | None = None,
):
    rows = CycleCountService(db).list_counts(ctx, company_id)
    return APIResponse(
        message="Cycle counts retrieved",
        data=[CycleCountResponse.model_validate(r) for r in paginate(rows, pagination)],
    )


@cycle_counts_router.post("", response_model=APIResponse[CycleCountResponse])
def create_cycle_count(
    body: CycleCountCreateRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("inventory.cycle_count:create"))],
    db: Annotated[Session, Depends(get_db)],
):
    data = body.model_dump()
    lines = data.pop("lines", [])
    row = CycleCountService(db).create_count(ctx, lines=lines, **data)
    db.commit()
    return APIResponse(message="Cycle count created", data=CycleCountResponse.model_validate(row))


@cycle_counts_router.post("/{count_id}/submit", response_model=APIResponse[CycleCountResponse])
def submit_cycle_count(
    count_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("inventory.cycle_count:submit"))],
    db: Annotated[Session, Depends(get_db)],
):
    row = CycleCountService(db).submit(ctx, count_id)
    db.commit()
    return APIResponse(message="Cycle count submitted", data=CycleCountResponse.model_validate(row))


@cycle_counts_router.post("/{count_id}/approve", response_model=APIResponse[CycleCountResponse])
def approve_cycle_count(
    count_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("inventory.cycle_count:approve"))],
    db: Annotated[Session, Depends(get_db)],
):
    row = CycleCountService(db).approve(ctx, count_id)
    db.commit()
    return APIResponse(message="Cycle count approved", data=CycleCountResponse.model_validate(row))


@cycle_counts_router.post("/{count_id}/post", response_model=APIResponse[CycleCountResponse])
def post_cycle_count(
    count_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("inventory.cycle_count:post"))],
    db: Annotated[Session, Depends(get_db)],
):
    row = CycleCountService(db).post(ctx, count_id)
    db.commit()
    return APIResponse(message="Cycle count posted", data=CycleCountResponse.model_validate(row))


@policies_router.get("", response_model=APIResponse[list[ReorderPolicyResponse]])
def list_policies(
    ctx: Annotated[TenantContext, Depends(require_permission("inventory.reorder_policy:read"))],
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends(get_pagination)],
    company_id: UUID | None = None,
):
    rows = ReorderPolicyService(db).list_policies(ctx, company_id)
    return APIResponse(
        message="Policies retrieved",
        data=[ReorderPolicyResponse.model_validate(r) for r in paginate(rows, pagination)],
    )


@policies_router.post("", response_model=APIResponse[ReorderPolicyResponse])
def create_policy(
    body: ReorderPolicyCreateRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("inventory.reorder_policy:create"))],
    db: Annotated[Session, Depends(get_db)],
):
    row = ReorderPolicyService(db).create_policy(ctx, **body.model_dump())
    db.commit()
    return APIResponse(message="Policy created", data=ReorderPolicyResponse.model_validate(row))


@policies_router.patch("/{policy_id}", response_model=APIResponse[ReorderPolicyResponse])
def update_policy(
    policy_id: UUID,
    body: ReorderPolicyUpdateRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("inventory.reorder_policy:update"))],
    db: Annotated[Session, Depends(get_db)],
):
    row = ReorderPolicyService(db).update_policy(ctx, policy_id, **extract_update_fields(body))
    db.commit()
    return APIResponse(message="Policy updated", data=ReorderPolicyResponse.model_validate(row))


@valuation_router.get("/layers", response_model=APIResponse[list[ValuationLayerResponse]])
def list_layers(
    ctx: Annotated[TenantContext, Depends(require_permission("inventory.valuation:read"))],
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends(get_pagination)],
    company_id: UUID | None = None,
    warehouse_id: UUID | None = None,
):
    rows = ValuationService(db).list_layers(ctx, company_id, warehouse_id)
    return APIResponse(
        message="Valuation layers retrieved",
        data=[ValuationLayerResponse.model_validate(r) for r in paginate(rows, pagination)],
    )


@valuation_router.post("/run", response_model=APIResponse[ValuationRunResponse])
def run_valuation(
    ctx: Annotated[TenantContext, Depends(require_permission("inventory.valuation:run"))],
    db: Annotated[Session, Depends(get_db)],
    company_id: UUID | None = None,
):
    result = ValuationService(db).run_valuation(ctx, company_id)
    return APIResponse(message="Valuation run complete", data=ValuationRunResponse(**result))


@reports_router.get("/stock-summary", response_model=APIResponse[ReportSummaryResponse])
def stock_summary_report(
    ctx: Annotated[TenantContext, Depends(require_permission("inventory.report:read"))],
    db: Annotated[Session, Depends(get_db)],
    company_id: UUID | None = None,
):
    rows = StockBalanceService(db).list_stock(ctx, company_id)
    data = [
        {
            "product_id": str(r.product_id),
            "warehouse_id": str(r.warehouse_id),
            "on_hand_qty": float(r.on_hand_qty),
            "available_qty": float(r.available_qty),
        }
        for r in rows
    ]
    return APIResponse(
        message="Stock summary",
        data=ReportSummaryResponse(name="stock-summary", row_count=len(data), rows=data),
    )


@reports_router.get("/batch-expiry", response_model=APIResponse[ReportSummaryResponse])
def batch_expiry_report(
    ctx: Annotated[TenantContext, Depends(require_permission("inventory.report:read"))],
    db: Annotated[Session, Depends(get_db)],
    company_id: UUID | None = None,
):
    rows = BatchService(db).list_batches(ctx, company_id)
    data = [
        {
            "batch_id": str(r.id),
            "product_id": str(r.product_id),
            "expiry_date": str(r.expiry_date) if r.expiry_date else None,
            "status": r.status,
        }
        for r in rows
        if r.expiry_date is not None
    ]
    return APIResponse(
        message="Batch expiry",
        data=ReportSummaryResponse(name="batch-expiry", row_count=len(data), rows=data),
    )
