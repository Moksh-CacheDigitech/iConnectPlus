"""Stock accountability: who owns each unit, how old it is, and what it costs to hold.

Every unit received against a CRM OVF is tagged to the salesperson who owns
that deal. Stock sits "owned" until the owner releases it (or the deal closes
/ is lost), after which it is open for anyone to sell. Other salespeople can
request owned stock; the owner accepts and accountability moves with it.
Carrying cost (1% a month on purchase cost) flows back into the OVF margin.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from core.exceptions import ConflictException, ForbiddenException, NotFoundException
from modules.crm.service.engines.margin_engine import carrying_cost
from modules.foundation.domain.value_objects import TenantContext
from modules.foundation.service.notification_service import NotificationService
from modules.procurement.adapters.crm_adapter import ProcurementCrmAdapter
from modules.procurement.adapters.master_data_adapter import ProcurementMasterDataAdapter
from modules.procurement.models.inventory_import import ProcInventoryImportLine
from modules.procurement.models.inventory_stock import ProcInventoryStockUnit
from modules.procurement.models.inventory_transfer import ProcInventoryTransferRequest
from modules.procurement.models.order import ProcOrderLine
from modules.procurement.service.procurement_scope_validator import ProcurementScopeValidator

AGING_BUCKETS: tuple[tuple[str, int, int | None], ...] = (
    ("0-30", 0, 30),
    ("31-90", 31, 90),
    ("91-180", 91, 180),
    ("181-365", 181, 365),
    ("365+", 366, None),
)
TARGET_MAX_AGE_DAYS = 30


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _as_date(value: Any) -> date | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date()
    return value


def aging_bucket(age_days: int) -> str:
    for label, low, high in AGING_BUCKETS:
        if age_days >= low and (high is None or age_days <= high):
            return label
    return AGING_BUCKETS[-1][0]


class InventoryOwnershipService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._scope = ProcurementScopeValidator(db)
        self._crm = ProcurementCrmAdapter(db)
        self._master = ProcurementMasterDataAdapter(db)

    def _company(self, ctx: TenantContext, company_id: UUID | None) -> UUID:
        cid = self._scope.resolve_company_id(ctx, company_id)
        if cid is None:
            raise ForbiddenException("Company context required")
        return cid

    # -- tagging at GRN ---------------------------------------------------
    def owner_for_order(self, ctx: TenantContext, order) -> tuple[UUID | None, UUID | None]:
        """(owner employee, source OVF) for a PO raised from a CRM OVF."""
        if getattr(order, "source_module", None) != "crm" or getattr(order, "source_document_type", None) != "ovf":
            return None, None
        ovf_id = getattr(order, "source_document_id", None)
        if ovf_id is None:
            return None, None
        return self._crm.get_ovf_owner_employee_id(ctx, ovf_id), ovf_id

    # -- ledger -------------------------------------------------------------
    def _on_hand(self, ctx: TenantContext, company_id: UUID | None) -> list[dict[str, Any]]:
        """``company_id=None`` reads the whole tenant (background jobs only)."""
        unit_stmt = select(ProcInventoryStockUnit).where(
            ProcInventoryStockUnit.tenant_id == ctx.tenant_id,
            ProcInventoryStockUnit.is_deleted.is_(False),
        )
        import_stmt = select(ProcInventoryImportLine).where(
            ProcInventoryImportLine.tenant_id == ctx.tenant_id,
            ProcInventoryImportLine.is_deleted.is_(False),
        )
        if company_id is not None:
            unit_stmt = unit_stmt.where(ProcInventoryStockUnit.company_id == company_id)
            import_stmt = import_stmt.where(ProcInventoryImportLine.company_id == company_id)
        units = list(self._db.scalars(unit_stmt).all())
        line_ids = list({u.order_line_id for u in units})
        cost_by_line: dict[UUID, Decimal] = {}
        if line_ids:
            for line in self._db.scalars(select(ProcOrderLine).where(ProcOrderLine.id.in_(line_ids))).all():
                cost_by_line[line.id] = Decimal(str(line.unit_cost or 0))
        rows: list[dict[str, Any]] = []
        for unit in units:
            qty = Decimal(str(unit.quantity or 1))
            rows.append(
                {
                    "kind": "stock_unit",
                    "id": unit.id,
                    "product_name": unit.product_name,
                    "serial_number": unit.serial_number,
                    "received_on": _as_date(unit.receipt_at),
                    "quantity": qty,
                    "unit_cost": cost_by_line.get(unit.order_line_id, Decimal("0")) * qty,
                    "warranty_valid_till": unit.warranty_valid_till,
                    "owner_employee_id": unit.owner_employee_id,
                    "source_ovf_id": unit.source_ovf_id,
                    "open_for_sale": bool(unit.open_for_sale),
                    "row": unit,
                }
            )
        for line in self._db.scalars(import_stmt).all():
            rows.append(
                {
                    "kind": "import_line",
                    "id": line.id,
                    "product_name": line.product_name,
                    "serial_number": line.serial_number,
                    "received_on": line.received_on or _as_date(line.created_at),
                    "quantity": Decimal("1"),
                    "unit_cost": Decimal(str(line.unit_cost or 0)),
                    "warranty_valid_till": line.warranty_valid_till,
                    "owner_employee_id": line.owner_employee_id,
                    "source_ovf_id": line.source_ovf_id,
                    "open_for_sale": bool(line.open_for_sale),
                    "row": line,
                }
            )
        return rows

    def _enrich(self, ctx: TenantContext, rows: list[dict[str, Any]], as_of: date) -> list[dict[str, Any]]:
        names = self._master.employee_names(ctx, [r["owner_employee_id"] for r in rows])
        out = []
        for r in rows:
            received = r["received_on"] or as_of
            age = max((as_of - received).days, 0)
            holding = carrying_cost(r["unit_cost"], age)
            warranty = r["warranty_valid_till"]
            out.append(
                {
                    **{k: v for k, v in r.items() if k != "row"},
                    "owner_name": names.get(r["owner_employee_id"]) if r["owner_employee_id"] else None,
                    "age_days": age,
                    "aging_bucket": aging_bucket(age),
                    "holding_cost": holding,
                    "current_value": (r["unit_cost"] + holding).quantize(Decimal("0.0001")),
                    "warranty_expired": bool(warranty and warranty < as_of),
                    "warranty_days_left": (warranty - as_of).days if warranty else None,
                    "status": "open_for_sale" if r["open_for_sale"] or not r["owner_employee_id"] else "owned",
                }
            )
        return out

    def list_units(self, ctx: TenantContext, company_id: UUID | None = None) -> list[dict[str, Any]]:
        """Organisation-wide stock list with owner, age, warranty and today's value."""
        cid = self._company(ctx, company_id)
        rows = self._enrich(ctx, self._on_hand(ctx, cid), date.today())
        rows.sort(key=lambda r: r["age_days"], reverse=True)
        return rows

    def aging_report(self, ctx: TenantContext, company_id: UUID | None = None) -> dict[str, Any]:
        cid = self._company(ctx, company_id)
        today = date.today()
        rows = self._enrich(ctx, self._on_hand(ctx, cid), today)

        def blank() -> dict[str, Any]:
            return {"units": Decimal("0"), "value": Decimal("0"), "holding_cost": Decimal("0")}

        buckets = {label: blank() for label, _l, _h in AGING_BUCKETS}
        by_owner: dict[UUID | None, dict[str, Any]] = defaultdict(blank)
        by_product: dict[str, dict[str, Any]] = defaultdict(blank)
        total = blank()
        over_target = blank()
        warranty_expired = 0
        for r in rows:
            for bucket in (buckets[r["aging_bucket"]], by_owner[r["owner_employee_id"]], by_product[r["product_name"]], total):
                bucket["units"] += r["quantity"]
                bucket["value"] += r["unit_cost"]
                bucket["holding_cost"] += r["holding_cost"]
            if r["age_days"] > TARGET_MAX_AGE_DAYS:
                over_target["units"] += r["quantity"]
                over_target["value"] += r["unit_cost"]
                over_target["holding_cost"] += r["holding_cost"]
            if r["warranty_expired"]:
                warranty_expired += 1

        names = self._master.employee_names(ctx, [oid for oid in by_owner if oid is not None])
        oldest_by_owner: dict[UUID | None, int] = defaultdict(int)
        for r in rows:
            oldest_by_owner[r["owner_employee_id"]] = max(oldest_by_owner[r["owner_employee_id"]], r["age_days"])
        return {
            "as_of": today,
            "target_max_age_days": TARGET_MAX_AGE_DAYS,
            "total": total,
            "over_target": over_target,
            "warranty_expired_units": warranty_expired,
            "buckets": [{"bucket": label, **buckets[label]} for label, _l, _h in AGING_BUCKETS],
            "by_owner": sorted(
                (
                    {
                        "owner_employee_id": oid,
                        "owner_name": names.get(oid, "Unassigned / open for sale") if oid else "Unassigned / open for sale",
                        "oldest_age_days": oldest_by_owner[oid],
                        **vals,
                    }
                    for oid, vals in by_owner.items()
                ),
                key=lambda item: item["value"],
                reverse=True,
            ),
            "by_product": sorted(
                ({"product_name": name, **vals} for name, vals in by_product.items()),
                key=lambda item: item["value"],
                reverse=True,
            )[:50],
        }

    def suggest_stock(self, ctx: TenantContext, query: str, company_id: UUID | None = None) -> list[dict[str, Any]]:
        """Before ordering fresh, show matching units on hand at today's value."""
        text = (query or "").strip().lower()
        if len(text) < 2:
            return []
        tokens = [t for t in text.split() if len(t) > 1]
        rows = self.list_units(ctx, company_id)
        return [r for r in rows if all(t in (r["product_name"] or "").lower() for t in tokens)][:100]

    # -- ownership changes ----------------------------------------------------
    def _load(self, ctx: TenantContext, stock_unit_ids: list[UUID], import_line_ids: list[UUID]):
        cid = self._company(ctx, None)
        units = []
        if stock_unit_ids:
            units = list(
                self._db.scalars(
                    select(ProcInventoryStockUnit).where(
                        ProcInventoryStockUnit.id.in_(stock_unit_ids),
                        ProcInventoryStockUnit.tenant_id == ctx.tenant_id,
                        ProcInventoryStockUnit.company_id == cid,
                        ProcInventoryStockUnit.is_deleted.is_(False),
                    )
                ).all()
            )
        imports = []
        if import_line_ids:
            imports = list(
                self._db.scalars(
                    select(ProcInventoryImportLine).where(
                        ProcInventoryImportLine.id.in_(import_line_ids),
                        ProcInventoryImportLine.tenant_id == ctx.tenant_id,
                        ProcInventoryImportLine.company_id == cid,
                        ProcInventoryImportLine.is_deleted.is_(False),
                    )
                ).all()
            )
        if len(units) != len(set(stock_unit_ids)) or len(imports) != len(set(import_line_ids)):
            raise NotFoundException("Some selected stock is no longer on hand. Refresh inventory and try again.")
        if not units and not imports:
            raise ConflictException("Select at least one stock unit")
        return cid, units + imports

    def assign_owner(
        self,
        ctx: TenantContext,
        *,
        owner_employee_id: UUID | None,
        stock_unit_ids: list[UUID],
        import_line_ids: list[UUID],
    ) -> int:
        """SCM tags legacy / imported stock to the salesperson accountable for it."""
        _cid, rows = self._load(ctx, stock_unit_ids, import_line_ids)
        now = _utcnow()
        for row in rows:
            row.owner_employee_id = owner_employee_id
            row.owner_assigned_at = now if owner_employee_id else None
            row.open_for_sale = owner_employee_id is None
            row.open_for_sale_at = now if owner_employee_id is None else None
            row.updated_by = ctx.user_id
            row.updated_at = now
        self._db.flush()
        return len(rows)

    def set_open_for_sale(
        self,
        ctx: TenantContext,
        *,
        open_for_sale: bool,
        stock_unit_ids: list[UUID],
        import_line_ids: list[UUID],
        is_scm_admin: bool = False,
    ) -> int:
        """The owner posts that their PO is done - the stock is now open to everyone."""
        _cid, rows = self._load(ctx, stock_unit_ids, import_line_ids)
        me = self._master.employee_id_for_user(ctx, ctx.user_id)
        now = _utcnow()
        for row in rows:
            if not is_scm_admin and row.owner_employee_id not in (None, me):
                raise ForbiddenException("Only the stock owner (or SCM) can release it for sale")
            row.open_for_sale = bool(open_for_sale)
            row.open_for_sale_at = now if open_for_sale else None
            row.updated_by = ctx.user_id
            row.updated_at = now
        self._db.flush()
        return len(rows)

    # -- transfer requests --------------------------------------------------
    def list_transfers(self, ctx: TenantContext, *, mine_only: bool = True) -> list[ProcInventoryTransferRequest]:
        cid = self._company(ctx, None)
        stmt = select(ProcInventoryTransferRequest).where(
            ProcInventoryTransferRequest.tenant_id == ctx.tenant_id,
            ProcInventoryTransferRequest.company_id == cid,
            ProcInventoryTransferRequest.is_deleted.is_(False),
        )
        if mine_only:
            me = self._master.employee_id_for_user(ctx, ctx.user_id)
            if me is None:
                return []
            stmt = stmt.where(
                (ProcInventoryTransferRequest.requester_employee_id == me)
                | (ProcInventoryTransferRequest.owner_employee_id == me)
            )
        return list(self._db.scalars(stmt.order_by(ProcInventoryTransferRequest.created_at.desc())).all())

    def request_transfer(
        self,
        ctx: TenantContext,
        *,
        stock_unit_ids: list[UUID],
        import_line_ids: list[UUID],
        customer_note: str | None = None,
    ) -> ProcInventoryTransferRequest:
        me = self._master.employee_id_for_user(ctx, ctx.user_id)
        if me is None:
            raise ConflictException("Your login is not linked to an employee - ask an admin to link it")
        cid, rows = self._load(ctx, stock_unit_ids, import_line_ids)
        owners = {row.owner_employee_id for row in rows}
        if len(owners) != 1:
            raise ConflictException("Request stock from one owner at a time")
        owner = next(iter(owners))
        if owner is None or all(bool(row.open_for_sale) for row in rows):
            raise ConflictException("This stock is already open for sale - use it directly on your OVF")
        if owner == me:
            raise ConflictException("You already own this stock")
        products = sorted({row.product_name for row in rows})
        request = ProcInventoryTransferRequest(
            requester_employee_id=me,
            owner_employee_id=owner,
            product_name=", ".join(products)[:255],
            quantity=sum((Decimal(str(getattr(row, "quantity", 1) or 1)) for row in rows), Decimal("0")),
            stock_unit_ids=[str(uid) for uid in stock_unit_ids],
            import_line_ids=[str(uid) for uid in import_line_ids],
            customer_note=(customer_note or "").strip() or None,
            status="pending",
            tenant_id=ctx.tenant_id,
            company_id=cid,
            branch_id=rows[0].branch_id,
            created_by=ctx.user_id,
            updated_by=ctx.user_id,
        )
        self._db.add(request)
        self._db.flush()
        names = self._master.employee_names(ctx, [me])
        self._notify(
            ctx,
            self._master.employee_user_id(ctx, owner),
            title="Stock requested from your inventory",
            body=(
                f"{names.get(me, 'A colleague')} wants {request.quantity.normalize():f} x {request.product_name}"
                f"{f' for: {request.customer_note}' if request.customer_note else ''}. Accept to hand it over."
            ),
            entity_id=request.id,
        )
        return request

    def decide_transfer(
        self,
        ctx: TenantContext,
        request_id: UUID,
        *,
        accept: bool,
        remark: str | None = None,
        is_scm_admin: bool = False,
    ) -> ProcInventoryTransferRequest:
        request = self._db.get(ProcInventoryTransferRequest, request_id)
        if request is None or request.is_deleted or request.tenant_id != ctx.tenant_id:
            raise NotFoundException("Transfer request not found")
        if request.status != "pending":
            raise ConflictException("This request is already decided")
        me = self._master.employee_id_for_user(ctx, ctx.user_id)
        if request.owner_employee_id != me and not is_scm_admin:
            raise ForbiddenException("Only the current stock owner can accept or reject this request")
        now = _utcnow()
        if accept:
            stock_ids = [UUID(v) for v in (request.stock_unit_ids or [])]
            import_ids = [UUID(v) for v in (request.import_line_ids or [])]
            _cid, rows = self._load(ctx, stock_ids, import_ids)
            for row in rows:
                if row.owner_employee_id != request.owner_employee_id:
                    raise ConflictException("Some of this stock has changed hands - ask for a fresh request")
                row.owner_employee_id = request.requester_employee_id
                row.owner_assigned_at = now
                row.open_for_sale = False
                row.open_for_sale_at = None
                row.updated_by = ctx.user_id
                row.updated_at = now
        request.status = "accepted" if accept else "rejected"
        request.decided_at = now
        request.decided_by = ctx.user_id
        request.decision_remark = (remark or "").strip() or None
        request.updated_by = ctx.user_id
        request.updated_at = now
        self._db.flush()
        self._notify(
            ctx,
            self._master.employee_user_id(ctx, request.requester_employee_id),
            title=f"Stock request {'accepted' if accept else 'rejected'}",
            body=(
                f"Your request for {request.product_name} was {'accepted - the stock is now yours' if accept else 'rejected'}"
                f"{f': {request.decision_remark}' if request.decision_remark else '.'}"
            ),
            entity_id=request.id,
        )
        return request

    def _notify(self, ctx: TenantContext, user_id: UUID | None, *, title: str, body: str, entity_id: UUID) -> None:
        if user_id is None:
            return
        notif = NotificationService(self._db)
        tpl = notif.get_or_create_template(
            tenant_id=ctx.tenant_id,
            template_code="procurement.inventory_transfer",
            template_name="Inventory transfer request",
            channel="in_app",
            subject_template="{{title}}",
            body_template="{{body}}",
            created_by=ctx.user_id,
        )
        notif.send(
            tenant_id=ctx.tenant_id,
            template_id=tpl.id,
            event_type="procurement.inventory_transfer",
            recipient_user_id=user_id,
            recipient_address=None,
            payload_json={
                "title": title,
                "body": body,
                "entity_type": "inventory_transfer",
                "entity_id": str(entity_id),
                "href": "/procurement/inventory",
            },
            created_by=ctx.user_id,
        )

    # -- nightly ------------------------------------------------------------
    def release_closed_deal_stock(self, ctx: TenantContext) -> int:
        """Leftover stock of a closed or lost deal becomes open for sale to everyone."""
        released = 0
        for model in (ProcInventoryStockUnit, ProcInventoryImportLine):
            rows = list(
                self._db.scalars(
                    select(model).where(
                        model.tenant_id == ctx.tenant_id,
                        model.is_deleted.is_(False),
                        model.open_for_sale.is_(False),
                        model.source_ovf_id.is_not(None),
                    )
                ).all()
            )
            states = self._crm.get_ovf_release_states(ctx, [r.source_ovf_id for r in rows])
            now = _utcnow()
            for row in rows:
                if states.get(row.source_ovf_id):
                    row.open_for_sale = True
                    row.open_for_sale_at = now
                    released += 1
        self._db.flush()
        return released

    def push_holding_costs(self, ctx: TenantContext) -> int:
        """Carrying cost of units still on hand, per source OVF, into the OVF live margin."""
        today = date.today()
        per_ovf: dict[UUID, Decimal] = defaultdict(Decimal)
        for r in self._enrich(ctx, self._on_hand(ctx, None), today):
            if r["source_ovf_id"] is not None:
                per_ovf[r["source_ovf_id"]] += r["holding_cost"]
        for ovf_id, amount in per_ovf.items():
            try:
                self._crm.set_ovf_holding_cost(ctx, ovf_id, amount)
            except NotFoundException:
                continue
        return len(per_ovf)
