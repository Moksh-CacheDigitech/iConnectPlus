"""Integration smoke: Asset module imports and router mount."""

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
    for route in asset_router.routes:
        p = getattr(route, "path", "")
        if "{row_id}" in p:
            # Sprint 14 lesson: path params must use leading slash form
            segment = p.split("{row_id}")[0]
            assert segment.endswith("/"), f"row_id missing leading slash in {p}"


def test_asset_services_and_engines_importable():
    assert AssetApplicationService is not None
    assert AssetService is not None
    assert DepreciationService is not None
    assert AssetEngine is not None
    assert AssetDepreciationEngine is not None
