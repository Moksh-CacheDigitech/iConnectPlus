"""Manufacturing ORM models."""

from modules.manufacturing.models.bom import MfgBom, MfgBomLine
from modules.manufacturing.models.machine import MfgMachine
from modules.manufacturing.models.material_issue import MfgMaterialIssue, MfgMaterialIssueLine
from modules.manufacturing.models.material_return import MfgMaterialReturn, MfgMaterialReturnLine
from modules.manufacturing.models.production_order import (
    MfgProductionOperation,
    MfgProductionOrder,
)
from modules.manufacturing.models.production_receipt import (
    MfgProductionReceipt,
    MfgProductionReceiptLine,
)
from modules.manufacturing.models.routing import MfgRouting, MfgRoutingOperation
from modules.manufacturing.models.scrap import MfgScrap
from modules.manufacturing.models.variance import MfgVariance
from modules.manufacturing.models.wip import MfgWip
from modules.manufacturing.models.work_center import MfgWorkCenter

__all__ = [
    "MfgBom",
    "MfgBomLine",
    "MfgMachine",
    "MfgMaterialIssue",
    "MfgMaterialIssueLine",
    "MfgMaterialReturn",
    "MfgMaterialReturnLine",
    "MfgProductionOperation",
    "MfgProductionOrder",
    "MfgProductionReceipt",
    "MfgProductionReceiptLine",
    "MfgRouting",
    "MfgRoutingOperation",
    "MfgScrap",
    "MfgVariance",
    "MfgWip",
    "MfgWorkCenter",
]
