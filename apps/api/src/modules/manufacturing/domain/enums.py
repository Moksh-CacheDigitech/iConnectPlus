"""Manufacturing domain enums per ERD_08."""

from enum import Enum


class BomStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    OBSOLETE = "obsolete"


class RoutingStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    OBSOLETE = "obsolete"


class LineStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class WorkCenterType(str, Enum):
    MACHINE = "machine"
    ASSEMBLY_LINE = "assembly_line"
    PACKAGING_LINE = "packaging_line"
    INSPECTION_STATION = "inspection_station"


class WorkCenterStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"


class MachineStatus(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    MAINTENANCE = "maintenance"
    BREAKDOWN = "breakdown"


class ProductionOrderStatus(str, Enum):
    DRAFT = "draft"
    RELEASED = "released"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CLOSED = "closed"
    CANCELLED = "cancelled"


class ProductionOperationStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"


class MaterialDocStatus(str, Enum):
    DRAFT = "draft"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"


class ScrapStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    POSTED = "posted"
    CANCELLED = "cancelled"


class ScrapType(str, Enum):
    MATERIAL = "material"
    PROCESS = "process"
    DAMAGED = "damaged"


class WipStatus(str, Enum):
    OPEN = "open"
    RELIEVED = "relieved"
    CLOSED = "closed"


class VarianceStatus(str, Enum):
    OPEN = "open"
    POSTED = "posted"


class VarianceType(str, Enum):
    MATERIAL = "material"
    LABOR = "labor"
    OVERHEAD = "overhead"
    QUANTITY = "quantity"


class MfgEntityType(str, Enum):
    BOM = "bom"
    ROUTING = "routing"
    PRODUCTION_ORDER = "production_order"
    MATERIAL_ISSUE = "material_issue"
    MATERIAL_RETURN = "material_return"
    PRODUCTION_RECEIPT = "production_receipt"
    SCRAP = "scrap"


CODE_PREFIXES: dict[MfgEntityType, tuple[str, int]] = {
    MfgEntityType.BOM: ("BOM-", 6),
    MfgEntityType.ROUTING: ("RTG-", 6),
    MfgEntityType.PRODUCTION_ORDER: ("WO-", 6),
    MfgEntityType.MATERIAL_ISSUE: ("MI-", 6),
    MfgEntityType.MATERIAL_RETURN: ("MR-", 6),
    MfgEntityType.PRODUCTION_RECEIPT: ("FGR-", 6),
    MfgEntityType.SCRAP: ("SCR-", 6),
}

SOURCE_MODULE = "manufacturing"
