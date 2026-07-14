"""Integration smoke: manufacturing module imports and router mount."""

from modules.manufacturing.models import MfgBom, MfgProductionOrder, MfgWip
from modules.manufacturing.router import manufacturing_router


def test_models_importable():
    assert MfgBom.__tablename__ == "mfg_bom"
    assert MfgProductionOrder.__tablename__ == "mfg_production_order"
    assert MfgWip.__tablename__ == "mfg_wip"


def test_router_prefix():
    assert manufacturing_router.prefix == "/manufacturing"
    assert len(manufacturing_router.routes) > 10
