"""Customer GST registrations: head office at onboarding, branches picked up from POs."""

from __future__ import annotations

import base64
import binascii
from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import ConflictException, NotFoundException, ValidationException
from modules.crm.domain.customer_po_extract import GST_STATE_CODES, GSTIN_RE, extract_customer_po_fields
from modules.crm.models import CrmCompany, CrmCompanyGst
from modules.crm.repository.customer_ledger_repository import CompanyGstRepository
from modules.crm.repository.selling_entity_repository import SellingEntityRepository
from modules.crm.service.company_service import CompanyService
from modules.foundation.domain.value_objects import TenantContext
from shared.document_text import text_from_bytes

MAX_PO_BYTES = 12 * 1024 * 1024


def normalize_gstin(value: str) -> str:
    gstin = (value or "").strip().upper().replace(" ", "")
    if not GSTIN_RE.fullmatch(gstin):
        raise ValidationException(f"'{value}' is not a valid 15-character GSTIN")
    return gstin


class CompanyGstService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._repo = CompanyGstRepository(db)
        self._companies = CompanyService(db)

    def _account(self, ctx: TenantContext, company_account_id: UUID) -> CrmCompany:
        return self._companies.get(ctx, company_account_id)

    def list(self, ctx: TenantContext, company_account_id: UUID) -> list[CrmCompanyGst]:
        self._account(ctx, company_account_id)
        return self._repo.list_for_account(ctx, company_account_id)

    def _clear_head_office(self, ctx: TenantContext, company_account_id: UUID, keep_id: UUID | None) -> None:
        for row in self._repo.list_for_account(ctx, company_account_id):
            if row.is_head_office and row.id != keep_id:
                self._repo.update(ctx, row, is_head_office=False)

    def create(
        self,
        ctx: TenantContext,
        company_account_id: UUID,
        *,
        gstin: str,
        location_label: str | None = None,
        billing_address: str | None = None,
        shipping_address: str | None = None,
        is_head_office: bool = False,
        certificate_attachment_id: UUID | None = None,
        source: str = "manual",
    ) -> CrmCompanyGst:
        account = self._account(ctx, company_account_id)
        value = normalize_gstin(gstin)
        if self._repo.find(ctx, company_account_id, value) is not None:
            raise ConflictException(f"GSTIN {value} is already registered on this account")
        existing = self._repo.list_for_account(ctx, company_account_id)
        row = self._repo.create(
            ctx,
            company_id=account.company_id,
            branch_id=account.branch_id,
            company_account_id=company_account_id,
            gstin=value,
            state_code=value[:2],
            state=GST_STATE_CODES.get(value[:2]),
            location_label=(location_label or "").strip() or None,
            billing_address=(billing_address or "").strip() or None,
            shipping_address=(shipping_address or "").strip() or None,
            # First registration on an account is its head office unless told otherwise.
            is_head_office=bool(is_head_office or not existing),
            certificate_attachment_id=certificate_attachment_id,
            source=source,
        )
        if row.is_head_office:
            self._clear_head_office(ctx, company_account_id, row.id)
        return row

    def update(self, ctx: TenantContext, gst_id: UUID, **fields) -> CrmCompanyGst:
        row = self._repo.get(ctx, gst_id)
        if row is None:
            raise NotFoundException("GST registration not found")
        self._account(ctx, row.company_account_id)
        fields.pop("gstin", None)
        for key in ("location_label", "billing_address", "shipping_address"):
            if key in fields and isinstance(fields[key], str):
                fields[key] = fields[key].strip() or None
        if "status" in fields and fields["status"] not in ("active", "inactive"):
            raise ConflictException("status must be 'active' or 'inactive'")
        row = self._repo.update(ctx, row, **fields)
        if fields.get("is_head_office"):
            self._clear_head_office(ctx, row.company_account_id, row.id)
        return row

    def delete(self, ctx: TenantContext, gst_id: UUID) -> None:
        row = self._repo.get(ctx, gst_id)
        if row is None:
            raise NotFoundException("GST registration not found")
        self._account(ctx, row.company_account_id)
        self._repo.soft_delete(ctx, row)

    def capture_from_po(
        self,
        ctx: TenantContext,
        company_account_id: UUID,
        registrations: list[dict[str, Any]],
        *,
        billing_address: str | None,
        shipping_address: str | None,
    ) -> list[dict[str, Any]]:
        """Save GSTINs seen on a customer PO so every PO location builds the account's GST book."""
        account = self._account(ctx, company_account_id)
        out: list[dict[str, Any]] = []
        for reg in registrations:
            gstin = reg["gstin"]
            existing = self._repo.find(ctx, company_account_id, gstin)
            if existing is not None:
                out.append({**reg, "id": existing.id, "is_new": False})
                continue
            has_any = bool(self._repo.list_for_account(ctx, company_account_id))
            row = self._repo.create(
                ctx,
                company_id=account.company_id,
                branch_id=account.branch_id,
                company_account_id=company_account_id,
                gstin=gstin,
                state_code=gstin[:2],
                state=GST_STATE_CODES.get(gstin[:2]),
                location_label=GST_STATE_CODES.get(gstin[:2]),
                billing_address=billing_address,
                shipping_address=shipping_address,
                is_head_office=not has_any,
                source="customer_po",
            )
            out.append({**reg, "id": row.id, "is_new": True})
        return out


class CustomerPoExtractService:
    """Read PO number/date, GSTINs, bill-to/ship-to and lead time off an uploaded customer PO."""

    def __init__(self, db: Session) -> None:
        self._db = db
        self._gst = CompanyGstService(db)
        self._entities = SellingEntityRepository(db)

    def extract(
        self,
        ctx: TenantContext,
        *,
        opportunity_id: UUID,
        file_name: str,
        content_base64: str,
        capture_gst: bool = True,
    ) -> dict[str, Any]:
        from modules.crm.service.blueprint_service import OpportunityBlueprintService

        opp = OpportunityBlueprintService(self._db).get(ctx, opportunity_id)
        try:
            raw = base64.b64decode(content_base64, validate=True)
        except (ValueError, binascii.Error) as exc:
            raise ValidationException("Invalid PO file data. Re-upload the PDF, image or Excel file.") from exc
        if len(raw) > MAX_PO_BYTES:
            raise ValidationException("PO file is too large (max 12 MB)")

        text = text_from_bytes(raw, file_name or "po.pdf", ocr=True)
        own = [e.entity_gst for e in self._entities.list_entities(ctx, opp.company_id) if e.entity_gst]
        fields = extract_customer_po_fields(text, own_gstins=own)
        if capture_gst and opp.company_account_id is not None and fields["gst_registrations"]:
            fields["gst_registrations"] = self._gst.capture_from_po(
                ctx,
                opp.company_account_id,
                fields["gst_registrations"],
                billing_address=fields.get("billing_address"),
                shipping_address=fields.get("shipping_address"),
            )
        return fields
