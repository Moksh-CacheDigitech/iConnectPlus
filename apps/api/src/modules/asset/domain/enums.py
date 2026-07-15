"""Asset domain enums per ERD_15 section 11."""

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
