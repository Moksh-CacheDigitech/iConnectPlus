"""Integration application service facade."""

from sqlalchemy.orm import Session

from modules.integration.service.api_credential_service import ApiCredentialService
from modules.integration.service.api_usage_service import ApiUsageService
from modules.integration.service.connector_service import ConnectorService
from modules.integration.service.data_mapping_service import DataMappingService
from modules.integration.service.data_transformation_service import DataTransformationService
from modules.integration.service.dead_letter_service import DeadLetterService
from modules.integration.service.event_definition_service import EventDefinitionService
from modules.integration.service.event_subscription_service import EventSubscriptionService
from modules.integration.service.external_system_service import ExternalSystemService
from modules.integration.service.integration_service import IntegrationIntegrationService
from modules.integration.service.message_queue_service import MessageQueueService
from modules.integration.service.message_service import MessageService
from modules.integration.service.monitor_service import MonitorService
from modules.integration.service.notification_service import NotificationService
from modules.integration.service.oauth_client_service import OauthClientService
from modules.integration.service.rate_limit_service import RateLimitService
from modules.integration.service.report_service import ReportService
from modules.integration.service.retry_queue_service import RetryQueueService
from modules.integration.service.sync_job_service import SyncJobService
from modules.integration.service.sync_log_service import SyncLogService
from modules.integration.service.webhook_service import WebhookService


class IntegrationApplicationService:
    def __init__(self, db: Session) -> None:
        self.external_systems = ExternalSystemService(db)
        self.connectors = ConnectorService(db)
        self.api_credentials = ApiCredentialService(db)
        self.oauth_clients = OauthClientService(db)
        self.webhooks = WebhookService(db)
        self.event_definitions = EventDefinitionService(db)
        self.event_subscriptions = EventSubscriptionService(db)
        self.message_queues = MessageQueueService(db)
        self.messages = MessageService(db)
        self.retry_queues = RetryQueueService(db)
        self.dead_letters = DeadLetterService(db)
        self.data_mappings = DataMappingService(db)
        self.data_transformations = DataTransformationService(db)
        self.sync_jobs = SyncJobService(db)
        self.sync_logs = SyncLogService(db)
        self.api_usages = ApiUsageService(db)
        self.rate_limits = RateLimitService(db)
        self.notifications = NotificationService(db)
        self.monitors = MonitorService(db)
        self.reports = ReportService(db)
        self.integration = IntegrationIntegrationService(db)
