
"""Payroll ORM mixin bundles per ERD_12."""

from database.mixins import (
    AuditMixin,
    BranchMixin,
    CompanyMixin,
    SoftDeleteMixin,
    TenantMixin,
    VersionMixin,
)

PayMasterMixin = (
    AuditMixin,
    TenantMixin,
    CompanyMixin,
    SoftDeleteMixin,
    VersionMixin,
)

PayTransactionMixin = (
    AuditMixin,
    TenantMixin,
    CompanyMixin,
    BranchMixin,
    SoftDeleteMixin,
    VersionMixin,
)

PayDetailMixin = (
    AuditMixin,
    TenantMixin,
    CompanyMixin,
    SoftDeleteMixin,
    VersionMixin,
)
