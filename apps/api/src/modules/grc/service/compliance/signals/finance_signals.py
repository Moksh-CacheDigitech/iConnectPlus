"""Finance compliance signals - read-only checks via the finance port."""

from uuid import UUID

from sqlalchemy.orm import Session

from modules.foundation.domain.value_objects import TenantContext
from modules.grc.adapters.finance_port import GrcFinanceAdapter
from modules.grc.service.compliance.signal_types import ComplianceSignalResult


def signal_gst_tax_register_populated(
    db: Session,
    ctx: TenantContext,
    company_id: UUID,
) -> ComplianceSignalResult:
    """India GST: tax register has posted lines for the company."""
    code = "IN-GST-TAX-REGISTER"
    count = GrcFinanceAdapter(db).tax_register_line_count(ctx, company_id)
    if count > 0:
        return ComplianceSignalResult(
            requirement_code=code,
            status="partially_compliant",
            summary=(
                f"Tax register has {count} line(s). "
                "E-invoice / GSTR filing integration is not yet automated."
            ),
            details={"tax_register_lines": count},
        )
    return ComplianceSignalResult(
        requirement_code=code,
        status="non_compliant",
        summary="No GST/VAT/TDS lines in the finance tax register.",
        details={"tax_register_lines": 0},
    )
