"""Create and complete Accounts invoice generation tasks from Billing GRNs."""

from __future__ import annotations

from datetime import date, datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy.orm import Session, selectinload

from core.exceptions import ConflictException, ForbiddenException, NotFoundException
from modules.foundation.domain.value_objects import TenantContext
from modules.foundation.repository.user_repository import UserRepository
from modules.procurement.models.invoice_generation_task import ProcInvoiceGenerationTask
from modules.procurement.models.order import ProcOrderHeader, ProcOrderLine
from modules.procurement.models.receipt_batch import ProcOrderReceiptBatch
from modules.procurement.repository.invoice_generation_task_repository import (
    ProcInvoiceGenerationTaskRepository,
)
from modules.procurement.service.approval_step_owner_service import ProcApprovalStepOwnerService
from modules.procurement.service.procurement_module_admin import ProcurementModuleAdminService

INVOICE_STEP_KEY = "invoice_generation"


class ProcInvoiceGenerationTaskService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._repo = ProcInvoiceGenerationTaskRepository(db)
        self._owners = ProcApprovalStepOwnerService(db)
        self._admin = ProcurementModuleAdminService(db)
        self._users = UserRepository(db)

    def _resolve_user_names(
        self, tenant_id: UUID, user_ids: set[UUID]
    ) -> dict[UUID, str]:
        names: dict[UUID, str] = {}
        for user_id in user_ids:
            if user_id is None:
                continue
            user = self._users.get_by_id(tenant_id, user_id)
            if user and user.display_name:
                names[user_id] = user.display_name
        return names

    def create_for_billing_receipt(
        self,
        ctx: TenantContext,
        *,
        order_id: UUID,
        receipt_batch_id: UUID,
        items_summary: str = "",
        vendor_name: str = "",
        customer_name: str = "",
    ) -> list[ProcInvoiceGenerationTask]:
        order = self._db.get(ProcOrderHeader, order_id)
        if order is None or order.is_deleted or order.tenant_id != ctx.tenant_id:
            raise NotFoundException("Purchase order not found")

        batch = self._db.get(ProcOrderReceiptBatch, receipt_batch_id)
        if (
            batch is None
            or batch.is_deleted
            or batch.tenant_id != ctx.tenant_id
            or batch.order_header_id != order_id
        ):
            raise NotFoundException("Receipt batch not found")

        owner_ids = self._owners.list_user_ids(ctx, INVOICE_STEP_KEY)
        if not owner_ids:
            raise ConflictException(
                "No Invoice generation approvers configured. Assign Accounts users under Approvers."
            )

        po_number = (order.company_po_number or order.document_number or "").strip()
        grn_number = (batch.grn_number or order.current_grn_number or "").strip()
        title = f"Invoice generation · {grn_number or po_number or 'GRN'}"
        summary = (items_summary or "").strip()[:500]
        vendor = (vendor_name or "").strip()[:255]
        customer = (customer_name or "").strip()[:255]
        company_id = order.company_id
        branch_id = order.branch_id
        if company_id is None or branch_id is None:
            raise ConflictException("Purchase order is missing company/branch scope")

        created: list[ProcInvoiceGenerationTask] = []
        for user_id in owner_ids:
            existing = self._repo.find_for_batch_assignee(
                ctx,
                receipt_batch_id=receipt_batch_id,
                assigned_user_id=user_id,
            )
            if existing is not None:
                created.append(existing)
                continue
            short = str(uuid4()).replace("-", "")[:8].upper()
            row = ProcInvoiceGenerationTask(
                id=uuid4(),
                tenant_id=ctx.tenant_id,
                company_id=company_id,
                branch_id=branch_id,
                task_code=f"INV-{short}",
                title=title,
                status="pending",
                order_header_id=order_id,
                receipt_batch_id=receipt_batch_id,
                grn_number=grn_number[:80],
                purchase_order_number=po_number[:100],
                vendor_name=vendor,
                customer_name=customer,
                items_summary=summary,
                assigned_user_id=user_id,
                requested_by=ctx.user_id,
                created_by=ctx.user_id,
                updated_by=ctx.user_id,
            )
            created.append(self._repo.add(row))

        if created:
            self._notify_assignees(
                ctx,
                order=order,
                tasks=created,
                po_number=po_number,
            )
        return created

    def _po_print_email_attachments(
        self, ctx: TenantContext, order_id: UUID
    ) -> list[dict]:
        import base64

        from modules.crm.service.attachment_service import AttachmentService
        from modules.procurement.adapters.crm_adapter import ProcurementCrmAdapter

        attachment_svc = AttachmentService(self._db)
        rows = ProcurementCrmAdapter(self._db).list_attachments(
            ctx,
            entity_filters=[("purchase_order", order_id)],
        )
        preferred = sorted(
            rows,
            key=lambda row: 0 if (row.category or "").lower() == "po_pdf" else 1,
        )
        for row in preferred:
            name = (row.file_name or "").lower()
            ctype = (row.content_type or "").lower()
            if "pdf" not in ctype and not name.endswith(".pdf"):
                continue
            try:
                download = attachment_svc.resolve_download(ctx, row.id)
            except Exception:  # noqa: BLE001
                continue
            raw = download.content
            if raw is None and download.path is not None:
                raw = download.path.read_bytes()
            if not raw:
                continue
            return [
                {
                    "filename": row.file_name or "Purchase_Order.pdf",
                    "content_base64": base64.b64encode(raw).decode("ascii"),
                    "content_type": row.content_type or "application/pdf",
                }
            ]
        return []

    def _notify_assignees(
        self,
        ctx: TenantContext,
        *,
        order: ProcOrderHeader,
        tasks: list[ProcInvoiceGenerationTask],
        po_number: str,
    ) -> None:
        from modules.procurement.domain.approval_step_owners import APPROVAL_STEP_CATALOG
        from modules.procurement.service.proc_email_notification_service import (
            ProcEmailNotificationService,
        )

        label, _team = APPROVAL_STEP_CATALOG.get(
            INVOICE_STEP_KEY, ("Invoice generation", "accounts")
        )
        attachments = self._po_print_email_attachments(ctx, order.id)
        recipient_ids = [task.assigned_user_id for task in tasks if task.assigned_user_id]
        try:
            ProcEmailNotificationService(self._db).notify_step_approvers(
                tenant_id=ctx.tenant_id,
                recipient_user_ids=recipient_ids,
                approval_type=label,
                record_title=f"{label} · {po_number or 'PO'}",
                requested_by=ctx.user_id,
                remarks="Billing GRN saved — fill invoice details in My Jobs",
                jobs_path="/procurement/my-jobs",
                attachments=attachments or None,
            )
        except Exception:  # noqa: BLE001
            pass

    def list_my_tasks(
        self,
        ctx: TenantContext,
        *,
        status: str | None = "pending",
    ) -> list[ProcInvoiceGenerationTask]:
        if ctx.user_id is None:
            return []
        return self._repo.list_for_assignee(ctx, user_id=ctx.user_id, status=status)

    def get_for_batch_prefill(
        self,
        ctx: TenantContext,
        *,
        receipt_batch_id: UUID,
    ) -> ProcInvoiceGenerationTask | None:
        rows = self._repo.list_for_batch(ctx, receipt_batch_id=receipt_batch_id)
        completed = [row for row in rows if row.status == "completed"]
        if completed:
            return completed[0]
        return None

    def billing_totals_for_batch(
        self,
        ctx: TenantContext,
        *,
        order_id: UUID,
        receipt_batch_id: UUID,
    ) -> tuple[float, float]:
        """Sum Billing disposition qty and amount from the SCM GRN batch."""
        batch = (
            self._db.query(ProcOrderReceiptBatch)
            .options(selectinload(ProcOrderReceiptBatch.lines))
            .filter(
                ProcOrderReceiptBatch.id == receipt_batch_id,
                ProcOrderReceiptBatch.tenant_id == ctx.tenant_id,
                ProcOrderReceiptBatch.is_deleted.is_(False),
            )
            .first()
        )
        if batch is None or batch.order_header_id != order_id:
            return 0.0, 0.0

        batch_lines = [
            ln
            for ln in (batch.lines or [])
            if not getattr(ln, "is_deleted", False)
        ]
        if not batch_lines:
            return 0.0, 0.0

        order_line_ids = [ln.order_line_id for ln in batch_lines]
        order_lines = (
            self._db.query(ProcOrderLine)
            .filter(
                ProcOrderLine.id.in_(order_line_ids),
                ProcOrderLine.tenant_id == ctx.tenant_id,
                ProcOrderLine.is_deleted.is_(False),
            )
            .all()
        )
        by_id = {ln.id: ln for ln in order_lines}

        qty_total = 0.0
        amount_total = 0.0
        for bl in batch_lines:
            bill_qty = float(getattr(bl, "billing_quantity", 0) or 0)
            if bill_qty <= 1e-9 and getattr(bl, "billing", True):
                # Older batches may only flip billing without a split qty.
                bill_qty = float(getattr(bl, "quantity", 0) or 0)
            if bill_qty <= 1e-9:
                continue
            qty_total += bill_qty
            ol = by_id.get(bl.order_line_id)
            if ol is None:
                continue
            ordered = float(getattr(ol, "quantity", 0) or 0)
            line_total = float(getattr(ol, "line_total", 0) or 0)
            unit_cost = float(getattr(ol, "unit_cost", 0) or 0)
            unit_net = (line_total / ordered) if ordered > 1e-9 else unit_cost
            amount_total += bill_qty * unit_net

        return round(qty_total, 4), round(amount_total, 4)

    def serialize(
        self,
        ctx: TenantContext,
        row: ProcInvoiceGenerationTask,
        *,
        requester_names: dict[UUID, str] | None = None,
    ) -> dict:
        suggested_qty, suggested_amount = self.billing_totals_for_batch(
            ctx,
            order_id=row.order_header_id,
            receipt_batch_id=row.receipt_batch_id,
        )
        requester_id = getattr(row, "requested_by", None) or getattr(row, "created_by", None)
        names = requester_names
        if names is None and requester_id is not None:
            names = self._resolve_user_names(ctx.tenant_id, {requester_id})
        return {
            "id": row.id,
            "task_code": row.task_code,
            "title": row.title,
            "status": row.status,
            "order_header_id": row.order_header_id,
            "receipt_batch_id": row.receipt_batch_id,
            "grn_number": row.grn_number or "",
            "purchase_order_number": row.purchase_order_number or "",
            "vendor_name": row.vendor_name or "",
            "customer_name": row.customer_name or "",
            "items_summary": row.items_summary or "",
            "assigned_user_id": row.assigned_user_id,
            "company_id": row.company_id,
            "branch_id": row.branch_id,
            "requested_by_id": requester_id,
            "requested_by_name": (names or {}).get(requester_id) if requester_id else None,
            "invoice_number": row.invoice_number,
            "invoice_date": row.invoice_date,
            "invoice_quantity": float(row.invoice_quantity)
            if row.invoice_quantity is not None
            else None,
            "invoice_amount": float(row.invoice_amount)
            if row.invoice_amount is not None
            else None,
            "suggested_quantity": suggested_qty,
            "suggested_amount": suggested_amount,
            "completed_at": row.completed_at,
            "created_at": row.created_at,
        }

    def serialize_many(
        self, ctx: TenantContext, rows: list[ProcInvoiceGenerationTask]
    ) -> list[dict]:
        requester_ids: set[UUID] = set()
        for row in rows:
            rid = getattr(row, "requested_by", None) or getattr(row, "created_by", None)
            if rid is not None:
                requester_ids.add(rid)
        names = self._resolve_user_names(ctx.tenant_id, requester_ids)
        return [self.serialize(ctx, row, requester_names=names) for row in rows]

    def submit(
        self,
        ctx: TenantContext,
        task_id: UUID,
        *,
        invoice_number: str,
        invoice_date: date,
        invoice_quantity: float | None = None,
        invoice_amount: float | None = None,
        file_name: str | None = None,
        content_base64: str | None = None,
        content_type: str | None = None,
    ) -> ProcInvoiceGenerationTask:
        task = self._repo.get(ctx, task_id)
        if task is None:
            raise NotFoundException("Invoice generation task not found")
        if task.status != "pending":
            raise ConflictException("Invoice generation task is already completed")
        if ctx.user_id is None:
            raise ForbiddenException("Authentication required")
        is_assignee = task.assigned_user_id == ctx.user_id
        if not is_assignee and not self._admin.is_admin(ctx):
            raise ForbiddenException("Only the assigned Accounts user can complete this task")

        number = invoice_number.strip()
        if not number:
            raise ConflictException("Invoice number is required")

        scm_qty, scm_amount = self.billing_totals_for_batch(
            ctx,
            order_id=task.order_header_id,
            receipt_batch_id=task.receipt_batch_id,
        )
        qty = scm_qty if scm_qty > 0 else float(invoice_quantity or 0)
        amount = scm_amount if scm_amount > 0 else float(invoice_amount or 0)
        if qty < 0:
            raise ConflictException("Invoice quantity cannot be negative")
        if amount < 0:
            raise ConflictException("Invoice amount cannot be negative")

        task.invoice_number = number[:80]
        task.invoice_date = invoice_date
        task.invoice_quantity = float(qty)
        task.invoice_amount = float(amount)
        task.status = "completed"
        task.completed_at = datetime.now(timezone.utc)
        task.completed_by = ctx.user_id
        task.updated_by = ctx.user_id

        # Mirror completed invoice onto the Billing GRN batch for Billing/challan prefill.
        from modules.procurement.service.scm_handoff_service import ScmHandoffService

        ScmHandoffService(self._db).update_receipt_batch_vendor_invoice(
            ctx,
            task.receipt_batch_id,
            vendor_invoice_number=number,
            vendor_invoice_date=invoice_date,
            vendor_invoice_quantity=float(qty),
            vendor_invoice_subtotal=float(amount),
            file_name=file_name,
            content_base64=content_base64,
            content_type=content_type,
            branch_id=task.branch_id,
            company_id=task.company_id,
        )

        self._db.flush()
        return task
