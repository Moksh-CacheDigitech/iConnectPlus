"""Asset permission constants per ERD_15 section 14."""

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
    p
    for p in _ALL
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

ASSET_MANAGER_PERMISSIONS = list(_ALL)

ASSET_AUDITOR_PERMISSIONS = [
    p
    for p in _ALL
    if p.endswith(":read") or p.startswith("asset.audit:") or p.startswith("asset.report:")
]

ASSET_ADMIN_PERMISSIONS = list(_ALL)
