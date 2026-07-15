"""Integration permission constants per ERD_21 section 10."""

INTEGRATION_PERMISSIONS: list[tuple[str, str, str, str]] = [
    ("integration.system:read", "integration.system", "read", "integration"),
    ("integration.system:create", "integration.system", "create", "integration"),
    ("integration.system:update", "integration.system", "update", "integration"),
    ("integration.connector:read", "integration.connector", "read", "integration"),
    ("integration.connector:create", "integration.connector", "create", "integration"),
    ("integration.connector:update", "integration.connector", "update", "integration"),
    ("integration.connector:submit", "integration.connector", "submit", "integration"),
    ("integration.connector:approve", "integration.connector", "approve", "integration"),
    ("integration.credential:read", "integration.credential", "read", "integration"),
    ("integration.credential:create", "integration.credential", "create", "integration"),
    ("integration.credential:update", "integration.credential", "update", "integration"),
    ("integration.credential:submit", "integration.credential", "submit", "integration"),
    ("integration.credential:approve", "integration.credential", "approve", "integration"),
    ("integration.credential:rotate", "integration.credential", "rotate", "integration"),
    ("integration.oauth:read", "integration.oauth", "read", "integration"),
    ("integration.oauth:create", "integration.oauth", "create", "integration"),
    ("integration.oauth:update", "integration.oauth", "update", "integration"),
    ("integration.oauth:rotate", "integration.oauth", "rotate", "integration"),
    ("integration.webhook:read", "integration.webhook", "read", "integration"),
    ("integration.webhook:create", "integration.webhook", "create", "integration"),
    ("integration.webhook:update", "integration.webhook", "update", "integration"),
    ("integration.webhook:submit", "integration.webhook", "submit", "integration"),
    ("integration.webhook:approve", "integration.webhook", "approve", "integration"),
    ("integration.event:read", "integration.event", "read", "integration"),
    ("integration.event:create", "integration.event", "create", "integration"),
    ("integration.event:update", "integration.event", "update", "integration"),
    ("integration.subscription:read", "integration.subscription", "read", "integration"),
    ("integration.subscription:create", "integration.subscription", "create", "integration"),
    ("integration.subscription:update", "integration.subscription", "update", "integration"),
    ("integration.queue:read", "integration.queue", "read", "integration"),
    ("integration.queue:create", "integration.queue", "create", "integration"),
    ("integration.queue:update", "integration.queue", "update", "integration"),
    ("integration.message:read", "integration.message", "read", "integration"),
    ("integration.message:create", "integration.message", "create", "integration"),
    ("integration.message:requeue", "integration.message", "requeue", "integration"),
    ("integration.retry:read", "integration.retry", "read", "integration"),
    ("integration.retry:review", "integration.retry", "review", "integration"),
    ("integration.retry:submit", "integration.retry", "submit", "integration"),
    ("integration.dlq:read", "integration.dlq", "read", "integration"),
    ("integration.dlq:review", "integration.dlq", "review", "integration"),
    ("integration.dlq:reprocess", "integration.dlq", "reprocess", "integration"),
    ("integration.mapping:read", "integration.mapping", "read", "integration"),
    ("integration.mapping:create", "integration.mapping", "create", "integration"),
    ("integration.mapping:update", "integration.mapping", "update", "integration"),
    ("integration.transformation:read", "integration.transformation", "read", "integration"),
    ("integration.transformation:create", "integration.transformation", "create", "integration"),
    ("integration.transformation:update", "integration.transformation", "update", "integration"),
    ("integration.sync:read", "integration.sync", "read", "integration"),
    ("integration.sync:create", "integration.sync", "create", "integration"),
    ("integration.sync:submit", "integration.sync", "submit", "integration"),
    ("integration.sync:approve", "integration.sync", "approve", "integration"),
    ("integration.sync:run", "integration.sync", "run", "integration"),
    ("integration.usage:read", "integration.usage", "read", "integration"),
    ("integration.usage:create", "integration.usage", "create", "integration"),
    ("integration.usage:update", "integration.usage", "update", "integration"),
    ("integration.rate_limit:read", "integration.rate_limit", "read", "integration"),
    ("integration.rate_limit:create", "integration.rate_limit", "create", "integration"),
    ("integration.rate_limit:update", "integration.rate_limit", "update", "integration"),
    ("integration.notification:read", "integration.notification", "read", "integration"),
    ("integration.notification:acknowledge", "integration.notification", "acknowledge", "integration"),
    ("integration.monitor:read", "integration.monitor", "read", "integration"),
    ("integration.monitor:acknowledge", "integration.monitor", "acknowledge", "integration"),
    ("integration.report:read", "integration.report", "read", "integration"),
    ("integration.report:export", "integration.report", "export", "integration"),
]

_ALL = [p[0] for p in INTEGRATION_PERMISSIONS]

INTEGRATION_ADMIN_PERMISSIONS = list(_ALL)
INTEGRATION_ENGINEER_PERMISSIONS = [
    p for p in _ALL
    if ":approve" not in p and ":review" not in p
]
API_MANAGER_PERMISSIONS = [
    p for p in _ALL
    if any(
        x in p
        for x in (
            "integration.credential",
            "integration.oauth",
            "integration.webhook",
            "integration.connector",
            "integration.system:read",
            "integration.rate_limit",
            "integration.usage",
            "integration.report:read",
        )
    )
]
SYSTEM_OPERATOR_PERMISSIONS = [
    p for p in _ALL
    if any(
        x in p
        for x in (
            "integration.queue",
            "integration.message",
            "integration.retry",
            "integration.dlq",
            "integration.sync",
            "integration.monitor",
            "integration.notification",
            "integration.report:read",
            "integration.system:read",
            "integration.connector:read",
        )
    )
]
