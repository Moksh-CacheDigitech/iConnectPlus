"""Integration domain enums per ERD_21 section 8."""

from enum import Enum


class ExternalSystemStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    INACTIVE = "inactive"
    RETIRED = "retired"


class ConnectorStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    ACTIVE = "active"
    INACTIVE = "inactive"
    FAILED = "failed"
    RETIRED = "retired"


class ApiCredentialStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"


class OauthClientStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    REVOKED = "revoked"


class WebhookStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    ACTIVE = "active"
    PAUSED = "paused"
    RETIRED = "retired"


class EventDefinitionStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    DEPRECATED = "deprecated"


class EventSubscriptionStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    CANCELLED = "cancelled"


class MessageQueueStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    DRAINED = "drained"


class MessageStatus(str, Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    DEAD_LETTERED = "dead_lettered"
    CANCELLED = "cancelled"


class RetryQueueStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCEEDED = "succeeded"
    EXHAUSTED = "exhausted"
    CANCELLED = "cancelled"


class DeadLetterStatus(str, Enum):
    OPEN = "open"
    REPROCESSED = "reprocessed"
    DISCARDED = "discarded"


class DataMappingStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    INACTIVE = "inactive"


class DataTransformationStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    INACTIVE = "inactive"


class SyncJobStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"


class SyncLogStatus(str, Enum):
    RECORDED = "recorded"


class ApiUsageStatus(str, Enum):
    RECORDED = "recorded"


class RateLimitStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class NotificationStatus(str, Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"


class MonitorStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    DOWN = "down"
    UNKNOWN = "unknown"
    INACTIVE = "inactive"


class ReportStatus(str, Enum):
    DRAFT = "draft"
    FINALIZED = "finalized"


class IntegrationEntityType(str, Enum):
    EXTERNAL_SYSTEM = "external_system"
    CONNECTOR = "connector"
    API_CREDENTIAL = "api_credential"
    OAUTH_CLIENT = "oauth_client"
    WEBHOOK = "webhook"
    EVENT_SUBSCRIPTION = "event_subscription"
    MESSAGE = "message"
    RETRY_QUEUE = "retry_queue"
    DEAD_LETTER = "dead_letter"
    SYNC_JOB = "sync_job"


CODE_PREFIXES: dict[IntegrationEntityType, tuple[str, int, bool]] = {
    IntegrationEntityType.EXTERNAL_SYSTEM: ("SYS-", 6, True),
    IntegrationEntityType.CONNECTOR: ("CON-", 6, True),
    IntegrationEntityType.API_CREDENTIAL: ("CRD-", 6, True),
    IntegrationEntityType.OAUTH_CLIENT: ("OAU-", 6, True),
    IntegrationEntityType.WEBHOOK: ("WHK-", 6, True),
    IntegrationEntityType.EVENT_SUBSCRIPTION: ("ESB-", 6, True),
    IntegrationEntityType.MESSAGE: ("MSG-", 6, True),
    IntegrationEntityType.RETRY_QUEUE: ("RTY-", 6, True),
    IntegrationEntityType.DEAD_LETTER: ("DLQ-", 6, True),
    IntegrationEntityType.SYNC_JOB: ("SYN-", 6, True),
}
