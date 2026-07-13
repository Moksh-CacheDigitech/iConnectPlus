"""Organization domain enumerations."""

from enum import Enum


class OrgStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    INACTIVE = "inactive"


class BranchType(str, Enum):
    HEAD_OFFICE = "head_office"
    REGIONAL = "regional"
    WAREHOUSE = "warehouse"
    RETAIL = "retail"


class LocationType(str, Enum):
    OFFICE = "office"
    WAREHOUSE = "warehouse"
    PLANT = "plant"
    STORE = "store"
