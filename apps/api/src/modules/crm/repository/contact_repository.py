"""CRM CrmContact repository."""

from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from modules.crm.models import CrmContact
from modules.crm.repository.base import CrmScopedRepository, utcnow
from modules.foundation.domain.value_objects import TenantContext


def normalize_email(value: str | None) -> str | None:
    text = (value or "").strip().lower()
    return text or None


def normalize_phone(value: str | None) -> str | None:
    """Keep digits only for comparison (E.164-ish without forcing +)."""
    digits = "".join(ch for ch in (value or "") if ch.isdigit())
    if len(digits) < 7:
        return None
    if len(digits) > 10:
        digits = digits[-10:]
    return digits


def normalize_name(first: str | None, last: str | None) -> str:
    parts = [((first or "").strip().lower()), ((last or "").strip().lower())]
    return " ".join(p for p in parts if p)


class ContactRepository(CrmScopedRepository):
    def __init__(self, db: Session) -> None:
        super().__init__(db)

    def get(self, ctx: TenantContext, row_id: UUID) -> CrmContact | None:
        stmt = select(CrmContact).where(CrmContact.id == row_id, CrmContact.is_deleted.is_(False))
        stmt = self.apply_crm_filter(stmt, CrmContact, ctx, branch_scoped=True)
        return self.db.scalar(stmt)

    def list_contacts(
        self, ctx: TenantContext, company_id: UUID, company_account_id: UUID | None = None
    ):
        stmt = select(CrmContact).where(
            CrmContact.company_id == company_id,
            CrmContact.is_deleted.is_(False),
        )
        if company_account_id is not None:
            stmt = stmt.where(CrmContact.company_account_id == company_account_id)
        stmt = self.apply_crm_filter(stmt, CrmContact, ctx, branch_scoped=True)
        stmt = stmt.order_by(CrmContact.created_at.desc())
        return list(self.db.scalars(stmt).all())

    def find_duplicates(
        self,
        ctx: TenantContext,
        *,
        company_account_id: UUID,
        email: str | None = None,
        phone: str | None = None,
        mobile: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        exclude_id: UUID | None = None,
    ) -> list[CrmContact]:
        """Exact email/phone match + fuzzy name+phone within the sales account (VAPT 7.1.35)."""
        stmt = select(CrmContact).where(
            CrmContact.tenant_id == ctx.tenant_id,
            CrmContact.company_account_id == company_account_id,
            CrmContact.is_deleted.is_(False),
        )
        if exclude_id is not None:
            stmt = stmt.where(CrmContact.id != exclude_id)
        candidates = list(self.db.scalars(stmt).all())
        if not candidates:
            return []

        want_email = normalize_email(email)
        want_phones = {
            p for p in (normalize_phone(phone), normalize_phone(mobile)) if p
        }
        want_name = normalize_name(first_name, last_name)
        hits: list[CrmContact] = []
        seen: set[UUID] = set()

        for row in candidates:
            row_email = normalize_email(row.email)
            row_phones = {
                p for p in (normalize_phone(row.phone), normalize_phone(row.mobile)) if p
            }
            exact = False
            if want_email and row_email and want_email == row_email:
                exact = True
            if want_phones and row_phones and want_phones & row_phones:
                exact = True
            fuzzy = False
            if want_name and want_phones:
                row_name = normalize_name(row.first_name, row.last_name)
                if row_name == want_name and (want_phones & row_phones):
                    fuzzy = True
                elif (
                    row_name
                    and want_name
                    and (want_name in row_name or row_name in want_name)
                    and (want_phones & row_phones)
                ):
                    fuzzy = True
            if exact or fuzzy:
                if row.id not in seen:
                    hits.append(row)
                    seen.add(row.id)
        return hits

    def create(self, ctx: TenantContext, **fields) -> CrmContact:
        row = CrmContact(
            id=uuid4(),
            tenant_id=ctx.tenant_id,
            created_by=ctx.user_id,
            updated_by=ctx.user_id,
            **fields,
        )
        self.db.add(row)
        self.db.flush()
        return row

    def update(self, ctx: TenantContext, row_id: UUID, **fields) -> CrmContact | None:
        row = self.get(ctx, row_id)
        if row is None:
            return None
        for k, v in fields.items():
            if v is not None:
                setattr(row, k, v)
        row.updated_at = utcnow()
        row.updated_by = ctx.user_id
        row.version = int(row.version or 1) + 1
        self.db.flush()
        return row
