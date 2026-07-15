"""Asset adapters."""

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
