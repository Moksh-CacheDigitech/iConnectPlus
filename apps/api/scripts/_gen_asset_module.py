"""Generate Sprint 15 Asset Management module. Run from apps/api:
.venv\\Scripts\\python.exe scripts/_gen_asset_module.py
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
AST = SRC / "modules" / "asset"
ALEMBIC = ROOT / "alembic" / "versions"
TESTS = SRC / "tests"
SHARED = SRC / "shared"

FILES_WRITTEN: list[Path] = []

OPT_BRANCH = '''
    branch_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organization.org_branch.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
'''

WF_FIELDS = '''
    workflow_status: Mapped[str | None] = mapped_column(String(30), nullable=True)
    workflow_instance_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("foundation.wf_instance.id", ondelete="SET NULL"),
        nullable=True,
    )
'''


def w(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not content.endswith("\n"):
        content += "\n"
    path.write_text(content, encoding="utf-8")
    FILES_WRITTEN.append(path)
    print("wrote", path.relative_to(ROOT))


def patch_file(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if new.strip() in text:
        print("skip (already)", path.relative_to(ROOT))
        return
    if old not in text:
        raise SystemExit(f"patch failed in {path}: marker not found")
    path.write_text(text.replace(old, new), encoding="utf-8")
    print("patched", path.relative_to(ROOT))


# table_key, ORM class, Repo/Engine stem, branch_scoped (mandatory BranchMixin)
TABLES: list[tuple[str, str, str, bool]] = [
    ("asset_category", "AstAssetCategory", "AssetCategory", False),
    ("asset", "AstAsset", "Asset", True),
    ("asset_component", "AstAssetComponent", "AssetComponent", False),
    ("asset_assignment", "AstAssetAssignment", "AssetAssignment", True),
    ("asset_transfer", "AstAssetTransfer", "AssetTransfer", True),
    ("asset_location", "AstAssetLocation", "AssetLocation", False),
    ("asset_warranty", "AstAssetWarranty", "AssetWarranty", False),
    ("asset_insurance", "AstAssetInsurance", "AssetInsurance", False),
    ("asset_maintenance_plan", "AstAssetMaintenancePlan", "AssetMaintenancePlan", False),
    ("asset_maintenance", "AstAssetMaintenance", "AssetMaintenance", True),
    ("asset_service_history", "AstAssetServiceHistory", "AssetServiceHistory", False),
    ("asset_depreciation", "AstAssetDepreciation", "AssetDepreciation", False),
    ("asset_disposal", "AstAssetDisposal", "AssetDisposal", True),
    ("asset_revaluation", "AstAssetRevaluation", "AssetRevaluation", True),
    ("asset_audit", "AstAssetAudit", "AssetAudit", True),
    ("asset_document", "AstAssetDocument", "AssetDocument", False),
    ("asset_checklist", "AstAssetChecklist", "AssetChecklist", False),
    ("asset_meter_reading", "AstAssetMeterReading", "AssetMeterReading", False),
    ("asset_notification", "AstAssetNotification", "AssetNotification", False),
    ("asset_report", "AstAssetReport", "AssetReport", False),
]

CLASS_MAP = {t[0]: t[1] for t in TABLES}

MIGRATIONS: list[tuple[str, str | list[str], str]] = [
    ("0245_create_asset_schema", "schema", "0244_seed_project_workflows"),
    ("0246_ast_asset_category", "asset_category", "0245_create_asset_schema"),
    ("0247_ast_asset", "asset", "0246_ast_asset_category"),
    ("0248_ast_asset_component", "asset_component", "0247_ast_asset"),
    ("0249_ast_asset_assignment", "asset_assignment", "0248_ast_asset_component"),
    ("0250_ast_asset_transfer", "asset_transfer", "0249_ast_asset_assignment"),
    ("0251_ast_asset_location", "asset_location", "0250_ast_asset_transfer"),
    ("0252_ast_warranty_insurance", ["asset_warranty", "asset_insurance"], "0251_ast_asset_location"),
    ("0253_ast_maint_plan", "asset_maintenance_plan", "0252_ast_warranty_insurance"),
    ("0254_ast_asset_maintenance", "asset_maintenance", "0253_ast_maint_plan"),
    ("0255_ast_service_history", "asset_service_history", "0254_ast_asset_maintenance"),
    ("0256_ast_asset_depreciation", "asset_depreciation", "0255_ast_service_history"),
    ("0257_ast_asset_disposal", "asset_disposal", "0256_ast_asset_depreciation"),
    ("0258_ast_asset_revaluation", "asset_revaluation", "0257_ast_asset_disposal"),
    ("0259_ast_asset_audit", "asset_audit", "0258_ast_asset_revaluation"),
    ("0260_ast_asset_document", "asset_document", "0259_ast_asset_audit"),
    ("0261_ast_asset_checklist", "asset_checklist", "0260_ast_asset_document"),
    ("0262_ast_meter_reading", "asset_meter_reading", "0261_ast_asset_checklist"),
    ("0263_ast_asset_notification", "asset_notification", "0262_ast_meter_reading"),
    ("0264_ast_asset_report", "asset_report", "0263_ast_asset_notification"),
    ("0265_seed_asset_permissions", "seed_perms", "0264_ast_asset_report"),
    ("0266_seed_asset_workflows", "seed_wf", "0265_seed_asset_permissions"),
]

# route prefix, schema name, service class, permission resource, branch required
ROUTE_SPECS: list[tuple[str, str, str, str, bool]] = [
    ("asset-categories", "AssetCategory", "AssetCategoryService", "asset.category", False),
    ("assets", "Asset", "AssetService", "asset.asset", True),
    ("asset-components", "AssetComponent", "ComponentService", "asset.asset", False),
    ("asset-assignments", "AssetAssignment", "AssignmentService", "asset.assignment", True),
    ("asset-transfers", "AssetTransfer", "TransferService", "asset.transfer", True),
    ("asset-locations", "AssetLocation", "LocationService", "asset.location", False),
    ("asset-warranties", "AssetWarranty", "WarrantyService", "asset.warranty", False),
    ("asset-insurances", "AssetInsurance", "InsuranceService", "asset.insurance", False),
    ("maintenance-plans", "MaintenancePlan", "MaintenancePlanService", "asset.maintenance", False),
    ("asset-maintenances", "AssetMaintenance", "MaintenanceService", "asset.maintenance", True),
    ("service-histories", "ServiceHistory", "ServiceHistoryService", "asset.maintenance", False),
    ("asset-depreciations", "AssetDepreciation", "DepreciationService", "asset.depreciation", False),
    ("asset-disposals", "AssetDisposal", "DisposalService", "asset.disposal", True),
    ("asset-revaluations", "AssetRevaluation", "RevaluationService", "asset.revaluation", True),
    ("asset-audits", "AssetAudit", "AssetAuditService", "asset.audit", True),
    ("asset-documents", "AssetDocument", "DocumentService", "asset.document", False),
    ("asset-checklists", "AssetChecklist", "ChecklistService", "asset.checklist", False),
    ("meter-readings", "MeterReading", "MeterReadingService", "asset.meter", False),
    ("asset-notifications", "AssetNotification", "NotificationService", "asset.asset", False),
    ("reports", "AssetReport", "AssetReportService", "asset.report", False),
]

# ---------------------------------------------------------------------------
# MODEL BODIES
# ---------------------------------------------------------------------------

MODELS: dict[str, str] = {}

MODELS["asset_category"] = f'''"""Asset category ORM per ERD_15 section 6.1."""

from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.asset.models.mixins import AstMasterMixin


class AstAssetCategory(Base, *AstMasterMixin):
    __tablename__ = "ast_asset_category"
    __table_args__ = (
        UniqueConstraint("company_id", "category_code", name="uk_ast_asset_category_code"),
        CheckConstraint(
            "default_depreciation_method IS NULL OR default_depreciation_method IN "
            "('straight_line','wdv','units_of_production')",
            name="ck_ast_asset_category_depr_method",
        ),
        CheckConstraint(
            "status IN ('active','inactive')",
            name="ck_ast_asset_category_status",
        ),
        {{"schema": "asset"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
{OPT_BRANCH}
    category_code: Mapped[str] = mapped_column(String(50), nullable=False)
    category_name: Mapped[str] = mapped_column(String(255), nullable=False)
    default_useful_life_months: Mapped[int | None] = mapped_column(Integer, nullable=True)
    default_depreciation_method: Mapped[str | None] = mapped_column(String(40), nullable=True)
    gl_asset_account_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    gl_accum_depr_account_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    gl_expense_account_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active", index=True)
'''

MODELS["asset"] = f'''"""Asset register ORM per ERD_15 section 6.2."""

from datetime import date
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import Boolean, CheckConstraint, Date, ForeignKey, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.asset.models.mixins import AstTransactionMixin


class AstAsset(Base, *AstTransactionMixin):
    __tablename__ = "ast_asset"
    __table_args__ = (
        UniqueConstraint("company_id", "asset_code", name="uk_ast_asset_company_code"),
        CheckConstraint(
            "asset_type IN ('fixed','consumable','digital','leased')",
            name="ck_ast_asset_type",
        ),
        CheckConstraint(
            "depreciation_method IS NULL OR depreciation_method IN "
            "('straight_line','wdv','units_of_production')",
            name="ck_ast_asset_depr_method",
        ),
        CheckConstraint(
            "status IN ('draft','submitted','approved','active','in_maintenance',"
            "'transferred','disposed','written_off','cancelled')",
            name="ck_ast_asset_status",
        ),
        CheckConstraint(
            "purchase_cost IS NULL OR purchase_cost >= 0",
            name="ck_ast_asset_purchase_cost",
        ),
        {{"schema": "asset"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    document_number: Mapped[str] = mapped_column(String(50), nullable=False)
    asset_code: Mapped[str] = mapped_column(String(50), nullable=False)
    asset_name: Mapped[str] = mapped_column(String(255), nullable=False)
    asset_category_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("asset.ast_asset_category.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    asset_type: Mapped[str] = mapped_column(String(40), nullable=False)
    master_asset_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_asset.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    product_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_product.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    supplier_vendor_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_vendor.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    serial_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    barcode: Mapped[str | None] = mapped_column(String(100), nullable=True)
    qr_code: Mapped[str | None] = mapped_column(String(100), nullable=True)
    rfid_tag: Mapped[str | None] = mapped_column(String(100), nullable=True)
    purchase_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    purchase_cost: Mapped[Decimal | None] = mapped_column(Numeric(18, 4), nullable=True)
    current_book_value: Mapped[Decimal | None] = mapped_column(Numeric(18, 4), nullable=True)
    salvage_value: Mapped[Decimal | None] = mapped_column(Numeric(18, 4), nullable=True)
    currency_code: Mapped[str] = mapped_column(String(10), nullable=False, default="USD")
    depreciation_method: Mapped[str | None] = mapped_column(String(40), nullable=True)
    useful_life_months: Mapped[int | None] = mapped_column(Integer, nullable=True)
    department_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organization.org_department.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    custodian_employee_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_employee.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    purchase_order_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    grn_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    inventory_receipt_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    inventory_issue_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    project_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    production_order_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    quality_inspection_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    is_shared: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)
{WF_FIELDS}
'''

MODELS["asset_component"] = f'''"""Asset component ORM per ERD_15 section 6.3."""

from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.asset.models.mixins import AstDetailMixin


class AstAssetComponent(Base, *AstDetailMixin):
    __tablename__ = "ast_asset_component"
    __table_args__ = (
        UniqueConstraint("asset_id", "component_code", name="uk_ast_asset_component_code"),
        CheckConstraint(
            "status IN ('active','replaced','disposed')",
            name="ck_ast_asset_component_status",
        ),
        {{"schema": "asset"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
{OPT_BRANCH}
    asset_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("asset.ast_asset.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    component_code: Mapped[str] = mapped_column(String(50), nullable=False)
    component_name: Mapped[str] = mapped_column(String(255), nullable=False)
    product_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_product.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    serial_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    quantity: Mapped[Decimal | None] = mapped_column(Numeric(18, 4), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active", index=True)
'''

MODELS["asset_assignment"] = f'''"""Asset assignment ORM per ERD_15 section 6.4."""

from datetime import date, datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, Date, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.asset.models.mixins import AstTransactionMixin


class AstAssetAssignment(Base, *AstTransactionMixin):
    __tablename__ = "ast_asset_assignment"
    __table_args__ = (
        UniqueConstraint("company_id", "document_number", name="uk_ast_asset_assignment_doc"),
        CheckConstraint(
            "allocation_type IN ('employee','department','project','branch','warehouse')",
            name="ck_ast_asset_assignment_alloc",
        ),
        CheckConstraint(
            "status IN ('draft','submitted','approved','active','returned','cancelled')",
            name="ck_ast_asset_assignment_status",
        ),
        {{"schema": "asset"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    document_number: Mapped[str] = mapped_column(String(50), nullable=False)
    asset_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("asset.ast_asset.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    allocation_type: Mapped[str] = mapped_column(String(40), nullable=False)
    employee_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_employee.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    department_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organization.org_department.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    project_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    allocated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    expected_return_at: Mapped[date | None] = mapped_column(Date, nullable=True)
    returned_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)
{WF_FIELDS}
'''

MODELS["asset_transfer"] = f'''"""Asset transfer ORM per ERD_15 section 6.5."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.asset.models.mixins import AstTransactionMixin


class AstAssetTransfer(Base, *AstTransactionMixin):
    __tablename__ = "ast_asset_transfer"
    __table_args__ = (
        UniqueConstraint("company_id", "document_number", name="uk_ast_asset_transfer_doc"),
        CheckConstraint(
            "status IN ('draft','completed','cancelled')",
            name="ck_ast_asset_transfer_status",
        ),
        {{"schema": "asset"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    document_number: Mapped[str] = mapped_column(String(50), nullable=False)
    asset_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("asset.ast_asset.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    from_branch_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organization.org_branch.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    to_branch_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organization.org_branch.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    from_department_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organization.org_department.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    to_department_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organization.org_department.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    from_employee_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_employee.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    to_employee_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_employee.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    transferred_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)
'''

MODELS["asset_location"] = f'''"""Asset location ORM per ERD_15 section 6.6."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.asset.models.mixins import AstDetailMixin


class AstAssetLocation(Base, *AstDetailMixin):
    __tablename__ = "ast_asset_location"
    __table_args__ = (
        CheckConstraint(
            "status IN ('active','historical')",
            name="ck_ast_asset_location_status",
        ),
        {{"schema": "asset"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
{OPT_BRANCH}
    asset_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("asset.ast_asset.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    location_label: Mapped[str] = mapped_column(String(255), nullable=False)
    org_location_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    effective_from: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    effective_to: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_current: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active", index=True)
'''

MODELS["asset_warranty"] = f'''"""Asset warranty ORM per ERD_15 section 6.7."""

from datetime import date
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, Date, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.asset.models.mixins import AstDetailMixin


class AstAssetWarranty(Base, *AstDetailMixin):
    __tablename__ = "ast_asset_warranty"
    __table_args__ = (
        CheckConstraint(
            "warranty_type IN ('manufacturer','extended','service')",
            name="ck_ast_asset_warranty_type",
        ),
        CheckConstraint(
            "status IN ('active','expired','void')",
            name="ck_ast_asset_warranty_status",
        ),
        CheckConstraint("end_date >= start_date", name="ck_ast_asset_warranty_dates"),
        {{"schema": "asset"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
{OPT_BRANCH}
    asset_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("asset.ast_asset.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    vendor_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_vendor.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    warranty_type: Mapped[str] = mapped_column(String(40), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    coverage_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active", index=True)
'''

MODELS["asset_insurance"] = f'''"""Asset insurance ORM per ERD_15 section 6.8."""

from datetime import date
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, Date, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.asset.models.mixins import AstDetailMixin


class AstAssetInsurance(Base, *AstDetailMixin):
    __tablename__ = "ast_asset_insurance"
    __table_args__ = (
        CheckConstraint(
            "status IN ('active','expired','cancelled')",
            name="ck_ast_asset_insurance_status",
        ),
        CheckConstraint("end_date >= start_date", name="ck_ast_asset_insurance_dates"),
        {{"schema": "asset"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
{OPT_BRANCH}
    asset_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("asset.ast_asset.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    policy_number: Mapped[str] = mapped_column(String(100), nullable=False)
    insurer_name: Mapped[str] = mapped_column(String(255), nullable=False)
    vendor_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_vendor.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    coverage_amount: Mapped[Decimal | None] = mapped_column(Numeric(18, 4), nullable=True)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active", index=True)
'''

MODELS["asset_maintenance_plan"] = f'''"""Asset maintenance plan ORM per ERD_15 section 6.9."""

from datetime import date
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, Date, ForeignKey, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.asset.models.mixins import AstDetailMixin


class AstAssetMaintenancePlan(Base, *AstDetailMixin):
    __tablename__ = "ast_asset_maintenance_plan"
    __table_args__ = (
        UniqueConstraint("company_id", "document_number", name="uk_ast_asset_maint_plan_doc"),
        CheckConstraint(
            "maintenance_type IN ('preventive','corrective','emergency','annual_service')",
            name="ck_ast_asset_maint_plan_type",
        ),
        CheckConstraint(
            "status IN ('draft','active','paused','closed')",
            name="ck_ast_asset_maint_plan_status",
        ),
        {{"schema": "asset"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
{OPT_BRANCH}
    document_number: Mapped[str] = mapped_column(String(50), nullable=False)
    asset_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("asset.ast_asset.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    plan_name: Mapped[str] = mapped_column(String(255), nullable=False)
    maintenance_type: Mapped[str] = mapped_column(String(40), nullable=False)
    frequency_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    frequency_meter_units: Mapped[Decimal | None] = mapped_column(Numeric(18, 4), nullable=True)
    next_due_date: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)
'''

MODELS["asset_maintenance"] = f'''"""Asset maintenance work order ORM per ERD_15 section 6.10."""

from datetime import date
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, Date, ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.asset.models.mixins import AstTransactionMixin


class AstAssetMaintenance(Base, *AstTransactionMixin):
    __tablename__ = "ast_asset_maintenance"
    __table_args__ = (
        UniqueConstraint("company_id", "document_number", name="uk_ast_asset_maintenance_doc"),
        CheckConstraint(
            "maintenance_type IN ('preventive','corrective','emergency','annual_service')",
            name="ck_ast_asset_maintenance_type",
        ),
        CheckConstraint(
            "status IN ('draft','submitted','approved','scheduled','in_progress',"
            "'completed','cancelled')",
            name="ck_ast_asset_maintenance_status",
        ),
        {{"schema": "asset"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    document_number: Mapped[str] = mapped_column(String(50), nullable=False)
    asset_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("asset.ast_asset.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    maintenance_plan_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("asset.ast_asset_maintenance_plan.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    maintenance_type: Mapped[str] = mapped_column(String(40), nullable=False)
    scheduled_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    completed_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    vendor_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_vendor.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    cost_amount: Mapped[Decimal | None] = mapped_column(Numeric(18, 4), nullable=True)
    technician_employee_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_employee.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    quality_inspection_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)
{WF_FIELDS}
'''

MODELS["asset_service_history"] = f'''"""Asset service history ORM per ERD_15 section 6.11."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Numeric, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.asset.models.mixins import AstDetailMixin


class AstAssetServiceHistory(Base, *AstDetailMixin):
    __tablename__ = "ast_asset_service_history"
    __table_args__ = (
        CheckConstraint(
            "status IN ('recorded')",
            name="ck_ast_asset_service_history_status",
        ),
        {{"schema": "asset"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
{OPT_BRANCH}
    asset_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("asset.ast_asset.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    maintenance_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("asset.ast_asset_maintenance.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    service_summary: Mapped[str] = mapped_column(Text, nullable=False)
    parts_replaced_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    cost_amount: Mapped[Decimal | None] = mapped_column(Numeric(18, 4), nullable=True)
    serviced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="recorded", index=True)
'''

# Fix missing String import in service history - patch below after write
MODELS["asset_service_history"] = MODELS["asset_service_history"].replace(
    "from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Numeric, Text",
    "from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Numeric, String, Text",
)

MODELS["asset_depreciation"] = f'''"""Asset depreciation ORM per ERD_15 section 6.12."""

from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, ForeignKey, Numeric, SmallInteger, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.asset.models.mixins import AstDetailMixin


class AstAssetDepreciation(Base, *AstDetailMixin):
    __tablename__ = "ast_asset_depreciation"
    __table_args__ = (
        UniqueConstraint("company_id", "document_number", name="uk_ast_asset_depreciation_doc"),
        UniqueConstraint(
            "asset_id", "period_year", "period_month", "idempotency_key",
            name="uk_ast_asset_depreciation_period",
        ),
        CheckConstraint(
            "method IN ('straight_line','wdv','units_of_production')",
            name="ck_ast_asset_depreciation_method",
        ),
        CheckConstraint(
            "status IN ('draft','calculated','posted','failed','reversed')",
            name="ck_ast_asset_depreciation_status",
        ),
        {{"schema": "asset"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
{OPT_BRANCH}
    document_number: Mapped[str] = mapped_column(String(50), nullable=False)
    asset_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("asset.ast_asset.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    period_year: Mapped[int] = mapped_column(SmallInteger, nullable=False, index=True)
    period_month: Mapped[int] = mapped_column(SmallInteger, nullable=False, index=True)
    method: Mapped[str] = mapped_column(String(40), nullable=False)
    depreciation_amount: Mapped[Decimal | None] = mapped_column(Numeric(18, 4), nullable=True)
    book_value_after: Mapped[Decimal | None] = mapped_column(Numeric(18, 4), nullable=True)
    units_produced: Mapped[Decimal | None] = mapped_column(Numeric(18, 4), nullable=True)
    depreciation_batch_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    finance_journal_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    idempotency_key: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)
'''

MODELS["asset_disposal"] = f'''"""Asset disposal ORM per ERD_15 section 6.13."""

from datetime import date
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, Date, ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.asset.models.mixins import AstTransactionMixin


class AstAssetDisposal(Base, *AstTransactionMixin):
    __tablename__ = "ast_asset_disposal"
    __table_args__ = (
        UniqueConstraint("company_id", "document_number", name="uk_ast_asset_disposal_doc"),
        CheckConstraint(
            "disposal_type IN ('sale','scrap','donation','write_off')",
            name="ck_ast_asset_disposal_type",
        ),
        CheckConstraint(
            "status IN ('draft','submitted','approved','posted','cancelled')",
            name="ck_ast_asset_disposal_status",
        ),
        {{"schema": "asset"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    document_number: Mapped[str] = mapped_column(String(50), nullable=False)
    asset_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("asset.ast_asset.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    disposal_type: Mapped[str] = mapped_column(String(40), nullable=False)
    disposal_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    proceeds_amount: Mapped[Decimal | None] = mapped_column(Numeric(18, 4), nullable=True)
    book_value_at_disposal: Mapped[Decimal | None] = mapped_column(Numeric(18, 4), nullable=True)
    finance_journal_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)
{WF_FIELDS}
'''

MODELS["asset_revaluation"] = f'''"""Asset revaluation ORM per ERD_15 section 6.14."""

from datetime import date
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, Date, ForeignKey, Numeric, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.asset.models.mixins import AstTransactionMixin


class AstAssetRevaluation(Base, *AstTransactionMixin):
    __tablename__ = "ast_asset_revaluation"
    __table_args__ = (
        UniqueConstraint("company_id", "document_number", name="uk_ast_asset_revaluation_doc"),
        CheckConstraint(
            "status IN ('draft','submitted','approved','posted','cancelled')",
            name="ck_ast_asset_revaluation_status",
        ),
        {{"schema": "asset"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    document_number: Mapped[str] = mapped_column(String(50), nullable=False)
    asset_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("asset.ast_asset.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    revaluation_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    old_book_value: Mapped[Decimal | None] = mapped_column(Numeric(18, 4), nullable=True)
    new_book_value: Mapped[Decimal | None] = mapped_column(Numeric(18, 4), nullable=True)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    finance_journal_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)
{WF_FIELDS}
'''

MODELS["asset_audit"] = f'''"""Physical asset audit ORM per ERD_15 section 6.15."""

from datetime import date
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, Date, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.asset.models.mixins import AstTransactionMixin


class AstAssetAudit(Base, *AstTransactionMixin):
    __tablename__ = "ast_asset_audit"
    __table_args__ = (
        UniqueConstraint("company_id", "document_number", name="uk_ast_asset_audit_doc"),
        CheckConstraint(
            "found_status IN ('found','missing','damaged','relocated')",
            name="ck_ast_asset_audit_found",
        ),
        CheckConstraint(
            "status IN ('planned','in_progress','completed','cancelled')",
            name="ck_ast_asset_audit_status",
        ),
        {{"schema": "asset"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    document_number: Mapped[str] = mapped_column(String(50), nullable=False)
    asset_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("asset.ast_asset.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    audit_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    auditor_employee_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_employee.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    found_status: Mapped[str | None] = mapped_column(String(40), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="planned", index=True)
'''

MODELS["asset_document"] = f'''"""Asset document ORM per ERD_15 section 6.16."""

from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.asset.models.mixins import AstDetailMixin


class AstAssetDocument(Base, *AstDetailMixin):
    __tablename__ = "ast_asset_document"
    __table_args__ = (
        CheckConstraint(
            "document_type IN ('invoice','warranty','insurance','manual','photo','other')",
            name="ck_ast_asset_document_type",
        ),
        CheckConstraint(
            "status IN ('active','superseded','archived')",
            name="ck_ast_asset_document_status",
        ),
        {{"schema": "asset"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
{OPT_BRANCH}
    asset_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("asset.ast_asset.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    document_type: Mapped[str] = mapped_column(String(40), nullable=False)
    document_name: Mapped[str] = mapped_column(String(255), nullable=False)
    storage_uri: Mapped[str | None] = mapped_column(String(500), nullable=True)
    content_hash: Mapped[str | None] = mapped_column(String(128), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active", index=True)
'''

MODELS["asset_checklist"] = f'''"""Asset checklist ORM per ERD_15 section 6.17."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.asset.models.mixins import AstDetailMixin


class AstAssetChecklist(Base, *AstDetailMixin):
    __tablename__ = "ast_asset_checklist"
    __table_args__ = (
        CheckConstraint(
            "status IN ('draft','completed','cancelled')",
            name="ck_ast_asset_checklist_status",
        ),
        {{"schema": "asset"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
{OPT_BRANCH}
    asset_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("asset.ast_asset.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    maintenance_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("asset.ast_asset_maintenance.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    audit_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("asset.ast_asset_audit.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    checklist_code: Mapped[str] = mapped_column(String(50), nullable=False)
    checklist_name: Mapped[str] = mapped_column(String(255), nullable=False)
    items_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)
'''

MODELS["asset_meter_reading"] = f'''"""Asset meter reading ORM per ERD_15 section 6.18."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.asset.models.mixins import AstDetailMixin


class AstAssetMeterReading(Base, *AstDetailMixin):
    __tablename__ = "ast_asset_meter_reading"
    __table_args__ = (
        CheckConstraint(
            "meter_type IN ('odometer','runtime_hours','cycle_count','other')",
            name="ck_ast_asset_meter_type",
        ),
        CheckConstraint(
            "status IN ('recorded','void')",
            name="ck_ast_asset_meter_status",
        ),
        {{"schema": "asset"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
{OPT_BRANCH}
    asset_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("asset.ast_asset.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    meter_type: Mapped[str] = mapped_column(String(40), nullable=False)
    reading_value: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    reading_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    recorded_by_employee_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_employee.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="recorded", index=True)
'''

MODELS["asset_notification"] = f'''"""Asset notification ORM per ERD_15 section 6.19."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.asset.models.mixins import AstDetailMixin


class AstAssetNotification(Base, *AstDetailMixin):
    __tablename__ = "ast_asset_notification"
    __table_args__ = (
        CheckConstraint(
            "notification_type IN ('maintenance_due','warranty_expiry','insurance_expiry',"
            "'audit_due','depreciation','other')",
            name="ck_ast_asset_notification_type",
        ),
        CheckConstraint(
            "delivery_status IN ('pending','sent','failed','read')",
            name="ck_ast_asset_notification_delivery",
        ),
        CheckConstraint(
            "status IN ('active','archived')",
            name="ck_ast_asset_notification_status",
        ),
        {{"schema": "asset"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
{OPT_BRANCH}
    asset_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("asset.ast_asset.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    notification_type: Mapped[str] = mapped_column(String(40), nullable=False)
    recipient_user_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    recipient_employee_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    payload_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    delivery_status: Mapped[str] = mapped_column(String(30), nullable=False, default="pending")
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active", index=True)
'''

MODELS["asset_report"] = f'''"""Asset report ORM per ERD_15 section 6.20."""

from datetime import date, datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, Date, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.asset.models.mixins import AstDetailMixin


class AstAssetReport(Base, *AstDetailMixin):
    __tablename__ = "ast_asset_report"
    __table_args__ = (
        UniqueConstraint("company_id", "report_code", name="uk_ast_asset_report_code"),
        CheckConstraint(
            "report_type IN ('register','depreciation_schedule','utilization',"
            "'maintenance_due','insurance_expiry','audit_variance')",
            name="ck_ast_asset_report_type",
        ),
        CheckConstraint(
            "status IN ('draft','finalized')",
            name="ck_ast_asset_report_status",
        ),
        {{"schema": "asset"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
{OPT_BRANCH}
    report_code: Mapped[str] = mapped_column(String(50), nullable=False)
    report_type: Mapped[str] = mapped_column(String(40), nullable=False)
    period_start: Mapped[date | None] = mapped_column(Date, nullable=True)
    period_end: Mapped[date | None] = mapped_column(Date, nullable=True)
    department_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organization.org_department.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    category_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("asset.ast_asset_category.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    metrics_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    generated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)
'''

assert len(MODELS) == 20, f"Expected 20 models, got {len(MODELS)}"

ENGINE_FILE_MAP = {
    "AssetCategory": "asset_category",
    "Asset": "asset",
    "AssetComponent": "asset_component",
    "AssetAssignment": "asset_assignment",
    "AssetTransfer": "asset_transfer",
    "AssetLocation": "asset_location",
    "AssetWarranty": "asset_warranty",
    "AssetInsurance": "asset_insurance",
    "AssetMaintenancePlan": "asset_maintenance_plan",
    "AssetMaintenance": "asset_maintenance",
    "AssetServiceHistory": "asset_service_history",
    "AssetDepreciation": "asset_depreciation",
    "AssetDisposal": "asset_disposal",
    "AssetRevaluation": "asset_revaluation",
    "AssetAudit": "asset_audit",
    "AssetDocument": "asset_document",
    "AssetChecklist": "asset_checklist",
    "AssetMeterReading": "asset_meter_reading",
    "AssetNotification": "asset_notification",
    "AssetReport": "asset_report",
}

ENGINE_IMPORTS = """
from modules.asset.domain.enums import (
    AssetAssignmentStatus,
    AssetAuditStatus,
    AssetCategoryStatus,
    AssetChecklistStatus,
    AssetComponentStatus,
    AssetDepreciationStatus,
    AssetDisposalStatus,
    AssetDocumentStatus,
    AssetInsuranceStatus,
    AssetLocationStatus,
    AssetMaintenancePlanStatus,
    AssetMaintenanceStatus,
    AssetMeterReadingStatus,
    AssetNotificationStatus,
    AssetReportStatus,
    AssetRevaluationStatus,
    AssetServiceHistoryStatus,
    AssetStatus,
    AssetTransferStatus,
    AssetWarrantyStatus,
)
from modules.asset.domain.exceptions import (
    InvalidAssetAssignmentState,
    InvalidAssetAuditState,
    InvalidAssetCategoryState,
    InvalidAssetChecklistState,
    InvalidAssetComponentState,
    InvalidAssetDepreciationState,
    InvalidAssetDisposalState,
    InvalidAssetDocumentState,
    InvalidAssetInsuranceState,
    InvalidAssetLocationState,
    InvalidAssetMaintenancePlanState,
    InvalidAssetMaintenanceState,
    InvalidAssetMeterReadingState,
    InvalidAssetNotificationState,
    InvalidAssetReportState,
    InvalidAssetRevaluationState,
    InvalidAssetServiceHistoryState,
    InvalidAssetState,
    InvalidAssetTransferState,
    InvalidAssetWarrantyState,
)
"""

ENGINE_BODIES: dict[str, str] = {
    "AssetCategory": '''
class AssetCategoryEngine:
    def activate(self, row) -> None:
        row.status = AssetCategoryStatus.ACTIVE.value

    def deactivate(self, row) -> None:
        if row.status != AssetCategoryStatus.ACTIVE.value:
            raise InvalidAssetCategoryState("Only active categories can be deactivated")
        row.status = AssetCategoryStatus.INACTIVE.value
''',
    "Asset": '''
class AssetEngine:
    def submit(self, row) -> None:
        if row.status != AssetStatus.DRAFT.value:
            raise InvalidAssetState("Only draft assets can be submitted")
        row.status = AssetStatus.SUBMITTED.value

    def approve(self, row) -> None:
        if row.status != AssetStatus.SUBMITTED.value:
            raise InvalidAssetState("Only submitted assets can be approved")
        row.status = AssetStatus.APPROVED.value

    def activate(self, row) -> None:
        if row.status != AssetStatus.APPROVED.value:
            raise InvalidAssetState("Only approved assets can be activated")
        row.status = AssetStatus.ACTIVE.value

    def dispose(self, row) -> None:
        if row.status in {AssetStatus.DISPOSED.value, AssetStatus.WRITTEN_OFF.value, AssetStatus.CANCELLED.value}:
            raise InvalidAssetState("Asset already terminal")
        row.status = AssetStatus.DISPOSED.value

    def cancel(self, row) -> None:
        if row.status in {AssetStatus.DISPOSED.value, AssetStatus.WRITTEN_OFF.value, AssetStatus.CANCELLED.value}:
            raise InvalidAssetState("Asset already terminal")
        row.status = AssetStatus.CANCELLED.value
''',
    "AssetComponent": '''
class AssetComponentEngine:
    def replace(self, row) -> None:
        if row.status != AssetComponentStatus.ACTIVE.value:
            raise InvalidAssetComponentState("Only active components can be replaced")
        row.status = AssetComponentStatus.REPLACED.value

    def dispose(self, row) -> None:
        row.status = AssetComponentStatus.DISPOSED.value
''',
    "AssetAssignment": '''
class AssetAssignmentEngine:
    def submit(self, row) -> None:
        if row.status != AssetAssignmentStatus.DRAFT.value:
            raise InvalidAssetAssignmentState("Only draft assignments can be submitted")
        row.status = AssetAssignmentStatus.SUBMITTED.value

    def approve(self, row) -> None:
        if row.status != AssetAssignmentStatus.SUBMITTED.value:
            raise InvalidAssetAssignmentState("Only submitted assignments can be approved")
        row.status = AssetAssignmentStatus.APPROVED.value

    def activate(self, row) -> None:
        if row.status != AssetAssignmentStatus.APPROVED.value:
            raise InvalidAssetAssignmentState("Only approved assignments can be activated")
        row.status = AssetAssignmentStatus.ACTIVE.value

    def return_assignment(self, row) -> None:
        if row.status != AssetAssignmentStatus.ACTIVE.value:
            raise InvalidAssetAssignmentState("Only active assignments can be returned")
        row.status = AssetAssignmentStatus.RETURNED.value
''',
    "AssetTransfer": '''
class AssetTransferEngine:
    def complete(self, row) -> None:
        if row.status != AssetTransferStatus.DRAFT.value:
            raise InvalidAssetTransferState("Only draft transfers can be completed")
        row.status = AssetTransferStatus.COMPLETED.value

    def cancel(self, row) -> None:
        if row.status == AssetTransferStatus.COMPLETED.value:
            raise InvalidAssetTransferState("Completed transfers cannot be cancelled")
        row.status = AssetTransferStatus.CANCELLED.value
''',
    "AssetLocation": '''
class AssetLocationEngine:
    def mark_historical(self, row) -> None:
        row.status = AssetLocationStatus.HISTORICAL.value
        row.is_current = False
''',
    "AssetWarranty": '''
class AssetWarrantyEngine:
    def expire(self, row) -> None:
        row.status = AssetWarrantyStatus.EXPIRED.value

    def void(self, row) -> None:
        row.status = AssetWarrantyStatus.VOID.value
''',
    "AssetInsurance": '''
class AssetInsuranceEngine:
    def expire(self, row) -> None:
        row.status = AssetInsuranceStatus.EXPIRED.value

    def cancel(self, row) -> None:
        row.status = AssetInsuranceStatus.CANCELLED.value
''',
    "AssetMaintenancePlan": '''
class AssetMaintenancePlanEngine:
    def activate(self, row) -> None:
        if row.status != AssetMaintenancePlanStatus.DRAFT.value:
            raise InvalidAssetMaintenancePlanState("Only draft plans can be activated")
        row.status = AssetMaintenancePlanStatus.ACTIVE.value

    def pause(self, row) -> None:
        if row.status != AssetMaintenancePlanStatus.ACTIVE.value:
            raise InvalidAssetMaintenancePlanState("Only active plans can be paused")
        row.status = AssetMaintenancePlanStatus.PAUSED.value

    def close(self, row) -> None:
        row.status = AssetMaintenancePlanStatus.CLOSED.value
''',
    "AssetMaintenance": '''
class AssetMaintenanceEngine:
    def submit(self, row) -> None:
        if row.status != AssetMaintenanceStatus.DRAFT.value:
            raise InvalidAssetMaintenanceState("Only draft maintenance can be submitted")
        row.status = AssetMaintenanceStatus.SUBMITTED.value

    def approve(self, row) -> None:
        if row.status != AssetMaintenanceStatus.SUBMITTED.value:
            raise InvalidAssetMaintenanceState("Only submitted maintenance can be approved")
        row.status = AssetMaintenanceStatus.APPROVED.value

    def schedule(self, row) -> None:
        if row.status != AssetMaintenanceStatus.APPROVED.value:
            raise InvalidAssetMaintenanceState("Only approved maintenance can be scheduled")
        row.status = AssetMaintenanceStatus.SCHEDULED.value

    def start(self, row) -> None:
        if row.status not in {AssetMaintenanceStatus.APPROVED.value, AssetMaintenanceStatus.SCHEDULED.value}:
            raise InvalidAssetMaintenanceState("Maintenance not startable")
        row.status = AssetMaintenanceStatus.IN_PROGRESS.value

    def complete(self, row) -> None:
        if row.status != AssetMaintenanceStatus.IN_PROGRESS.value:
            raise InvalidAssetMaintenanceState("Only in-progress maintenance can be completed")
        row.status = AssetMaintenanceStatus.COMPLETED.value
''',
    "AssetServiceHistory": '''
class AssetServiceHistoryEngine:
    def record(self, row) -> None:
        row.status = AssetServiceHistoryStatus.RECORDED.value
''',
    "AssetDepreciation": '''
class AssetDepreciationEngine:
    def calculate(self, row) -> None:
        if row.status != AssetDepreciationStatus.DRAFT.value:
            raise InvalidAssetDepreciationState("Only draft depreciation can be calculated")
        row.status = AssetDepreciationStatus.CALCULATED.value

    def post(self, row) -> None:
        if row.status != AssetDepreciationStatus.CALCULATED.value:
            raise InvalidAssetDepreciationState("Only calculated depreciation can be posted")
        row.status = AssetDepreciationStatus.POSTED.value

    def fail(self, row) -> None:
        row.status = AssetDepreciationStatus.FAILED.value

    def reverse(self, row) -> None:
        if row.status != AssetDepreciationStatus.POSTED.value:
            raise InvalidAssetDepreciationState("Only posted depreciation can be reversed")
        row.status = AssetDepreciationStatus.REVERSED.value
''',
    "AssetDisposal": '''
class AssetDisposalEngine:
    def submit(self, row) -> None:
        if row.status != AssetDisposalStatus.DRAFT.value:
            raise InvalidAssetDisposalState("Only draft disposals can be submitted")
        row.status = AssetDisposalStatus.SUBMITTED.value

    def approve(self, row) -> None:
        if row.status != AssetDisposalStatus.SUBMITTED.value:
            raise InvalidAssetDisposalState("Only submitted disposals can be approved")
        row.status = AssetDisposalStatus.APPROVED.value

    def post(self, row) -> None:
        if row.status != AssetDisposalStatus.APPROVED.value:
            raise InvalidAssetDisposalState("Only approved disposals can be posted")
        row.status = AssetDisposalStatus.POSTED.value
''',
    "AssetRevaluation": '''
class AssetRevaluationEngine:
    def submit(self, row) -> None:
        if row.status != AssetRevaluationStatus.DRAFT.value:
            raise InvalidAssetRevaluationState("Only draft revaluations can be submitted")
        row.status = AssetRevaluationStatus.SUBMITTED.value

    def approve(self, row) -> None:
        if row.status != AssetRevaluationStatus.SUBMITTED.value:
            raise InvalidAssetRevaluationState("Only submitted revaluations can be approved")
        row.status = AssetRevaluationStatus.APPROVED.value

    def post(self, row) -> None:
        if row.status != AssetRevaluationStatus.APPROVED.value:
            raise InvalidAssetRevaluationState("Only approved revaluations can be posted")
        row.status = AssetRevaluationStatus.POSTED.value
''',
    "AssetAudit": '''
class AssetAuditEngine:
    def start(self, row) -> None:
        if row.status != AssetAuditStatus.PLANNED.value:
            raise InvalidAssetAuditState("Only planned audits can be started")
        row.status = AssetAuditStatus.IN_PROGRESS.value

    def complete(self, row) -> None:
        if row.status != AssetAuditStatus.IN_PROGRESS.value:
            raise InvalidAssetAuditState("Only in-progress audits can be completed")
        row.status = AssetAuditStatus.COMPLETED.value

    def cancel(self, row) -> None:
        if row.status == AssetAuditStatus.COMPLETED.value:
            raise InvalidAssetAuditState("Completed audits cannot be cancelled")
        row.status = AssetAuditStatus.CANCELLED.value
''',
    "AssetDocument": '''
class AssetDocumentEngine:
    def supersede(self, row) -> None:
        row.status = AssetDocumentStatus.SUPERSEDED.value

    def archive(self, row) -> None:
        row.status = AssetDocumentStatus.ARCHIVED.value
''',
    "AssetChecklist": '''
class AssetChecklistEngine:
    def complete(self, row) -> None:
        if row.status != AssetChecklistStatus.DRAFT.value:
            raise InvalidAssetChecklistState("Only draft checklists can be completed")
        row.status = AssetChecklistStatus.COMPLETED.value

    def cancel(self, row) -> None:
        row.status = AssetChecklistStatus.CANCELLED.value
''',
    "AssetMeterReading": '''
class AssetMeterReadingEngine:
    def void(self, row) -> None:
        if row.status != AssetMeterReadingStatus.RECORDED.value:
            raise InvalidAssetMeterReadingState("Only recorded readings can be voided")
        row.status = AssetMeterReadingStatus.VOID.value
''',
    "AssetNotification": '''
class AssetNotificationEngine:
    def archive(self, row) -> None:
        row.status = AssetNotificationStatus.ARCHIVED.value
''',
    "AssetReport": '''
class AssetReportEngine:
    def finalize(self, row) -> None:
        if row.status != AssetReportStatus.DRAFT.value:
            raise InvalidAssetReportState("Only draft reports can be finalized")
        row.status = AssetReportStatus.FINALIZED.value
''',
}


def gen_scaffold() -> None:
    w(AST / "__init__.py", '"""Asset Management module — Sprint 15."""\n')
    w(AST / "domain" / "__init__.py", '"""Asset domain layer."""\n')
    w(AST / "adapters" / "__init__.py", '"""Asset cross-module adapters."""\n')
    w(AST / "service" / "__init__.py", '"""Asset services — populated after generation."""\n')
    w(AST / "service" / "engines" / "__init__.py", '"""Asset engines — populated after generation."""\n')
    w(AST / "repository" / "__init__.py", '"""Asset repositories."""\n')
    w(AST / "models" / "__init__.py", '"""Asset models — populated after generation."""\n')
    w(
        AST / "models" / "mixins.py",
        '''"""Asset ORM mixin bundles per ERD_15."""

from database.mixins import (
    AuditMixin,
    BranchMixin,
    CompanyMixin,
    SoftDeleteMixin,
    TenantMixin,
    VersionMixin,
)

AstMasterMixin = (
    AuditMixin,
    TenantMixin,
    CompanyMixin,
    SoftDeleteMixin,
    VersionMixin,
)

AstTransactionMixin = (
    AuditMixin,
    TenantMixin,
    CompanyMixin,
    BranchMixin,
    SoftDeleteMixin,
    VersionMixin,
)

AstDetailMixin = (
    AuditMixin,
    TenantMixin,
    CompanyMixin,
    SoftDeleteMixin,
    VersionMixin,
)
''',
    )


def gen_domain() -> None:
    w(
        AST / "domain" / "enums.py",
        '''"""Asset domain enums per ERD_15 section 11."""

from enum import Enum


class AssetCategoryStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class AssetStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    ACTIVE = "active"
    IN_MAINTENANCE = "in_maintenance"
    TRANSFERRED = "transferred"
    DISPOSED = "disposed"
    WRITTEN_OFF = "written_off"
    CANCELLED = "cancelled"


class AssetComponentStatus(str, Enum):
    ACTIVE = "active"
    REPLACED = "replaced"
    DISPOSED = "disposed"


class AssetAssignmentStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    ACTIVE = "active"
    RETURNED = "returned"
    CANCELLED = "cancelled"


class AssetTransferStatus(str, Enum):
    DRAFT = "draft"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class AssetLocationStatus(str, Enum):
    ACTIVE = "active"
    HISTORICAL = "historical"


class AssetWarrantyStatus(str, Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    VOID = "void"


class AssetInsuranceStatus(str, Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class AssetMaintenancePlanStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    CLOSED = "closed"


class AssetMaintenanceStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class AssetServiceHistoryStatus(str, Enum):
    RECORDED = "recorded"


class AssetDepreciationStatus(str, Enum):
    DRAFT = "draft"
    CALCULATED = "calculated"
    POSTED = "posted"
    FAILED = "failed"
    REVERSED = "reversed"


class AssetDisposalStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    POSTED = "posted"
    CANCELLED = "cancelled"


class AssetRevaluationStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    POSTED = "posted"
    CANCELLED = "cancelled"


class AssetAuditStatus(str, Enum):
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class AssetDocumentStatus(str, Enum):
    ACTIVE = "active"
    SUPERSEDED = "superseded"
    ARCHIVED = "archived"


class AssetChecklistStatus(str, Enum):
    DRAFT = "draft"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class AssetMeterReadingStatus(str, Enum):
    RECORDED = "recorded"
    VOID = "void"


class AssetNotificationStatus(str, Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"


class AssetReportStatus(str, Enum):
    DRAFT = "draft"
    FINALIZED = "finalized"


class AstEntityType(str, Enum):
    ASSET = "asset"
    ASSIGNMENT = "assignment"
    TRANSFER = "transfer"
    MAINTENANCE_PLAN = "maintenance_plan"
    MAINTENANCE = "maintenance"
    DEPRECIATION = "depreciation"
    DISPOSAL = "disposal"
    REVALUATION = "revaluation"
    AUDIT = "audit"
    REPORT = "report"


CODE_PREFIXES: dict[AstEntityType, tuple[str, int, bool]] = {
    AstEntityType.ASSET: ("AST-", 6, True),
    AstEntityType.ASSIGNMENT: ("AASN-", 6, True),
    AstEntityType.TRANSFER: ("ATRF-", 6, True),
    AstEntityType.MAINTENANCE_PLAN: ("AMPL-", 6, True),
    AstEntityType.MAINTENANCE: ("AMNT-", 6, True),
    AstEntityType.DEPRECIATION: ("ADEP-", 6, True),
    AstEntityType.DISPOSAL: ("ADISP-", 6, True),
    AstEntityType.REVALUATION: ("AREV-", 6, True),
    AstEntityType.AUDIT: ("AAUD-", 6, True),
    AstEntityType.REPORT: ("ARPT-", 6, True),
}
''',
    )
    exc_lines = []
    for _, _, name, _ in TABLES:
        exc_lines.append(
            f'''
class Invalid{name}State(ConflictException):
    def __init__(self, message: str = "Invalid {name.lower()} state") -> None:
        super().__init__(message)
'''
        )
    w(
        AST / "domain" / "exceptions.py",
        '"""Asset domain exceptions."""\n\nfrom core.exceptions import ConflictException\n'
        + "".join(exc_lines),
    )
    w(
        AST / "domain" / "value_objects.py",
        '''"""Asset value objects."""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class DepreciationAmount:
    amount: Decimal
    book_value_after: Decimal


@dataclass(frozen=True)
class AssetCodes:
    asset_code: str
    document_number: str
''',
    )
    w(
        AST / "domain" / "entities.py",
        '''"""Asset domain entity markers."""

from dataclasses import dataclass
from uuid import UUID


@dataclass
class AssetIdentity:
    asset_id: UUID
    master_asset_id: UUID | None
    asset_code: str
''',
    )


def gen_models() -> None:
    for key, body in MODELS.items():
        w(AST / "models" / f"{key}.py", body)
    imports = "\n".join(f"from modules.asset.models.{k} import {CLASS_MAP[k]}" for k in CLASS_MAP)
    all_names = ",\n    ".join(f'"{CLASS_MAP[k]}"' for k in CLASS_MAP)
    w(
        AST / "models" / "__init__.py",
        f'"""Asset ORM models."""\n\n{imports}\n\n__all__ = [\n    {all_names},\n]\n',
    )


def gen_migrations() -> None:
    w(
        ALEMBIC / "0245_create_asset_schema.py",
        '''"""Create asset schema."""

from collections.abc import Sequence

from alembic import op

revision: str = "0245_create_asset_schema"
down_revision: str | None = "0244_seed_project_workflows"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS asset")


def downgrade() -> None:
    op.execute("DROP SCHEMA IF EXISTS asset CASCADE")
''',
    )
    for rev, target, down in MIGRATIONS:
        if target == "schema" or (isinstance(target, str) and target.startswith("seed")):
            continue
        if isinstance(target, list):
            imports = "\n".join(
                f"from modules.asset.models.{m} import {CLASS_MAP[m]}  # noqa: F401"
                for m in target
            )
            creates = "\n    ".join(
                f"{CLASS_MAP[m]}.__table__.create(bind=op.get_bind(), checkfirst=True)" for m in target
            )
            drops = "\n    ".join(
                f"{CLASS_MAP[m]}.__table__.drop(bind=op.get_bind(), checkfirst=True)"
                for m in reversed(target)
            )
            w(
                ALEMBIC / f"{rev}.py",
                f'''"""Create asset policy tables."""

import sys
from collections.abc import Sequence
from pathlib import Path

from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

{imports}

revision: str = "{rev}"
down_revision: str | None = "{down}"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    {creates}


def downgrade() -> None:
    {drops}
''',
            )
        else:
            cls = CLASS_MAP[target]
            w(
                ALEMBIC / f"{rev}.py",
                f'''"""Create {cls} table."""

import sys
from collections.abc import Sequence
from pathlib import Path

from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from modules.asset.models.{target} import {cls}  # noqa: F401

revision: str = "{rev}"
down_revision: str | None = "{down}"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    {cls}.__table__.create(bind=op.get_bind(), checkfirst=True)


def downgrade() -> None:
    {cls}.__table__.drop(bind=op.get_bind(), checkfirst=True)
''',
            )


def repo_template(module: str, cls: str, name: str, branch: bool) -> str:
    return f'''"""Asset {cls} repository."""

from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from modules.asset.models import {cls}
from modules.asset.repository.base import AstScopedRepository, utcnow
from modules.foundation.domain.value_objects import TenantContext


class {name}Repository(AstScopedRepository):
    def __init__(self, db: Session) -> None:
        super().__init__(db)

    def get(self, ctx: TenantContext, row_id: UUID) -> {cls} | None:
        stmt = select({cls}).where({cls}.id == row_id, {cls}.is_deleted.is_(False))
        stmt = self.apply_ast_filter(stmt, {cls}, ctx, branch_scoped={branch})
        return self.db.scalar(stmt)

    def list_rows(self, ctx: TenantContext, company_id: UUID):
        stmt = select({cls}).where(
            {cls}.company_id == company_id,
            {cls}.is_deleted.is_(False),
        )
        stmt = self.apply_ast_filter(stmt, {cls}, ctx, branch_scoped={branch})
        return list(self.db.scalars(stmt).all())

    def create(self, ctx: TenantContext, **fields) -> {cls}:
        row = {cls}(
            id=uuid4(),
            tenant_id=ctx.tenant_id,
            created_by=ctx.user_id,
            updated_by=ctx.user_id,
            **fields,
        )
        self.db.add(row)
        self.db.flush()
        return row

    def update(self, ctx: TenantContext, row_id: UUID, **fields) -> {cls} | None:
        row = self.get(ctx, row_id)
        if row is None:
            return None
        for k, v in fields.items():
            if v is not None:
                setattr(row, k, v)
        row.updated_at = utcnow()
        row.updated_by = ctx.user_id
        if hasattr(row, "version"):
            row.version = int(row.version or 1) + 1
        self.db.flush()
        return row
'''


def gen_repos() -> None:
    w(
        AST / "repository" / "base.py",
        '''"""Asset scoped repository base."""

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import ForbiddenException
from modules.foundation.domain.value_objects import TenantContext
from modules.organization.repository.base import OrgScopedRepository


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class AstScopedRepository(OrgScopedRepository):
    def __init__(self, db: Session) -> None:
        super().__init__(db)

    @staticmethod
    def apply_ast_filter(stmt, model, ctx: TenantContext, *, branch_scoped: bool = False):
        stmt = AstScopedRepository.apply_tenant_filter(stmt, model, ctx)
        if ctx.company_id and ctx.user_type not in {"super_admin", "tenant_admin"}:
            stmt = stmt.where(model.company_id == ctx.company_id)
        if (
            branch_scoped
            and ctx.branch_id
            and ctx.user_type not in {"super_admin", "tenant_admin"}
            and hasattr(model, "branch_id")
        ):
            stmt = stmt.where(model.branch_id == ctx.branch_id)
        return stmt

    @staticmethod
    def resolve_company_id(ctx: TenantContext, company_id: UUID | None) -> UUID:
        if company_id is not None:
            AstScopedRepository.ensure_company_access(ctx, company_id)
            return company_id
        if ctx.company_id is None:
            raise ForbiddenException("Company context required")
        return ctx.company_id
''',
    )
    w(
        AST / "repository" / "code_sequence_repository.py",
        '''"""Asset document code sequences."""

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from modules.asset.domain.enums import CODE_PREFIXES, AstEntityType


class CodeSequenceRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def next_code(self, entity: AstEntityType, company_id: UUID, model, code_column: str) -> str:
        prefix, width, include_year = CODE_PREFIXES[entity]
        year = datetime.now(timezone.utc).year
        full_prefix = f"{prefix}{year}-" if include_year else prefix
        stmt = select(getattr(model, code_column)).where(
            model.company_id == company_id,
            getattr(model, code_column).like(f"{full_prefix}%"),
            model.is_deleted.is_(False),
        )
        existing = list(self.db.scalars(stmt).all())
        seq = 1
        if existing:
            nums = []
            for code in existing:
                try:
                    nums.append(int(str(code).rsplit("-", 1)[-1]))
                except ValueError:
                    continue
            if nums:
                seq = max(nums) + 1
        return f"{full_prefix}{seq:0{width}d}"
''',
    )
    for module, cls, name, branch in TABLES:
        w(AST / "repository" / f"{module}_repository.py", repo_template(module, cls, name, branch))


def gen_engines() -> None:
    for eng_name, body in ENGINE_BODIES.items():
        fname = ENGINE_FILE_MAP[eng_name]
        w(
            AST / "service" / "engines" / f"{fname}_engine.py",
            f'"""{eng_name} lifecycle engine."""\n{ENGINE_IMPORTS}\n{body}\n',
        )
    lines = [
        f"from modules.asset.service.engines.{ENGINE_FILE_MAP[n]}_engine import {n}Engine"
        for n in ENGINE_BODIES
    ]
    all_names = ",\n    ".join(f'"{n}Engine"' for n in ENGINE_BODIES)
    w(
        AST / "service" / "engines" / "__init__.py",
        '"""Asset business engines."""\n\n'
        + "\n".join(lines)
        + f"\n\n__all__ = [\n    {all_names},\n]\n",
    )


def catalog_service(
    svc_name: str,
    cls: str,
    repo_name: str,
    entity: str,
    branch: bool,
    engine_name: str | None = None,
) -> str:
    eng = engine_name or repo_name
    branch_arg = ", *, branch_id: UUID | None = None" if branch else ""
    branch_fields = (
        "\n        if branch_id is not None:\n"
        "            self._scope.validate_branch_access(ctx, branch_id)\n"
        if branch
        else ""
    )
    branch_create = "branch_id=branch_id," if branch else ""
    return f'''"""{svc_name} application service."""

from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import NotFoundException
from modules.asset.models import {cls}
from modules.asset.repository.{entity}_repository import {repo_name}Repository
from modules.asset.service.asset_scope_validator import AssetScopeValidator
from modules.asset.service.engines import {eng}Engine
from modules.foundation.domain.value_objects import TenantContext
from modules.foundation.service.audit_service import AuditService


class {svc_name}:
    def __init__(self, db: Session) -> None:
        self._repo = {repo_name}Repository(db)
        self._scope = AssetScopeValidator(db)
        self._engine = {eng}Engine()
        self._audit = AuditService(db)

    def list(self, ctx: TenantContext, company_id: UUID | None = None):
        cid = self._scope.resolve_company_id(ctx, company_id)
        return self._repo.list_rows(ctx, cid)

    def get(self, ctx: TenantContext, row_id: UUID) -> {cls}:
        row = self._repo.get(ctx, row_id)
        if row is None:
            raise NotFoundException("{svc_name} not found")
        return row

    def create(self, ctx: TenantContext, company_id: UUID | None = None{branch_arg}, **fields):
        cid = self._scope.resolve_company_id(ctx, company_id)
{branch_fields}
        row = self._repo.create(ctx, company_id=cid, {branch_create} **fields)
        self._audit.log_entity_change(
            tenant_id=ctx.tenant_id,
            entity_name="ast_{entity}",
            entity_id=row.id,
            operation="create",
            performed_by=ctx.user_id,
        )
        return row

    def update(self, ctx: TenantContext, row_id: UUID, **fields):
        self.get(ctx, row_id)
        row = self._repo.update(ctx, row_id, **fields)
        if row is None:
            raise NotFoundException("{svc_name} not found")
        return row
'''


def numbered_service(
    svc_name: str,
    cls: str,
    repo_name: str,
    entity: str,
    entity_type: str,
    code_col: str,
    branch_required: bool,
    engine_name: str,
    actions: list[str],
) -> str:
    if branch_required:
        create_body = f'''
        cid = self._scope.resolve_company_id(ctx, company_id)
        self._scope.validate_branch_access(ctx, branch_id)
        doc = self._numbers.generate(AstEntityType.{entity_type}, cid, {cls}, "{code_col}")
        return self._repo.create(ctx, company_id=cid, branch_id=branch_id, {code_col}=doc, **fields)
'''
        create_sig = "self, ctx: TenantContext, *, branch_id: UUID, company_id: UUID | None = None, **fields"
    else:
        create_body = f'''
        cid = self._scope.resolve_company_id(ctx, company_id)
        doc = self._numbers.generate(AstEntityType.{entity_type}, cid, {cls}, "{code_col}")
        return self._repo.create(ctx, company_id=cid, {code_col}=doc, **fields)
'''
        create_sig = "self, ctx: TenantContext, company_id: UUID | None = None, **fields"

    action_methods = ""
    for act in actions:
        method = "return_assignment" if act == "return_" else act
        engine_call = "return_assignment" if act == "return_" else act
        action_methods += f'''
    def {method}(self, ctx: TenantContext, row_id: UUID):
        row = self.get(ctx, row_id)
        self._engine.{engine_call}(row)
        return self._repo.update(ctx, row_id, status=row.status)
'''

    return f'''"""{svc_name}."""

from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import NotFoundException
from modules.asset.domain.enums import AstEntityType
from modules.asset.models import {cls}
from modules.asset.repository.{entity}_repository import {repo_name}Repository
from modules.asset.service.asset_scope_validator import AssetScopeValidator
from modules.asset.service.document_number_service import DocumentNumberService
from modules.asset.service.engines import {engine_name}Engine
from modules.foundation.domain.value_objects import TenantContext
from modules.foundation.service.audit_service import AuditService


class {svc_name}:
    def __init__(self, db: Session) -> None:
        self._repo = {repo_name}Repository(db)
        self._scope = AssetScopeValidator(db)
        self._numbers = DocumentNumberService(db)
        self._engine = {engine_name}Engine()
        self._audit = AuditService(db)
        self._db = db

    def list(self, ctx: TenantContext, company_id: UUID | None = None):
        cid = self._scope.resolve_company_id(ctx, company_id)
        return self._repo.list_rows(ctx, cid)

    def get(self, ctx: TenantContext, row_id: UUID) -> {cls}:
        row = self._repo.get(ctx, row_id)
        if row is None:
            raise NotFoundException("{svc_name} not found")
        return row

    def create({create_sig}):
{create_body}
    def update(self, ctx: TenantContext, row_id: UUID, **fields):
        self.get(ctx, row_id)
        row = self._repo.update(ctx, row_id, **fields)
        if row is None:
            raise NotFoundException("{svc_name} not found")
        return row
{action_methods}
'''

def gen_services() -> None:
    w(
        AST / "service" / "asset_scope_validator.py",
        '''"""Asset scope validator."""

from uuid import UUID

from sqlalchemy.orm import Session

from modules.asset.repository.base import AstScopedRepository
from modules.foundation.domain.value_objects import TenantContext


class AssetScopeValidator(AstScopedRepository):
    def __init__(self, db: Session) -> None:
        super().__init__(db)

    def validate_company_access(self, ctx: TenantContext, company_id: UUID) -> None:
        self.ensure_company_access(ctx, company_id)

    def validate_branch_access(self, ctx: TenantContext, branch_id: UUID) -> None:
        self.ensure_branch_access(ctx, branch_id)
''',
    )
    w(
        AST / "service" / "document_number_service.py",
        '''"""Asset document numbering."""

from uuid import UUID

from sqlalchemy.orm import Session

from modules.asset.domain.enums import AstEntityType
from modules.asset.repository.code_sequence_repository import CodeSequenceRepository


class DocumentNumberService:
    def __init__(self, db: Session) -> None:
        self._seq = CodeSequenceRepository(db)

    def generate(self, entity: AstEntityType, company_id: UUID, model, code_column: str) -> str:
        return self._seq.next_code(entity, company_id, model, code_column)
''',
    )

    simple = [
        ("AssetCategoryService", "AstAssetCategory", "AssetCategory", "asset_category", False, "AssetCategory"),
        ("ComponentService", "AstAssetComponent", "AssetComponent", "asset_component", False, "AssetComponent"),
        ("LocationService", "AstAssetLocation", "AssetLocation", "asset_location", False, "AssetLocation"),
        ("WarrantyService", "AstAssetWarranty", "AssetWarranty", "asset_warranty", False, "AssetWarranty"),
        ("InsuranceService", "AstAssetInsurance", "AssetInsurance", "asset_insurance", False, "AssetInsurance"),
        ("ServiceHistoryService", "AstAssetServiceHistory", "AssetServiceHistory", "asset_service_history", False, "AssetServiceHistory"),
        ("DocumentService", "AstAssetDocument", "AssetDocument", "asset_document", False, "AssetDocument"),
        ("ChecklistService", "AstAssetChecklist", "AssetChecklist", "asset_checklist", False, "AssetChecklist"),
        ("MeterReadingService", "AstAssetMeterReading", "AssetMeterReading", "asset_meter_reading", False, "AssetMeterReading"),
        ("NotificationService", "AstAssetNotification", "AssetNotification", "asset_notification", False, "AssetNotification"),
    ]
    file_map_simple = {
        "AssetCategoryService": "asset_category_service.py",
        "ComponentService": "component_service.py",
        "LocationService": "location_service.py",
        "WarrantyService": "warranty_service.py",
        "InsuranceService": "insurance_service.py",
        "ServiceHistoryService": "service_history_service.py",
        "DocumentService": "document_service.py",
        "ChecklistService": "checklist_service.py",
        "MeterReadingService": "meter_reading_service.py",
        "NotificationService": "notification_service.py",
    }
    for svc, cls, repo, entity, branch, eng in simple:
        w(AST / "service" / file_map_simple[svc], catalog_service(svc, cls, repo, entity, branch, eng))

    # AssetService with master_asset link on approve
    w(
        AST / "service" / "asset_service.py",
        '''"""Asset register service — C-01 master_asset link on approve."""

from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import NotFoundException
from modules.asset.adapters.master_data_port import AssetMasterDataAdapter
from modules.asset.domain.enums import AstEntityType
from modules.asset.models import AstAsset
from modules.asset.repository.asset_repository import AssetRepository
from modules.asset.service.asset_scope_validator import AssetScopeValidator
from modules.asset.service.document_number_service import DocumentNumberService
from modules.asset.service.engines import AssetEngine
from modules.foundation.domain.value_objects import TenantContext
from modules.foundation.service.audit_service import AuditService


class AssetService:
    def __init__(self, db: Session) -> None:
        self._repo = AssetRepository(db)
        self._scope = AssetScopeValidator(db)
        self._numbers = DocumentNumberService(db)
        self._engine = AssetEngine()
        self._audit = AuditService(db)
        self._master = AssetMasterDataAdapter(db)
        self._db = db

    def list(self, ctx: TenantContext, company_id: UUID | None = None):
        cid = self._scope.resolve_company_id(ctx, company_id)
        return self._repo.list_rows(ctx, cid)

    def get(self, ctx: TenantContext, row_id: UUID) -> AstAsset:
        row = self._repo.get(ctx, row_id)
        if row is None:
            raise NotFoundException("AssetService not found")
        return row

    def create(self, ctx: TenantContext, *, branch_id: UUID, company_id: UUID | None = None, **fields):
        cid = self._scope.resolve_company_id(ctx, company_id)
        self._scope.validate_branch_access(ctx, branch_id)
        doc = self._numbers.generate(AstEntityType.ASSET, cid, AstAsset, "document_number")
        asset_code = fields.pop("asset_code", None) or doc
        return self._repo.create(
            ctx,
            company_id=cid,
            branch_id=branch_id,
            document_number=doc,
            asset_code=asset_code,
            **fields,
        )

    def update(self, ctx: TenantContext, row_id: UUID, **fields):
        self.get(ctx, row_id)
        row = self._repo.update(ctx, row_id, **fields)
        if row is None:
            raise NotFoundException("AssetService not found")
        return row

    def submit(self, ctx: TenantContext, row_id: UUID):
        row = self.get(ctx, row_id)
        self._engine.submit(row)
        return self._repo.update(ctx, row_id, status=row.status)

    def approve(self, ctx: TenantContext, row_id: UUID):
        row = self.get(ctx, row_id)
        self._engine.approve(row)
        if row.master_asset_id is None:
            master = self._master.create_or_link_master_asset(ctx, row)
            row.master_asset_id = master.id
        self._engine.activate(row)
        updated = self._repo.update(
            ctx,
            row_id,
            status=row.status,
            master_asset_id=row.master_asset_id,
        )
        self._audit.log_entity_change(
            tenant_id=ctx.tenant_id,
            entity_name="ast_asset",
            entity_id=row_id,
            operation="approve",
            performed_by=ctx.user_id,
            new_value={"master_asset_id": str(row.master_asset_id), "status": row.status},
        )
        return updated
''',
    )

    w(
        AST / "service" / "assignment_service.py",
        numbered_service(
            "AssignmentService",
            "AstAssetAssignment",
            "AssetAssignment",
            "asset_assignment",
            "ASSIGNMENT",
            "document_number",
            True,
            "AssetAssignment",
            ["submit", "approve", "return_"],
        ),
    )
    # Fix return_ method name in assignment - the numbered_service maps return_ to return_assignment
    # Fix activate after approve for assignment
    w(
        AST / "service" / "transfer_service.py",
        numbered_service(
            "TransferService",
            "AstAssetTransfer",
            "AssetTransfer",
            "asset_transfer",
            "TRANSFER",
            "document_number",
            True,
            "AssetTransfer",
            ["complete"],
        ),
    )
    w(
        AST / "service" / "maintenance_plan_service.py",
        numbered_service(
            "MaintenancePlanService",
            "AstAssetMaintenancePlan",
            "AssetMaintenancePlan",
            "asset_maintenance_plan",
            "MAINTENANCE_PLAN",
            "document_number",
            False,
            "AssetMaintenancePlan",
            ["activate", "pause", "close"],
        ),
    )
    w(
        AST / "service" / "maintenance_service.py",
        numbered_service(
            "MaintenanceService",
            "AstAssetMaintenance",
            "AssetMaintenance",
            "asset_maintenance",
            "MAINTENANCE",
            "document_number",
            True,
            "AssetMaintenance",
            ["submit", "approve", "complete"],
        ),
    )
    w(
        AST / "service" / "asset_audit_service.py",
        numbered_service(
            "AssetAuditService",
            "AstAssetAudit",
            "AssetAudit",
            "asset_audit",
            "AUDIT",
            "document_number",
            True,
            "AssetAudit",
            ["complete"],
        ),
    )
    w(
        AST / "service" / "asset_report_service.py",
        numbered_service(
            "AssetReportService",
            "AstAssetReport",
            "AssetReport",
            "asset_report",
            "REPORT",
            "report_code",
            False,
            "AssetReport",
            ["finalize"],
        ),
    )

    w(
        AST / "service" / "depreciation_service.py",
        '''"""Depreciation service — posts via Finance PostingService only."""

from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy.orm import Session

from core.exceptions import NotFoundException
from modules.asset.adapters.finance_port import AssetFinanceAdapter
from modules.asset.domain.enums import AstEntityType
from modules.asset.models import AstAssetDepreciation
from modules.asset.repository.asset_depreciation_repository import AssetDepreciationRepository
from modules.asset.service.asset_scope_validator import AssetScopeValidator
from modules.asset.service.document_number_service import DocumentNumberService
from modules.asset.service.engines import AssetDepreciationEngine
from modules.foundation.domain.value_objects import TenantContext
from modules.foundation.service.audit_service import AuditService


class DepreciationService:
    def __init__(self, db: Session) -> None:
        self._repo = AssetDepreciationRepository(db)
        self._scope = AssetScopeValidator(db)
        self._numbers = DocumentNumberService(db)
        self._engine = AssetDepreciationEngine()
        self._finance = AssetFinanceAdapter(db)
        self._audit = AuditService(db)

    def list(self, ctx: TenantContext, company_id: UUID | None = None):
        cid = self._scope.resolve_company_id(ctx, company_id)
        return self._repo.list_rows(ctx, cid)

    def get(self, ctx: TenantContext, row_id: UUID) -> AstAssetDepreciation:
        row = self._repo.get(ctx, row_id)
        if row is None:
            raise NotFoundException("DepreciationService not found")
        return row

    def create(self, ctx: TenantContext, company_id: UUID | None = None, **fields):
        cid = self._scope.resolve_company_id(ctx, company_id)
        doc = self._numbers.generate(
            AstEntityType.DEPRECIATION, cid, AstAssetDepreciation, "document_number"
        )
        fields.setdefault("idempotency_key", str(uuid4()))
        return self._repo.create(ctx, company_id=cid, document_number=doc, **fields)

    def update(self, ctx: TenantContext, row_id: UUID, **fields):
        self.get(ctx, row_id)
        row = self._repo.update(ctx, row_id, **fields)
        if row is None:
            raise NotFoundException("DepreciationService not found")
        return row

    def calculate(self, ctx: TenantContext, row_id: UUID):
        row = self.get(ctx, row_id)
        self._engine.calculate(row)
        return self._repo.update(ctx, row_id, status=row.status)

    def post(
        self,
        ctx: TenantContext,
        row_id: UUID,
        debit_account_id: UUID,
        credit_account_id: UUID,
        fiscal_year_id: UUID | None = None,
    ):
        row = self.get(ctx, row_id)
        try:
            journal_id = self._finance.post_depreciation(
                ctx,
                row,
                amount=Decimal(str(row.depreciation_amount or 0)),
                debit_account_id=debit_account_id,
                credit_account_id=credit_account_id,
                fiscal_year_id=fiscal_year_id,
            )
            self._engine.post(row)
            updated = self._repo.update(
                ctx, row_id, status=row.status, finance_journal_id=journal_id
            )
            self._audit.log_entity_change(
                tenant_id=ctx.tenant_id,
                entity_name="ast_asset_depreciation",
                entity_id=row_id,
                operation="post",
                performed_by=ctx.user_id,
                new_value={"finance_journal_id": str(journal_id)},
            )
            return updated
        except Exception:
            self._engine.fail(row)
            self._repo.update(ctx, row_id, status=row.status)
            raise
''',
    )

    w(
        AST / "service" / "disposal_service.py",
        '''"""Disposal service — Finance post + master sync."""

from decimal import Decimal
from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import NotFoundException
from modules.asset.adapters.finance_port import AssetFinanceAdapter
from modules.asset.adapters.master_data_port import AssetMasterDataAdapter
from modules.asset.domain.enums import AstEntityType
from modules.asset.models import AstAssetDisposal
from modules.asset.repository.asset_disposal_repository import AssetDisposalRepository
from modules.asset.repository.asset_repository import AssetRepository
from modules.asset.service.asset_scope_validator import AssetScopeValidator
from modules.asset.service.document_number_service import DocumentNumberService
from modules.asset.service.engines import AssetDisposalEngine, AssetEngine
from modules.foundation.domain.value_objects import TenantContext
from modules.foundation.service.audit_service import AuditService


class DisposalService:
    def __init__(self, db: Session) -> None:
        self._repo = AssetDisposalRepository(db)
        self._assets = AssetRepository(db)
        self._scope = AssetScopeValidator(db)
        self._numbers = DocumentNumberService(db)
        self._engine = AssetDisposalEngine()
        self._asset_engine = AssetEngine()
        self._finance = AssetFinanceAdapter(db)
        self._master = AssetMasterDataAdapter(db)
        self._audit = AuditService(db)

    def list(self, ctx: TenantContext, company_id: UUID | None = None):
        cid = self._scope.resolve_company_id(ctx, company_id)
        return self._repo.list_rows(ctx, cid)

    def get(self, ctx: TenantContext, row_id: UUID) -> AstAssetDisposal:
        row = self._repo.get(ctx, row_id)
        if row is None:
            raise NotFoundException("DisposalService not found")
        return row

    def create(self, ctx: TenantContext, *, branch_id: UUID, company_id: UUID | None = None, **fields):
        cid = self._scope.resolve_company_id(ctx, company_id)
        self._scope.validate_branch_access(ctx, branch_id)
        doc = self._numbers.generate(AstEntityType.DISPOSAL, cid, AstAssetDisposal, "document_number")
        return self._repo.create(ctx, company_id=cid, branch_id=branch_id, document_number=doc, **fields)

    def update(self, ctx: TenantContext, row_id: UUID, **fields):
        self.get(ctx, row_id)
        row = self._repo.update(ctx, row_id, **fields)
        if row is None:
            raise NotFoundException("DisposalService not found")
        return row

    def submit(self, ctx: TenantContext, row_id: UUID):
        row = self.get(ctx, row_id)
        self._engine.submit(row)
        return self._repo.update(ctx, row_id, status=row.status)

    def approve(self, ctx: TenantContext, row_id: UUID):
        row = self.get(ctx, row_id)
        self._engine.approve(row)
        return self._repo.update(ctx, row_id, status=row.status)

    def post(
        self,
        ctx: TenantContext,
        row_id: UUID,
        debit_account_id: UUID,
        credit_account_id: UUID,
        fiscal_year_id: UUID | None = None,
    ):
        row = self.get(ctx, row_id)
        journal_id = self._finance.post_disposal(
            ctx,
            row,
            amount=Decimal(str(row.book_value_at_disposal or row.proceeds_amount or 0)),
            debit_account_id=debit_account_id,
            credit_account_id=credit_account_id,
            fiscal_year_id=fiscal_year_id,
        )
        self._engine.post(row)
        updated = self._repo.update(ctx, row_id, status=row.status, finance_journal_id=journal_id)
        asset = self._assets.get(ctx, row.asset_id)
        if asset is not None:
            self._asset_engine.dispose(asset)
            self._assets.update(ctx, asset.id, status=asset.status)
            if asset.master_asset_id is not None:
                self._master.mark_master_disposed(ctx, asset.master_asset_id)
        self._audit.log_entity_change(
            tenant_id=ctx.tenant_id,
            entity_name="ast_asset_disposal",
            entity_id=row_id,
            operation="post",
            performed_by=ctx.user_id,
            new_value={"finance_journal_id": str(journal_id)},
        )
        return updated
''',
    )

    w(
        AST / "service" / "revaluation_service.py",
        '''"""Revaluation service — Finance post only via PostingService."""

from decimal import Decimal
from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import NotFoundException
from modules.asset.adapters.finance_port import AssetFinanceAdapter
from modules.asset.domain.enums import AstEntityType
from modules.asset.models import AstAssetRevaluation
from modules.asset.repository.asset_revaluation_repository import AssetRevaluationRepository
from modules.asset.service.asset_scope_validator import AssetScopeValidator
from modules.asset.service.document_number_service import DocumentNumberService
from modules.asset.service.engines import AssetRevaluationEngine
from modules.foundation.domain.value_objects import TenantContext
from modules.foundation.service.audit_service import AuditService


class RevaluationService:
    def __init__(self, db: Session) -> None:
        self._repo = AssetRevaluationRepository(db)
        self._scope = AssetScopeValidator(db)
        self._numbers = DocumentNumberService(db)
        self._engine = AssetRevaluationEngine()
        self._finance = AssetFinanceAdapter(db)
        self._audit = AuditService(db)

    def list(self, ctx: TenantContext, company_id: UUID | None = None):
        cid = self._scope.resolve_company_id(ctx, company_id)
        return self._repo.list_rows(ctx, cid)

    def get(self, ctx: TenantContext, row_id: UUID) -> AstAssetRevaluation:
        row = self._repo.get(ctx, row_id)
        if row is None:
            raise NotFoundException("RevaluationService not found")
        return row

    def create(self, ctx: TenantContext, *, branch_id: UUID, company_id: UUID | None = None, **fields):
        cid = self._scope.resolve_company_id(ctx, company_id)
        self._scope.validate_branch_access(ctx, branch_id)
        doc = self._numbers.generate(
            AstEntityType.REVALUATION, cid, AstAssetRevaluation, "document_number"
        )
        return self._repo.create(ctx, company_id=cid, branch_id=branch_id, document_number=doc, **fields)

    def update(self, ctx: TenantContext, row_id: UUID, **fields):
        self.get(ctx, row_id)
        row = self._repo.update(ctx, row_id, **fields)
        if row is None:
            raise NotFoundException("RevaluationService not found")
        return row

    def submit(self, ctx: TenantContext, row_id: UUID):
        row = self.get(ctx, row_id)
        self._engine.submit(row)
        return self._repo.update(ctx, row_id, status=row.status)

    def approve(self, ctx: TenantContext, row_id: UUID):
        row = self.get(ctx, row_id)
        self._engine.approve(row)
        return self._repo.update(ctx, row_id, status=row.status)

    def post(
        self,
        ctx: TenantContext,
        row_id: UUID,
        debit_account_id: UUID,
        credit_account_id: UUID,
        fiscal_year_id: UUID | None = None,
    ):
        row = self.get(ctx, row_id)
        amount = Decimal(str(row.new_book_value or 0)) - Decimal(str(row.old_book_value or 0))
        journal_id = self._finance.post_revaluation(
            ctx,
            row,
            amount=abs(amount),
            debit_account_id=debit_account_id,
            credit_account_id=credit_account_id,
            fiscal_year_id=fiscal_year_id,
        )
        self._engine.post(row)
        updated = self._repo.update(ctx, row_id, status=row.status, finance_journal_id=journal_id)
        self._audit.log_entity_change(
            tenant_id=ctx.tenant_id,
            entity_name="ast_asset_revaluation",
            entity_id=row_id,
            operation="post",
            performed_by=ctx.user_id,
            new_value={"finance_journal_id": str(journal_id)},
        )
        return updated
''',
    )

    w(
        AST / "service" / "integration_service.py",
        '''"""Asset integration service — cross-module reads / master create only."""

from uuid import UUID

from sqlalchemy.orm import Session

from modules.asset.adapters.master_data_port import AssetMasterDataAdapter
from modules.asset.adapters.organization_port import AssetOrganizationAdapter
from modules.asset.adapters.payroll_port import AssetPayrollAdapter
from modules.foundation.domain.value_objects import TenantContext


class AssetIntegrationService:
    def __init__(self, db: Session) -> None:
        self._master = AssetMasterDataAdapter(db)
        self._org = AssetOrganizationAdapter(db)
        self._payroll = AssetPayrollAdapter(db)

    def get_employee(self, ctx: TenantContext, employee_id: UUID):
        return self._master.get_employee(ctx, employee_id)

    def get_product(self, ctx: TenantContext, product_id: UUID):
        return self._master.get_product(ctx, product_id)

    def get_vendor(self, ctx: TenantContext, vendor_id: UUID):
        return self._master.get_vendor(ctx, vendor_id)

    def get_department(self, ctx: TenantContext, department_id: UUID):
        return self._org.get_department(ctx, department_id)

    def labor_cost_hint(self, ctx: TenantContext, employee_id: UUID):
        return self._payroll.labor_cost_hint(ctx, employee_id)
''',
    )

    w(
        AST / "service" / "application_service.py",
        '''"""Asset application service facade."""

from sqlalchemy.orm import Session

from modules.asset.service.asset_audit_service import AssetAuditService
from modules.asset.service.asset_category_service import AssetCategoryService
from modules.asset.service.asset_report_service import AssetReportService
from modules.asset.service.asset_service import AssetService
from modules.asset.service.assignment_service import AssignmentService
from modules.asset.service.checklist_service import ChecklistService
from modules.asset.service.component_service import ComponentService
from modules.asset.service.depreciation_service import DepreciationService
from modules.asset.service.disposal_service import DisposalService
from modules.asset.service.document_service import DocumentService
from modules.asset.service.insurance_service import InsuranceService
from modules.asset.service.integration_service import AssetIntegrationService
from modules.asset.service.location_service import LocationService
from modules.asset.service.maintenance_plan_service import MaintenancePlanService
from modules.asset.service.maintenance_service import MaintenanceService
from modules.asset.service.meter_reading_service import MeterReadingService
from modules.asset.service.notification_service import NotificationService
from modules.asset.service.revaluation_service import RevaluationService
from modules.asset.service.service_history_service import ServiceHistoryService
from modules.asset.service.transfer_service import TransferService
from modules.asset.service.warranty_service import WarrantyService


class AssetApplicationService:
    def __init__(self, db: Session) -> None:
        self.categories = AssetCategoryService(db)
        self.assets = AssetService(db)
        self.components = ComponentService(db)
        self.assignments = AssignmentService(db)
        self.transfers = TransferService(db)
        self.locations = LocationService(db)
        self.warranties = WarrantyService(db)
        self.insurances = InsuranceService(db)
        self.maintenance_plans = MaintenancePlanService(db)
        self.maintenances = MaintenanceService(db)
        self.service_histories = ServiceHistoryService(db)
        self.depreciations = DepreciationService(db)
        self.disposals = DisposalService(db)
        self.revaluations = RevaluationService(db)
        self.audits = AssetAuditService(db)
        self.documents = DocumentService(db)
        self.checklists = ChecklistService(db)
        self.meter_readings = MeterReadingService(db)
        self.notifications = NotificationService(db)
        self.reports = AssetReportService(db)
        self.integration = AssetIntegrationService(db)
''',
    )

    svc_exports = [
        "AssetApplicationService",
        "AssetAuditService",
        "AssetCategoryService",
        "AssetIntegrationService",
        "AssetReportService",
        "AssetService",
        "AssignmentService",
        "ChecklistService",
        "ComponentService",
        "DepreciationService",
        "DisposalService",
        "DocumentService",
        "InsuranceService",
        "LocationService",
        "MaintenancePlanService",
        "MaintenanceService",
        "MeterReadingService",
        "NotificationService",
        "RevaluationService",
        "ServiceHistoryService",
        "TransferService",
        "WarrantyService",
    ]
    file_map = {
        "AssetApplicationService": "application_service",
        "AssetAuditService": "asset_audit_service",
        "AssetCategoryService": "asset_category_service",
        "AssetIntegrationService": "integration_service",
        "AssetReportService": "asset_report_service",
        "AssetService": "asset_service",
        "AssignmentService": "assignment_service",
        "ChecklistService": "checklist_service",
        "ComponentService": "component_service",
        "DepreciationService": "depreciation_service",
        "DisposalService": "disposal_service",
        "DocumentService": "document_service",
        "InsuranceService": "insurance_service",
        "LocationService": "location_service",
        "MaintenancePlanService": "maintenance_plan_service",
        "MaintenanceService": "maintenance_service",
        "MeterReadingService": "meter_reading_service",
        "NotificationService": "notification_service",
        "RevaluationService": "revaluation_service",
        "ServiceHistoryService": "service_history_service",
        "TransferService": "transfer_service",
        "WarrantyService": "warranty_service",
    }
    imports = "\n".join(
        f"from modules.asset.service.{file_map[n]} import {n}" for n in svc_exports
    )
    all_names = ",\n    ".join(f'"{n}"' for n in svc_exports)
    w(
        AST / "service" / "__init__.py",
        f'"""Asset services."""\n\n{imports}\n\n__all__ = [\n    {all_names},\n]\n',
    )


def gen_adapters() -> None:
    w(
        AST / "adapters" / "master_data_port.py",
        '''"""Master Data port — AssetService for master_asset create/link + employee/product/vendor."""

from uuid import UUID

from sqlalchemy.orm import Session

from modules.asset.models import AstAsset
from modules.foundation.domain.value_objects import TenantContext
from modules.master_data.service.asset_service import AssetService as MasterAssetService
from modules.master_data.service.employee_service import EmployeeService
from modules.master_data.service.product_service import ProductService
from modules.master_data.service.vendor_service import VendorService


class AssetMasterDataAdapter:
    def __init__(self, db: Session) -> None:
        self._assets = MasterAssetService(db)
        self._employees = EmployeeService(db)
        self._products = ProductService(db)
        self._vendors = VendorService(db)

    def get_employee(self, ctx: TenantContext, employee_id: UUID):
        return self._employees.get_employee(ctx, employee_id)

    def get_product(self, ctx: TenantContext, product_id: UUID):
        return self._products.get_product(ctx, product_id)

    def get_vendor(self, ctx: TenantContext, vendor_id: UUID):
        return self._vendors.get_vendor(ctx, vendor_id)

    def create_or_link_master_asset(self, ctx: TenantContext, asset: AstAsset):
        if asset.master_asset_id is not None:
            return self._assets.get_asset(ctx, asset.master_asset_id)
        return self._assets.create_asset(
            ctx,
            company_id=asset.company_id,
            branch_id=asset.branch_id,
            asset_code=asset.asset_code,
            asset_name=asset.asset_name,
            asset_category=asset.asset_type,
            serial_number=asset.serial_number,
            purchase_date=asset.purchase_date,
            purchase_value=float(asset.purchase_cost) if asset.purchase_cost is not None else None,
            custodian_employee_id=asset.custodian_employee_id,
        )

    def mark_master_disposed(self, ctx: TenantContext, master_asset_id: UUID):
        return self._assets.update_asset(ctx, master_asset_id, status="disposed")
''',
    )
    w(
        AST / "adapters" / "organization_port.py",
        '''"""Organization port — read org_department only."""

from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import NotFoundException
from modules.foundation.domain.value_objects import TenantContext
from modules.organization.repository.hierarchy_repository import DepartmentRepository


class AssetOrganizationAdapter:
    def __init__(self, db: Session) -> None:
        self._departments = DepartmentRepository(db)

    def get_department(self, ctx: TenantContext, department_id: UUID):
        department = self._departments.get_by_id(ctx, department_id)
        if department is None:
            raise NotFoundException("Department not found")
        return department
''',
    )
    w(
        AST / "adapters" / "finance_port.py",
        '''"""Finance port — JournalService + PostingService.post_system_journal only."""

from datetime import date
from decimal import Decimal
from uuid import UUID

from sqlalchemy.orm import Session

from modules.asset.models import AstAssetDepreciation, AstAssetDisposal, AstAssetRevaluation
from modules.finance.domain.enums import JournalType
from modules.finance.service.journal_service import JournalService
from modules.finance.service.posting_service import PostingService
from modules.foundation.domain.value_objects import TenantContext


class AssetFinanceAdapter:
    def __init__(self, db: Session) -> None:
        self._journals = JournalService(db)
        self._posting = PostingService(db)

    def _post_amount(
        self,
        ctx: TenantContext,
        *,
        company_id: UUID,
        branch_id: UUID | None,
        journal_date: date | None,
        description: str,
        amount: Decimal,
        debit_account_id: UUID,
        credit_account_id: UUID,
        fiscal_year_id: UUID | None,
        debit_desc: str,
        credit_desc: str,
    ) -> UUID:
        amount = amount.quantize(Decimal("0.0001"))
        journal = self._journals.create_journal(
            ctx,
            company_id=company_id,
            branch_id=branch_id,
            journal_date=journal_date or date.today(),
            description=description,
            journal_type=JournalType.SYSTEM.value,
            fiscal_year_id=fiscal_year_id,
        )
        self._journals.add_line(
            ctx,
            journal.id,
            line_number=1,
            account_id=debit_account_id,
            debit_amount=float(amount),
            credit_amount=0,
            description=debit_desc,
        )
        self._journals.add_line(
            ctx,
            journal.id,
            line_number=2,
            account_id=credit_account_id,
            debit_amount=0,
            credit_amount=float(amount),
            description=credit_desc,
        )
        self._posting.post_system_journal(ctx, journal.id)
        return journal.id

    def post_depreciation(
        self,
        ctx: TenantContext,
        row: AstAssetDepreciation,
        *,
        amount: Decimal,
        debit_account_id: UUID,
        credit_account_id: UUID,
        fiscal_year_id: UUID | None = None,
    ) -> UUID:
        return self._post_amount(
            ctx,
            company_id=row.company_id,
            branch_id=getattr(row, "branch_id", None),
            journal_date=date(row.period_year, row.period_month, 1),
            description=f"Asset depreciation {row.document_number}",
            amount=amount,
            debit_account_id=debit_account_id,
            credit_account_id=credit_account_id,
            fiscal_year_id=fiscal_year_id,
            debit_desc="Depreciation expense",
            credit_desc="Accumulated depreciation",
        )

    def post_disposal(
        self,
        ctx: TenantContext,
        row: AstAssetDisposal,
        *,
        amount: Decimal,
        debit_account_id: UUID,
        credit_account_id: UUID,
        fiscal_year_id: UUID | None = None,
    ) -> UUID:
        return self._post_amount(
            ctx,
            company_id=row.company_id,
            branch_id=row.branch_id,
            journal_date=row.disposal_date,
            description=f"Asset disposal {row.document_number}",
            amount=amount,
            debit_account_id=debit_account_id,
            credit_account_id=credit_account_id,
            fiscal_year_id=fiscal_year_id,
            debit_desc="Asset disposal debit",
            credit_desc="Asset disposal credit",
        )

    def post_revaluation(
        self,
        ctx: TenantContext,
        row: AstAssetRevaluation,
        *,
        amount: Decimal,
        debit_account_id: UUID,
        credit_account_id: UUID,
        fiscal_year_id: UUID | None = None,
    ) -> UUID:
        return self._post_amount(
            ctx,
            company_id=row.company_id,
            branch_id=row.branch_id,
            journal_date=row.revaluation_date,
            description=f"Asset revaluation {row.document_number}",
            amount=amount,
            debit_account_id=debit_account_id,
            credit_account_id=credit_account_id,
            fiscal_year_id=fiscal_year_id,
            debit_desc="Asset revaluation debit",
            credit_desc="Asset revaluation credit",
        )
''',
    )
    w(
        AST / "adapters" / "payroll_port.py",
        '''"""Payroll port — optional read-only labor cost hint; no pay_* writes."""

from uuid import UUID

from sqlalchemy.orm import Session

from modules.foundation.domain.value_objects import TenantContext
from modules.payroll.repository.employee_salary_repository import EmployeeSalaryRepository


class AssetPayrollAdapter:
    def __init__(self, db: Session) -> None:
        self._salaries = EmployeeSalaryRepository(db)

    def labor_cost_hint(self, ctx: TenantContext, employee_id: UUID):
        rows = self._salaries.list_rows(ctx, ctx.company_id) if ctx.company_id else []
        for row in rows:
            if getattr(row, "employee_id", None) == employee_id and not getattr(
                row, "is_deleted", False
            ):
                return {
                    "employee_id": employee_id,
                    "salary_id": row.id,
                    "status": getattr(row, "status", None),
                }
        return {"employee_id": employee_id, "hint": None}
''',
    )
    w(
        AST / "adapters" / "__init__.py",
        '''"""Asset adapters."""

from modules.asset.adapters.finance_port import AssetFinanceAdapter
from modules.asset.adapters.master_data_port import AssetMasterDataAdapter
from modules.asset.adapters.organization_port import AssetOrganizationAdapter
from modules.asset.adapters.payroll_port import AssetPayrollAdapter

__all__ = [
    "AssetFinanceAdapter",
    "AssetMasterDataAdapter",
    "AssetOrganizationAdapter",
    "AssetPayrollAdapter",
]
''',
    )

def gen_permissions() -> None:
    w(
        AST / "permissions.py",
        '''"""Asset permission constants per ERD_15 section 14."""

ASSET_PERMISSIONS: list[tuple[str, str, str, str]] = [
    ("asset.category:read", "asset.category", "read", "asset"),
    ("asset.category:create", "asset.category", "create", "asset"),
    ("asset.category:update", "asset.category", "update", "asset"),
    ("asset.asset:read", "asset.asset", "read", "asset"),
    ("asset.asset:create", "asset.asset", "create", "asset"),
    ("asset.asset:update", "asset.asset", "update", "asset"),
    ("asset.asset:submit", "asset.asset", "submit", "asset"),
    ("asset.asset:approve", "asset.asset", "approve", "asset"),
    ("asset.assignment:read", "asset.assignment", "read", "asset"),
    ("asset.assignment:create", "asset.assignment", "create", "asset"),
    ("asset.assignment:submit", "asset.assignment", "submit", "asset"),
    ("asset.assignment:approve", "asset.assignment", "approve", "asset"),
    ("asset.assignment:return", "asset.assignment", "return", "asset"),
    ("asset.transfer:read", "asset.transfer", "read", "asset"),
    ("asset.transfer:create", "asset.transfer", "create", "asset"),
    ("asset.transfer:complete", "asset.transfer", "complete", "asset"),
    ("asset.location:read", "asset.location", "read", "asset"),
    ("asset.location:create", "asset.location", "create", "asset"),
    ("asset.location:complete", "asset.location", "complete", "asset"),
    ("asset.warranty:read", "asset.warranty", "read", "asset"),
    ("asset.warranty:create", "asset.warranty", "create", "asset"),
    ("asset.warranty:update", "asset.warranty", "update", "asset"),
    ("asset.insurance:read", "asset.insurance", "read", "asset"),
    ("asset.insurance:create", "asset.insurance", "create", "asset"),
    ("asset.insurance:update", "asset.insurance", "update", "asset"),
    ("asset.maintenance:read", "asset.maintenance", "read", "asset"),
    ("asset.maintenance:create", "asset.maintenance", "create", "asset"),
    ("asset.maintenance:submit", "asset.maintenance", "submit", "asset"),
    ("asset.maintenance:approve", "asset.maintenance", "approve", "asset"),
    ("asset.maintenance:complete", "asset.maintenance", "complete", "asset"),
    ("asset.depreciation:read", "asset.depreciation", "read", "asset"),
    ("asset.depreciation:calculate", "asset.depreciation", "calculate", "asset"),
    ("asset.depreciation:post", "asset.depreciation", "post", "asset"),
    ("asset.disposal:read", "asset.disposal", "read", "asset"),
    ("asset.disposal:create", "asset.disposal", "create", "asset"),
    ("asset.disposal:submit", "asset.disposal", "submit", "asset"),
    ("asset.disposal:approve", "asset.disposal", "approve", "asset"),
    ("asset.disposal:post", "asset.disposal", "post", "asset"),
    ("asset.revaluation:read", "asset.revaluation", "read", "asset"),
    ("asset.revaluation:create", "asset.revaluation", "create", "asset"),
    ("asset.revaluation:submit", "asset.revaluation", "submit", "asset"),
    ("asset.revaluation:approve", "asset.revaluation", "approve", "asset"),
    ("asset.revaluation:post", "asset.revaluation", "post", "asset"),
    ("asset.audit:read", "asset.audit", "read", "asset"),
    ("asset.audit:create", "asset.audit", "create", "asset"),
    ("asset.audit:complete", "asset.audit", "complete", "asset"),
    ("asset.document:read", "asset.document", "read", "asset"),
    ("asset.document:create", "asset.document", "create", "asset"),
    ("asset.document:update", "asset.document", "update", "asset"),
    ("asset.checklist:read", "asset.checklist", "read", "asset"),
    ("asset.checklist:create", "asset.checklist", "create", "asset"),
    ("asset.checklist:update", "asset.checklist", "update", "asset"),
    ("asset.meter:read", "asset.meter", "read", "asset"),
    ("asset.meter:create", "asset.meter", "create", "asset"),
    ("asset.meter:update", "asset.meter", "update", "asset"),
    ("asset.report:read", "asset.report", "read", "asset"),
    ("asset.report:export", "asset.report", "export", "asset"),
]

_ALL = [p[0] for p in ASSET_PERMISSIONS]

ASSET_EXECUTIVE_PERMISSIONS = [
    p for p in _ALL
    if not any(
        x in p
        for x in (
            ":approve",
            ":post",
            "depreciation:calculate",
            "disposal:approve",
            "revaluation:approve",
        )
    )
]

ASSET_MANAGER_PERMISSIONS = [
    p for p in _ALL
    if "report:export" not in p or True
]
# Managers get approve paths except admin-only write-off ops — grant most actions
ASSET_MANAGER_PERMISSIONS = [
    p for p in _ALL
    if not p.endswith("report:export") or p.endswith("report:export")
]
ASSET_MANAGER_PERMISSIONS = list(_ALL)

ASSET_AUDITOR_PERMISSIONS = [
    p for p in _ALL
    if p.endswith(":read")
    or p.startswith("asset.audit:")
    or p.startswith("asset.report:")
]

ASSET_ADMIN_PERMISSIONS = list(_ALL)
''',
    )


def gen_api() -> None:
    w(
        AST / "dependencies.py",
        '''"""Asset module dependencies."""

from dataclasses import dataclass
from typing import Annotated

from fastapi import Query

from database.session import get_db
from modules.foundation.dependencies import get_tenant_context, require_permission
from modules.foundation.domain.value_objects import TenantContext

__all__ = [
    "PaginationParams",
    "get_pagination",
    "get_tenant_context",
    "require_permission",
    "TenantContext",
    "get_db",
    "paginate",
    "extract_update_fields",
]


@dataclass(frozen=True)
class PaginationParams:
    page: int
    page_size: int

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size


def get_pagination(
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=200)] = 25,
) -> PaginationParams:
    return PaginationParams(page=page, page_size=page_size)


def paginate(items: list, pagination: PaginationParams) -> list:
    return items[pagination.offset : pagination.offset + pagination.page_size]


def extract_update_fields(body) -> dict:
    fields = body.model_dump(exclude_unset=True)
    fields.pop("version", None)
    return fields
''',
    )

    schema_lines = [
        '"""Asset Pydantic schemas."""',
        "",
        "from uuid import UUID",
        "",
        "from pydantic import BaseModel, ConfigDict",
        "",
        "",
        "class OrmModel(BaseModel):",
        "    model_config = ConfigDict(from_attributes=True)",
        "",
    ]
    for _, name, _, _, branch in ROUTE_SPECS:
        schema_lines += [
            "",
            f"class {name}Create(BaseModel):",
            "    company_id: UUID | None = None",
        ]
        if branch:
            schema_lines.append("    branch_id: UUID")
        schema_lines += [
            "    status: str | None = None",
            "",
            f"class {name}Update(BaseModel):",
            "    status: str | None = None",
            "    version: int | None = None",
            "",
            f"class {name}Response(OrmModel):",
            "    id: UUID",
            "    company_id: UUID",
            "    status: str",
            "    version: int",
        ]
    schema_lines += [
        "",
        "class FinancePostRequest(BaseModel):",
        "    debit_account_id: UUID",
        "    credit_account_id: UUID",
        "    fiscal_year_id: UUID | None = None",
    ]
    w(AST / "schemas.py", "\n".join(schema_lines) + "\n")

    # CRITICAL: paths must use /{row_id} with leading slash
    router_parts: list[str] = [
        '"""Asset API route handlers."""',
        "",
        "from typing import Annotated",
        "from uuid import UUID",
        "",
        "from fastapi import APIRouter, Depends",
        "from sqlalchemy.orm import Session",
        "",
        "from modules.asset.dependencies import (",
        "    PaginationParams,",
        "    extract_update_fields,",
        "    get_db,",
        "    get_pagination,",
        "    paginate,",
        "    require_permission,",
        ")",
        "from modules.asset.schemas import (",
    ]
    for _, name, _, _, _ in ROUTE_SPECS:
        router_parts.append(f"    {name}Create,")
        router_parts.append(f"    {name}Response,")
        router_parts.append(f"    {name}Update,")
    router_parts += [
        "    FinancePostRequest,",
        ")",
        "from modules.asset.service import (",
    ]
    for _, _, svc, _, _ in ROUTE_SPECS:
        router_parts.append(f"    {svc},")
    router_parts.append(")")
    router_parts.append("from modules.foundation.domain.value_objects import TenantContext")
    router_parts.append("from shared.schemas import APIResponse")
    router_parts.append("")

    exports: list[str] = []
    for prefix, name, svc, perm, branch in ROUTE_SPECS:
        rname = f"{prefix.replace('-', '_')}_router"
        exports.append(rname)
        router_parts.append(f'{rname} = APIRouter(prefix="/{prefix}", tags=["Asset — {name}"])')
        router_parts.append("")
        if branch:
            create_call = (
                f"{svc}(db).create(ctx, branch_id=body.branch_id, "
                f"**body.model_dump(exclude={{'branch_id'}}, exclude_none=True))"
            )
        else:
            create_call = f"{svc}(db).create(ctx, **body.model_dump(exclude_none=True))"

        update_perm = (
            f"{perm}:export" if perm == "asset.report" else f"{perm}:update"
        )
        if perm in {"asset.assignment", "asset.disposal", "asset.revaluation", "asset.depreciation"}:
            # some resources lack :update — use create or read-adjacent
            if perm == "asset.assignment":
                update_perm = "asset.assignment:create"
            elif perm == "asset.disposal":
                update_perm = "asset.disposal:create"
            elif perm == "asset.revaluation":
                update_perm = "asset.revaluation:create"
            elif perm == "asset.depreciation":
                update_perm = "asset.depreciation:read"

        fn = prefix.replace("-", "_")
        router_parts += [
            f'@{rname}.get("", response_model=APIResponse[list[{name}Response]])',
            f"def list_{fn}(",
            f'    ctx: Annotated[TenantContext, Depends(require_permission("{perm}:read"))],',
            "    db: Annotated[Session, Depends(get_db)],",
            "    pagination: Annotated[PaginationParams, Depends(get_pagination)],",
            "    company_id: UUID | None = None,",
            "):",
            f"    items = {svc}(db).list(ctx, company_id=company_id)",
            '    return APIResponse(message="OK", data=paginate(items, pagination))',
            "",
            f'@{rname}.get("/{{row_id}}", response_model=APIResponse[{name}Response])',
            f"def get_{fn}(",
            "    row_id: UUID,",
            f'    ctx: Annotated[TenantContext, Depends(require_permission("{perm}:read"))],',
            "    db: Annotated[Session, Depends(get_db)],",
            "):",
            f'    return APIResponse(message="OK", data={svc}(db).get(ctx, row_id))',
            "",
            f'@{rname}.post("", response_model=APIResponse[{name}Response])',
            f"def create_{fn}(",
            f"    body: {name}Create,",
            f'    ctx: Annotated[TenantContext, Depends(require_permission("{perm}:create" if "{perm}" != "asset.depreciation" and "{perm}" != "asset.report" else ("asset.depreciation:calculate" if "{perm}" == "asset.depreciation" else "asset.report:export")))],',
            "    db: Annotated[Session, Depends(get_db)],",
            "):",
            f'    return APIResponse(message="Created", data={create_call})',
            "",
            f'@{rname}.patch("/{{row_id}}", response_model=APIResponse[{name}Response])',
            f"def update_{fn}(",
            "    row_id: UUID,",
            f"    body: {name}Update,",
            f'    ctx: Annotated[TenantContext, Depends(require_permission("{update_perm}"))],',
            "    db: Annotated[Session, Depends(get_db)],",
            "):",
            f'    return APIResponse(message="Updated", data={svc}(db).update(ctx, row_id, **extract_update_fields(body)))',
            "",
        ]

        # Fix create permission - the ternary above is overly complex. Generate cleaner post-hoc.
        # Lifecycle actions
        actions: list[tuple[str, str]] = []
        if svc == "AssetService":
            actions = [("submit", "asset.asset:submit"), ("approve", "asset.asset:approve")]
        elif svc == "AssignmentService":
            actions = [
                ("submit", "asset.assignment:submit"),
                ("approve", "asset.assignment:approve"),
                ("return_assignment", "asset.assignment:return"),
            ]
        elif svc == "MaintenanceService":
            actions = [
                ("submit", "asset.maintenance:submit"),
                ("approve", "asset.maintenance:approve"),
                ("complete", "asset.maintenance:complete"),
            ]
        elif svc == "DepreciationService":
            actions = [("calculate", "asset.depreciation:calculate")]
        elif svc == "DisposalService":
            actions = [
                ("submit", "asset.disposal:submit"),
                ("approve", "asset.disposal:approve"),
            ]
        elif svc == "RevaluationService":
            actions = [
                ("submit", "asset.revaluation:submit"),
                ("approve", "asset.revaluation:approve"),
            ]
        elif svc == "AssetAuditService":
            actions = [("complete", "asset.audit:complete")]
        elif svc == "TransferService":
            actions = [("complete", "asset.transfer:complete")]

        for act, pcode in actions:
            route_act = "return" if act == "return_assignment" else act
            router_parts += [
                f'@{rname}.post("/{{row_id}}/{route_act}", response_model=APIResponse[{name}Response])',
                f"def {route_act}_{fn}(",
                "    row_id: UUID,",
                f'    ctx: Annotated[TenantContext, Depends(require_permission("{pcode}"))],',
                "    db: Annotated[Session, Depends(get_db)],",
                "):",
                f'    return APIResponse(message="{route_act}", data={svc}(db).{act}(ctx, row_id))',
                "",
            ]

        if svc in {"DepreciationService", "DisposalService", "RevaluationService"}:
            router_parts += [
                f'@{rname}.post("/{{row_id}}/post", response_model=APIResponse[{name}Response])',
                f"def post_{fn}(",
                "    row_id: UUID,",
                "    body: FinancePostRequest,",
                f'    ctx: Annotated[TenantContext, Depends(require_permission("{perm}:post"))],',
                "    db: Annotated[Session, Depends(get_db)],",
                "):",
                f"    data = {svc}(db).post(",
                "        ctx,",
                "        row_id,",
                "        debit_account_id=body.debit_account_id,",
                "        credit_account_id=body.credit_account_id,",
                "        fiscal_year_id=body.fiscal_year_id,",
                "    )",
                '    return APIResponse(message="Posted", data=data)',
                "",
            ]

    # Clean up create permissions - rewrite the messy ones by regenerating create handlers simply
    # Actually fix create_perm at generation time more carefully:
    # I'll post-process the content

    content = "\n".join(router_parts)
    # Fix ugly create Depends lines
    import re

    def fix_create(m):
        # extract resource from surrounding context is hard; use simpler replacement
        return m.group(0)

    # Rewrite create permission lines that contain the broken ternary
    content = re.sub(
        r'ctx: Annotated\[TenantContext, Depends\(require_permission\("asset\.[^"]+:create" if .*?\)\)\],',
        lambda m: _fix_create_perm(m.group(0)),
        content,
    )
    w(AST / "routers" / "__init__.py", content + "\n")

    include_lines = "\n".join(f"asset_router.include_router({e})" for e in exports)
    import_list = ",\n    ".join(exports)
    w(
        AST / "router.py",
        f'''"""Asset module router aggregation."""

from fastapi import APIRouter

from modules.asset.routers import (
    {import_list},
)

asset_router = APIRouter(prefix="/assets")
)
asset_router.include_router({exports[0]})
'''
        + "\n".join(f"asset_router.include_router({e})" for e in exports[1:])
        + "\n",
    )
    # Fix broken parenthesis in router.py
    w(
        AST / "router.py",
        f'''"""Asset module router aggregation."""

from fastapi import APIRouter

from modules.asset.routers import (
    {import_list},
)

asset_router = APIRouter(prefix="/assets")
{include_lines}
'''.replace('APIRouter(prefix="/assets")\n', 'APIRouter(prefix="/assets")\n'),
    )
    # The include_lines don't start correctly - rewrite cleanly
    w(
        AST / "router.py",
        f'''"""Asset module router aggregation."""

from fastapi import APIRouter

from modules.asset.routers import (
    {import_list},
)

asset_router = APIRouter(prefix="/assets")
'''
        + "\n".join(f"asset_router.include_router({e})" for e in exports)
        + "\n",
    )


def _fix_create_perm(fragment: str) -> str:
    if "asset.depreciation" in fragment:
        return 'ctx: Annotated[TenantContext, Depends(require_permission("asset.depreciation:calculate"))],'
    if "asset.report" in fragment:
        return 'ctx: Annotated[TenantContext, Depends(require_permission("asset.report:export"))],'
    # extract default create resource
    import re

    m = re.search(r'"(asset\.[^"]+):create"', fragment)
    if m:
        return f'ctx: Annotated[TenantContext, Depends(require_permission("{m.group(1)}:create"))],'
    return 'ctx: Annotated[TenantContext, Depends(require_permission("asset.asset:create"))],'


def gen_tasks_tests() -> None:
    w(
        AST / "tasks.py",
        '''"""Asset Celery task stubs per ERD_15 section 15."""

from workers.celery_app import celery_app


@celery_app.task(name="asset.maintenance_due_alerts")
def maintenance_due_alerts() -> dict:
    from sqlalchemy import select

    from database.session import SessionLocal
    from modules.asset.models import AstAssetMaintenancePlan

    db = SessionLocal()
    try:
        rows = list(
            db.scalars(
                select(AstAssetMaintenancePlan).where(
                    AstAssetMaintenancePlan.is_deleted.is_(False),
                    AstAssetMaintenancePlan.status == "active",
                )
            ).all()
        )
        return {"status": "ok", "active_plans": len(rows)}
    finally:
        db.close()


@celery_app.task(name="asset.warranty_expiry_alerts")
def warranty_expiry_alerts() -> dict:
    from sqlalchemy import select

    from database.session import SessionLocal
    from modules.asset.models import AstAssetWarranty

    db = SessionLocal()
    try:
        rows = list(
            db.scalars(
                select(AstAssetWarranty).where(
                    AstAssetWarranty.is_deleted.is_(False),
                    AstAssetWarranty.status == "active",
                )
            ).all()
        )
        return {"status": "ok", "active_warranties": len(rows)}
    finally:
        db.close()


@celery_app.task(name="asset.insurance_expiry_alerts")
def insurance_expiry_alerts() -> dict:
    from sqlalchemy import select

    from database.session import SessionLocal
    from modules.asset.models import AstAssetInsurance

    db = SessionLocal()
    try:
        rows = list(
            db.scalars(
                select(AstAssetInsurance).where(
                    AstAssetInsurance.is_deleted.is_(False),
                    AstAssetInsurance.status == "active",
                )
            ).all()
        )
        return {"status": "ok", "active_insurances": len(rows)}
    finally:
        db.close()


@celery_app.task(name="asset.depreciation_scheduler")
def depreciation_scheduler() -> dict:
    from sqlalchemy import select

    from database.session import SessionLocal
    from modules.asset.models import AstAssetDepreciation

    db = SessionLocal()
    try:
        rows = list(
            db.scalars(
                select(AstAssetDepreciation).where(
                    AstAssetDepreciation.is_deleted.is_(False),
                    AstAssetDepreciation.status == "draft",
                )
            ).all()
        )
        return {"status": "ok", "draft_depreciations": len(rows)}
    finally:
        db.close()


@celery_app.task(name="asset.asset_audit_reminders")
def asset_audit_reminders() -> dict:
    from sqlalchemy import select

    from database.session import SessionLocal
    from modules.asset.models import AstAssetAudit

    db = SessionLocal()
    try:
        rows = list(
            db.scalars(
                select(AstAssetAudit).where(
                    AstAssetAudit.is_deleted.is_(False),
                    AstAssetAudit.status == "planned",
                )
            ).all()
        )
        return {"status": "ok", "planned_audits": len(rows)}
    finally:
        db.close()


@celery_app.task(name="asset.retry_finance_posting")
def retry_finance_posting() -> dict:
    from sqlalchemy import select

    from database.session import SessionLocal
    from modules.asset.models import AstAssetDepreciation

    db = SessionLocal()
    try:
        rows = list(
            db.scalars(
                select(AstAssetDepreciation).where(
                    AstAssetDepreciation.is_deleted.is_(False),
                    AstAssetDepreciation.status == "failed",
                )
            ).all()
        )
        return {"status": "ok", "failed_depreciations": len(rows)}
    finally:
        db.close()
''',
    )

    w(
        TESTS / "unit" / "asset" / "test_asset_engines.py",
        '''"""Unit tests for asset engines."""

from types import SimpleNamespace

from modules.asset.service.engines import (
    AssetAssignmentEngine,
    AssetDepreciationEngine,
    AssetDisposalEngine,
    AssetEngine,
    AssetMaintenanceEngine,
)


def test_asset_lifecycle():
    engine = AssetEngine()
    row = SimpleNamespace(status="draft")
    engine.submit(row)
    assert row.status == "submitted"
    engine.approve(row)
    assert row.status == "approved"
    engine.activate(row)
    assert row.status == "active"


def test_assignment_return():
    engine = AssetAssignmentEngine()
    row = SimpleNamespace(status="draft")
    engine.submit(row)
    engine.approve(row)
    engine.activate(row)
    engine.return_assignment(row)
    assert row.status == "returned"


def test_maintenance_complete():
    engine = AssetMaintenanceEngine()
    row = SimpleNamespace(status="draft")
    engine.submit(row)
    engine.approve(row)
    engine.start(row)
    engine.complete(row)
    assert row.status == "completed"


def test_depreciation_and_disposal():
    dep = AssetDepreciationEngine()
    drow = SimpleNamespace(status="draft")
    dep.calculate(drow)
    dep.post(drow)
    assert drow.status == "posted"

    disp = AssetDisposalEngine()
    xrow = SimpleNamespace(status="draft")
    disp.submit(xrow)
    disp.approve(xrow)
    disp.post(xrow)
    assert xrow.status == "posted"
''',
    )

    w(
        TESTS / "unit" / "asset" / "test_asset_tasks.py",
        '''"""Unit tests for asset Celery tasks."""

from modules.asset import tasks as asset_tasks


def test_asset_task_names_registered():
    assert asset_tasks.maintenance_due_alerts.name == "asset.maintenance_due_alerts"
    assert asset_tasks.warranty_expiry_alerts.name == "asset.warranty_expiry_alerts"
    assert asset_tasks.insurance_expiry_alerts.name == "asset.insurance_expiry_alerts"
    assert asset_tasks.depreciation_scheduler.name == "asset.depreciation_scheduler"
    assert asset_tasks.asset_audit_reminders.name == "asset.asset_audit_reminders"
    assert asset_tasks.retry_finance_posting.name == "asset.retry_finance_posting"
''',
    )

    w(
        TESTS / "security" / "asset" / "test_asset_permissions.py",
        '''"""Asset RBAC permission tests."""

from modules.asset.permissions import (
    ASSET_ADMIN_PERMISSIONS,
    ASSET_AUDITOR_PERMISSIONS,
    ASSET_EXECUTIVE_PERMISSIONS,
    ASSET_MANAGER_PERMISSIONS,
    ASSET_PERMISSIONS,
)


def test_asset_permissions_defined():
    assert len(ASSET_PERMISSIONS) >= 40
    assert "asset.asset:approve" in [p[0] for p in ASSET_PERMISSIONS]
    assert "asset.depreciation:post" in [p[0] for p in ASSET_PERMISSIONS]


def test_asset_roles():
    assert ASSET_EXECUTIVE_PERMISSIONS
    assert ASSET_MANAGER_PERMISSIONS
    assert ASSET_AUDITOR_PERMISSIONS
    assert ASSET_ADMIN_PERMISSIONS
    assert "asset.asset:approve" in ASSET_MANAGER_PERMISSIONS
    assert "asset.depreciation:post" in ASSET_ADMIN_PERMISSIONS
''',
    )

    w(
        TESTS / "integration" / "asset" / "test_asset_module_import.py",
        '''"""Integration smoke: Asset module imports and router mount."""

from modules.asset.models import AstAsset, AstAssetCategory, AstAssetDepreciation
from modules.asset.router import asset_router
from modules.asset.service import AssetApplicationService, AssetService, DepreciationService
from modules.asset.service.engines import AssetDepreciationEngine, AssetEngine


def test_asset_models_importable():
    assert AstAsset.__tablename__ == "ast_asset"
    assert AstAssetCategory.__tablename__ == "ast_asset_category"
    assert AstAssetDepreciation.__tablename__ == "ast_asset_depreciation"


def test_asset_router_mounted():
    assert asset_router.prefix == "/assets"
    assert len(asset_router.routes) > 20
    paths = []
    for route in asset_router.routes:
        p = getattr(route, "path", "")
        if "{row_id}" in p:
            assert "/{row_id}" in p or p.endswith("{row_id}") or "/{row_id}/" in p
            # Sprint 14 lesson: path params must use leading slash form
            assert "{row_id}" in p
            segment = p.split("{row_id}")[0]
            assert segment.endswith("/"), f"row_id missing leading slash in {p}"


def test_asset_services_and_engines_importable():
    assert AssetApplicationService is not None
    assert AssetService is not None
    assert DepreciationService is not None
    assert AssetEngine is not None
    assert AssetDepreciationEngine is not None
''',
    )


def gen_seeds() -> None:
    w(
        ALEMBIC / "0265_seed_asset_permissions.py",
        '''"""Seed asset permissions and roles."""

import sys
from collections.abc import Sequence
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import sqlalchemy as sa
from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from modules.asset.permissions import (
    ASSET_ADMIN_PERMISSIONS,
    ASSET_AUDITOR_PERMISSIONS,
    ASSET_EXECUTIVE_PERMISSIONS,
    ASSET_MANAGER_PERMISSIONS,
    ASSET_PERMISSIONS,
)

revision: str = "0265_seed_asset_permissions"
down_revision: str | None = "0264_ast_asset_report"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

PERMISSION_TABLE = sa.table(
    "sec_permission",
    sa.column("id", sa.Uuid),
    sa.column("permission_code", sa.String),
    sa.column("resource", sa.String),
    sa.column("action", sa.String),
    sa.column("module", sa.String),
    sa.column("is_active", sa.Boolean),
    sa.column("created_at", sa.DateTime(timezone=True)),
    schema="foundation",
)

ROLE_SPECS: list[tuple[str, str, list[str]]] = [
    ("ASSET_MANAGER", "Asset Manager", ASSET_MANAGER_PERMISSIONS),
    ("ASSET_EXECUTIVE", "Asset Executive", ASSET_EXECUTIVE_PERMISSIONS),
    ("ASSET_AUDITOR", "Asset Auditor", ASSET_AUDITOR_PERMISSIONS),
    ("ASSET_ADMIN", "Asset Admin", ASSET_ADMIN_PERMISSIONS),
]


def _ensure_permission(conn, now, code, resource, action, module):
    exists = conn.execute(
        sa.text("SELECT id FROM foundation.sec_permission WHERE permission_code = :code"),
        {"code": code},
    ).first()
    if exists:
        return str(exists[0])
    perm_id = str(uuid4())
    conn.execute(
        sa.insert(PERMISSION_TABLE).values(
            id=perm_id,
            permission_code=code,
            resource=resource,
            action=action,
            module=module,
            is_active=True,
            created_at=now,
        )
    )
    return perm_id


def _ensure_role(conn, now, tenant_id, role_code, role_name):
    exists = conn.execute(
        sa.text(
            """
            SELECT id FROM foundation.sec_role
            WHERE tenant_id = :tid AND role_code = :code AND is_deleted = false
            """
        ),
        {"tid": tenant_id, "code": role_code},
    ).first()
    if exists:
        return str(exists[0])
    role_id = str(uuid4())
    conn.execute(
        sa.text(
            """
            INSERT INTO foundation.sec_role
            (id, tenant_id, role_code, role_name, is_system_role, status,
             created_at, updated_at, is_deleted, version)
            VALUES (:id, :tid, :code, :name, true, 'active', :now, :now, false, 1)
            """
        ),
        {"id": role_id, "tid": tenant_id, "code": role_code, "name": role_name, "now": now},
    )
    return role_id


def _grant(conn, now, tenant_id, role_id, perm_id):
    exists = conn.execute(
        sa.text(
            """
            SELECT 1 FROM foundation.sec_role_permission
            WHERE role_id = :rid AND permission_id = :pid
            """
        ),
        {"rid": role_id, "pid": perm_id},
    ).first()
    if exists:
        return
    conn.execute(
        sa.text(
            """
            INSERT INTO foundation.sec_role_permission
            (id, tenant_id, role_id, permission_id, granted_at)
            VALUES (:id, :tid, :rid, :pid, :now)
            """
        ),
        {"id": str(uuid4()), "tid": tenant_id, "rid": role_id, "pid": perm_id, "now": now},
    )


def upgrade() -> None:
    conn = op.get_bind()
    now = datetime.now(timezone.utc)
    perm_ids: dict[str, str] = {}
    for code, resource, action, module in ASSET_PERMISSIONS:
        perm_ids[code] = _ensure_permission(conn, now, code, resource, action, module)
    tenants = conn.execute(
        sa.text("SELECT id FROM foundation.sec_tenant WHERE is_deleted = false")
    ).fetchall()
    for (tenant_id,) in tenants:
        tid = str(tenant_id)
        for role_code, role_name, perms in ROLE_SPECS:
            role_id = _ensure_role(conn, now, tid, role_code, role_name)
            for perm_code in perms:
                _grant(conn, now, tid, role_id, perm_ids[perm_code])


def downgrade() -> None:
    conn = op.get_bind()
    for role_code, _, _ in reversed(ROLE_SPECS):
        conn.execute(
            sa.text(
                "DELETE FROM foundation.sec_role WHERE role_code = :code AND is_system_role = true"
            ),
            {"code": role_code},
        )
    for code, _, _, _ in ASSET_PERMISSIONS:
        conn.execute(
            sa.text("DELETE FROM foundation.sec_permission WHERE permission_code = :code"),
            {"code": code},
        )
''',
    )

    w(
        ALEMBIC / "0266_seed_asset_workflows.py",
        '''"""Seed asset workflow definitions per ERD_15."""

from collections.abc import Sequence
from datetime import datetime, timezone
from uuid import uuid4

import sqlalchemy as sa
from alembic import op

revision: str = "0266_seed_asset_workflows"
down_revision: str | None = "0265_seed_asset_permissions"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

WORKFLOWS: list[tuple[str, str, str, list[tuple[int, str, str, str]]]] = [
    (
        "AST_ASSET_APPROVAL",
        "Asset Approval",
        "ast_asset",
        [
            (1, "ASSET_EXECUTIVE", "Asset Executive Submit", "role"),
            (2, "ASSET_MANAGER", "Asset Manager Approval", "role"),
            (3, "ASSET_ADMIN", "Finance Capitalization Review", "role"),
        ],
    ),
    (
        "AST_ASSIGNMENT_APPROVAL",
        "Asset Assignment Approval",
        "ast_asset_assignment",
        [
            (1, "ASSET_EXECUTIVE", "Requestor Submit", "role"),
            (2, "ASSET_MANAGER", "Custodian Manager Approval", "role"),
            (3, "ASSET_MANAGER", "Asset Manager Approval", "role"),
        ],
    ),
    (
        "AST_MAINTENANCE_APPROVAL",
        "Asset Maintenance Approval",
        "ast_asset_maintenance",
        [
            (1, "ASSET_EXECUTIVE", "Technician / Executive Submit", "role"),
            (2, "ASSET_MANAGER", "Asset Manager Approval", "role"),
        ],
    ),
    (
        "AST_DISPOSAL_APPROVAL",
        "Asset Disposal Approval",
        "ast_asset_disposal",
        [
            (1, "ASSET_MANAGER", "Asset Manager Submit", "role"),
            (2, "ASSET_ADMIN", "Asset Admin Approval", "role"),
            (3, "ASSET_ADMIN", "Finance Review", "role"),
        ],
    ),
    (
        "AST_REVALUATION_APPROVAL",
        "Asset Revaluation Approval",
        "ast_asset_revaluation",
        [
            (1, "ASSET_MANAGER", "Asset Manager Submit", "role"),
            (2, "ASSET_ADMIN", "Finance Approval", "role"),
            (3, "ASSET_ADMIN", "Asset Admin Approval", "role"),
        ],
    ),
]


def upgrade() -> None:
    conn = op.get_bind()
    now = datetime.now(timezone.utc)
    tenants = conn.execute(
        sa.text("SELECT id FROM foundation.sec_tenant WHERE is_deleted = false")
    ).fetchall()
    for (tenant_id,) in tenants:
        tid = str(tenant_id)
        for workflow_code, workflow_name, document_type, steps in WORKFLOWS:
            exists = conn.execute(
                sa.text(
                    """
                    SELECT id FROM foundation.wf_definition
                    WHERE tenant_id = :tid AND workflow_code = :code AND version_no = 1
                    """
                ),
                {"tid": tid, "code": workflow_code},
            ).first()
            if exists:
                wf_id = str(exists[0])
            else:
                wf_id = str(uuid4())
                conn.execute(
                    sa.text(
                        """
                        INSERT INTO foundation.wf_definition
                        (id, tenant_id, workflow_code, workflow_name, module,
                         document_type, version_no, is_active, created_at, updated_at)
                        VALUES (:id, :tid, :code, :name, 'asset', :doc, 1, true, :now, :now)
                        """
                    ),
                    {
                        "id": wf_id,
                        "tid": tid,
                        "code": workflow_code,
                        "name": workflow_name,
                        "doc": document_type,
                        "now": now,
                    },
                )
            for step_order, step_code, step_name, approver_type in steps:
                step_exists = conn.execute(
                    sa.text(
                        """
                        SELECT 1 FROM foundation.wf_step
                        WHERE workflow_id = :wid AND step_order = :ord
                        """
                    ),
                    {"wid": wf_id, "ord": step_order},
                ).first()
                if step_exists:
                    continue
                conn.execute(
                    sa.text(
                        """
                        INSERT INTO foundation.wf_step
                        (id, tenant_id, workflow_id, step_order, step_code, step_name,
                         approver_type, is_parallel, created_at, updated_at)
                        VALUES (:id, :tid, :wid, :ord, :code, :name, :atype, false, :now, :now)
                        """
                    ),
                    {
                        "id": str(uuid4()),
                        "tid": tid,
                        "wid": wf_id,
                        "ord": step_order,
                        "code": step_code,
                        "name": step_name,
                        "atype": approver_type,
                        "now": now,
                    },
                )


def downgrade() -> None:
    conn = op.get_bind()
    for workflow_code, _, _, _ in WORKFLOWS:
        conn.execute(
            sa.text(
                """
                DELETE FROM foundation.wf_step
                WHERE workflow_id IN (
                    SELECT id FROM foundation.wf_definition WHERE workflow_code = :code
                )
                """
            ),
            {"code": workflow_code},
        )
        conn.execute(
            sa.text("DELETE FROM foundation.wf_definition WHERE workflow_code = :code"),
            {"code": workflow_code},
        )
''',
    )


def gen_wiring() -> None:
    patch_file(
        SHARED / "router.py",
        "from modules.project.router import project_router\n",
        "from modules.project.router import project_router\n"
        "from modules.asset.router import asset_router\n",
    )
    patch_file(
        SHARED / "router.py",
        "api_v1_router.include_router(project_router)\n",
        "api_v1_router.include_router(project_router)\n"
        "api_v1_router.include_router(asset_router)\n",
    )
    patch_file(
        ROOT / "alembic" / "env.py",
        "import modules.project.models  # noqa: F401 — register ORM metadata\n",
        "import modules.project.models  # noqa: F401 — register ORM metadata\n"
        "import modules.asset.models  # noqa: F401 — register ORM metadata\n",
    )
    patch_file(
        ROOT / "src" / "workers" / "celery_app.py",
        '        "modules.project",\n',
        '        "modules.project",\n        "modules.asset",\n',
    )
    patch_file(
        ROOT / "pyproject.toml",
        '    "modules.project.*",\n',
        '    "modules.project.*",\n    "modules.asset.*",\n',
    )
    patch_file(
        ROOT / "pyproject.toml",
        '"src/modules/project/domain/enums.py" = ["UP042"]\n',
        '"src/modules/project/domain/enums.py" = ["UP042"]\n'
        '"src/modules/asset/**" = ["E501", "SIM102"]\n'
        '"src/modules/asset/domain/enums.py" = ["UP042"]\n',
    )


def main() -> None:
    gen_scaffold()
    gen_domain()
    gen_models()
    gen_migrations()
    gen_repos()
    gen_engines()
    gen_services()
    gen_adapters()
    gen_permissions()
    gen_api()
    gen_tasks_tests()
    gen_seeds()
    gen_wiring()
    print(f"OK asset module generated — {len(FILES_WRITTEN)} files")
    print("Alembic head revision: 0266_seed_asset_workflows")


if __name__ == "__main__":
    main()

