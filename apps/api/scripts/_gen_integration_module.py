"""Generate Sprint 21 Enterprise Integration Hub module. Run from apps/api:
.venv\\Scripts\\python.exe scripts/_gen_integration_module.py
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
INTEGRATION = SRC / "modules" / "integration"
ALEMBIC = ROOT / "alembic" / "versions"
TESTS = SRC / "tests"
SHARED = SRC / "shared"

FILES_WRITTEN: list[Path] = []

WF_FIELDS = """
    workflow_status: Mapped[str | None] = mapped_column(String(30), nullable=True)
    workflow_instance_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("foundation.wf_instance.id", ondelete="SET NULL"),
        nullable=True,
    )
"""

OPT_BRANCH = """
    branch_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organization.org_branch.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
"""


def w(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not content.endswith("\n"):
        content += "\n"
    path.write_text(content, encoding="utf-8")
    FILES_WRITTEN.append(path)
    print("wrote", path.relative_to(ROOT))


def patch_file(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if new.strip() in text:
        print("skip (already)", path.relative_to(ROOT))
        return
    if old not in text:
        raise SystemExit(f"patch failed in {path}: marker not found")
    path.write_text(text.replace(old, new), encoding="utf-8")
    print("patched", path.relative_to(ROOT))


# table_key, ORM class, stem, branch_scoped
TABLES: list[tuple[str, str, str, bool]] = [
    ("external_system", "IntExternalSystem", "ExternalSystem", False),
    ("connector", "IntConnector", "Connector", False),
    ("api_credential", "IntApiCredential", "ApiCredential", False),
    ("oauth_client", "IntOauthClient", "OauthClient", False),
    ("webhook", "IntWebhook", "Webhook", False),
    ("event_definition", "IntEventDefinition", "EventDefinition", False),
    ("event_subscription", "IntEventSubscription", "EventSubscription", False),
    ("message_queue", "IntMessageQueue", "MessageQueue", False),
    ("message", "IntMessage", "Message", False),
    ("retry_queue", "IntRetryQueue", "RetryQueue", False),
    ("dead_letter", "IntDeadLetter", "DeadLetter", False),
    ("data_mapping", "IntDataMapping", "DataMapping", False),
    ("data_transformation", "IntDataTransformation", "DataTransformation", False),
    ("sync_job", "IntSyncJob", "SyncJob", False),
    ("sync_log", "IntSyncLog", "SyncLog", False),
    ("api_usage", "IntApiUsage", "ApiUsage", False),
    ("rate_limit", "IntRateLimit", "RateLimit", False),
    ("notification", "IntNotification", "Notification", False),
    ("monitor", "IntMonitor", "Monitor", False),
    ("report", "IntReport", "Report", False),
]

CLASS_MAP = {t[0]: t[1] for t in TABLES}

MIGRATIONS: list[tuple[str, str | list[str], str]] = [
    ("0377_create_integration_schema", "schema", "0376_seed_analytics_workflows"),
    ("0378_int_external_system", "external_system", "0377_create_integration_schema"),
    ("0379_int_connector", "connector", "0378_int_external_system"),
    ("0380_int_api_credential", "api_credential", "0379_int_connector"),
    ("0381_int_oauth_client", "oauth_client", "0380_int_api_credential"),
    ("0382_int_webhook", "webhook", "0381_int_oauth_client"),
    ("0383_int_event_definition", "event_definition", "0382_int_webhook"),
    ("0384_int_event_subscription", "event_subscription", "0383_int_event_definition"),
    ("0385_int_message_queue", "message_queue", "0384_int_event_subscription"),
    ("0386_int_message", "message", "0385_int_message_queue"),
    ("0387_int_retry_and_dlq", ["retry_queue", "dead_letter"], "0386_int_message"),
    ("0388_int_data_mapping", "data_mapping", "0387_int_retry_and_dlq"),
    ("0389_int_data_transformation", "data_transformation", "0388_int_data_mapping"),
    ("0390_int_sync_job", "sync_job", "0389_int_data_transformation"),
    ("0391_int_sync_log", "sync_log", "0390_int_sync_job"),
    ("0392_int_api_usage", "api_usage", "0391_int_sync_log"),
    ("0393_int_rate_limit", "rate_limit", "0392_int_api_usage"),
    ("0394_int_notification", "notification", "0393_int_rate_limit"),
    ("0395_int_monitor", "monitor", "0394_int_notification"),
    ("0396_int_report", "report", "0395_int_monitor"),
    ("0397_seed_int_permissions", "seed_perms", "0396_int_report"),
    ("0398_seed_integration_workflows", "seed_wf", "0397_seed_int_permissions"),
]

# route prefix, schema name, service class, perm resource, branch_required
ROUTE_SPECS: list[tuple[str, str, str, str, bool]] = [
    ("external-systems", "ExternalSystem", "ExternalSystemService", "integration.system", False),
    ("connectors", "Connector", "ConnectorService", "integration.connector", False),
    ("api-credentials", "ApiCredential", "ApiCredentialService", "integration.credential", False),
    ("oauth-clients", "OauthClient", "OauthClientService", "integration.oauth", False),
    ("webhooks", "Webhook", "WebhookService", "integration.webhook", False),
    ("event-definitions", "EventDefinition", "EventDefinitionService", "integration.event", False),
    ("event-subscriptions", "EventSubscription", "EventSubscriptionService", "integration.subscription", False),
    ("message-queues", "MessageQueue", "MessageQueueService", "integration.queue", False),
    ("messages", "Message", "MessageService", "integration.message", False),
    ("retry-queues", "RetryQueue", "RetryQueueService", "integration.retry", False),
    ("dead-letters", "DeadLetter", "DeadLetterService", "integration.dlq", False),
    ("data-mappings", "DataMapping", "DataMappingService", "integration.mapping", False),
    ("data-transformations", "DataTransformation", "DataTransformationService", "integration.transformation", False),
    ("sync-jobs", "SyncJob", "SyncJobService", "integration.sync", False),
    ("sync-logs", "SyncLog", "SyncLogService", "integration.sync", False),
    ("api-usages", "ApiUsage", "ApiUsageService", "integration.usage", False),
    ("rate-limits", "RateLimit", "RateLimitService", "integration.rate_limit", False),
    ("notifications", "Notification", "NotificationService", "integration.notification", False),
    ("monitors", "Monitor", "MonitorService", "integration.monitor", False),
    ("reports", "Report", "ReportService", "integration.report", False),
]

ENGINE_NAMES = [
    "ExternalSystem",
    "Connector",
    "ApiCredential",
    "OauthClient",
    "Webhook",
    "EventDefinition",
    "EventSubscription",
    "MessageQueue",
    "Message",
    "RetryQueue",
    "DeadLetter",
    "DataMapping",
    "DataTransformation",
    "SyncJob",
    "SyncLog",
    "ApiUsage",
    "RateLimit",
    "Notification",
    "Monitor",
    "Report",
]

ENGINE_FILE_MAP = {
    "ExternalSystem": "external_system",
    "Connector": "connector",
    "ApiCredential": "api_credential",
    "OauthClient": "oauth_client",
    "Webhook": "webhook",
    "EventDefinition": "event_definition",
    "EventSubscription": "event_subscription",
    "MessageQueue": "message_queue",
    "Message": "message",
    "RetryQueue": "retry_queue",
    "DeadLetter": "dead_letter",
    "DataMapping": "data_mapping",
    "DataTransformation": "data_transformation",
    "SyncJob": "sync_job",
    "SyncLog": "sync_log",
    "ApiUsage": "api_usage",
    "RateLimit": "rate_limit",
    "Notification": "notification",
    "Monitor": "monitor",
    "Report": "report",
}


def _emp_fk(col: str, nullable: bool = True) -> str:
    null = "True" if nullable else "False"
    mapped = "UUID | None" if nullable else "UUID"
    return f'''
    {col}: Mapped[{mapped}] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_employee.id", ondelete="RESTRICT"),
        nullable={null},
        index=True,
    )'''


def _dept_fk(col: str = "department_id", nullable: bool = True) -> str:
    null = "True" if nullable else "False"
    mapped = "UUID | None" if nullable else "UUID"
    return f'''
    {col}: Mapped[{mapped}] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organization.org_department.id", ondelete="RESTRICT"),
        nullable={null},
        index=True,
    )'''


def _customer_fk(col: str = "customer_id", nullable: bool = True) -> str:
    null = "True" if nullable else "False"
    mapped = "UUID | None" if nullable else "UUID"
    return f'''
    {col}: Mapped[{mapped}] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_customer.id", ondelete="RESTRICT"),
        nullable={null},
        index=True,
    )'''


def _vendor_fk(col: str = "vendor_id", nullable: bool = True) -> str:
    null = "True" if nullable else "False"
    mapped = "UUID | None" if nullable else "UUID"
    return f'''
    {col}: Mapped[{mapped}] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_vendor.id", ondelete="RESTRICT"),
        nullable={null},
        index=True,
    )'''


def _uuid_only(col: str) -> str:
    return f'''
    {col}: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)'''


def _fk(
    col: str,
    table: str,
    *,
    nullable: bool = True,
    ondelete: str = "SET NULL",
    use_alter: bool = False,
    name: str | None = None,
) -> str:
    null = "True" if nullable else "False"
    mapped = "UUID | None" if nullable else "UUID"
    extra = ""
    if use_alter:
        fk_name = name or f"fk_int_{col}"
        extra = f',\n            use_alter=True,\n            name="{fk_name}"'
    return f'''
    {col}: Mapped[{mapped}] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey(
            "{table}",
            ondelete="{ondelete}"{extra},
        ),
        nullable={null},
        index=True,
    )'''


MODELS: dict[str, str] = {}

MODELS["external_system"] = f'''"""External system ORM per ERD_21 section 5.1."""

from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.integration.models.mixins import IntRowMixin


class IntExternalSystem(Base, *IntRowMixin):
    __tablename__ = "int_external_system"
    __table_args__ = (
        UniqueConstraint("company_id", "system_number", name="uk_int_external_system_number"),
        UniqueConstraint("company_id", "system_code", name="uk_int_external_system_code"),
        CheckConstraint(
            "system_type IN ('bank','payment_gateway','tax','ecommerce','crm_external','custom')",
            name="ck_int_external_system_type",
        ),
        CheckConstraint(
            "environment IN ('sandbox','production')",
            name="ck_int_external_system_env",
        ),
        CheckConstraint(
            "status IN ('draft','active','inactive','retired')",
            name="ck_int_external_system_status",
        ),
        Index("ix_int_ext_sys_tenant_co_status", "tenant_id", "company_id", "status"),
        {{"schema": "integration"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
{OPT_BRANCH}
    system_number: Mapped[str] = mapped_column(String(50), nullable=False)
    system_code: Mapped[str] = mapped_column(String(50), nullable=False)
    system_name: Mapped[str] = mapped_column(String(255), nullable=False)
    system_type: Mapped[str] = mapped_column(String(40), nullable=False)
    base_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    environment: Mapped[str] = mapped_column(String(20), nullable=False, default="sandbox")
{_emp_fk("owner_employee_id")}
{_dept_fk()}
{_vendor_fk()}
{_customer_fk()}
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)
'''

MODELS["connector"] = f'''"""Connector ORM per ERD_21 section 5.2."""

from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.integration.models.mixins import IntRowMixin


class IntConnector(Base, *IntRowMixin):
    __tablename__ = "int_connector"
    __table_args__ = (
        UniqueConstraint("company_id", "connector_number", name="uk_int_connector_number"),
        CheckConstraint(
            "connector_protocol IN ('rest','webhook','queue','sftp','soap')",
            name="ck_int_connector_protocol",
        ),
        CheckConstraint(
            "direction IN ('inbound','outbound','bidirectional')",
            name="ck_int_connector_direction",
        ),
        CheckConstraint(
            "status IN ('draft','submitted','approved','active','inactive','failed','retired')",
            name="ck_int_connector_status",
        ),
        Index("ix_int_connector_tenant_co_status", "tenant_id", "company_id", "status"),
        {{"schema": "integration"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
{OPT_BRANCH}
    connector_number: Mapped[str] = mapped_column(String(50), nullable=False)
    connector_code: Mapped[str] = mapped_column(String(50), nullable=False)
    connector_name: Mapped[str] = mapped_column(String(255), nullable=False)
    external_system_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("integration.int_external_system.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    connector_protocol: Mapped[str] = mapped_column(String(30), nullable=False)
    direction: Mapped[str] = mapped_column(String(20), nullable=False)
{_emp_fk("owner_employee_id")}
    config_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
{_fk("credential_id", "integration.int_api_credential.id", use_alter=True, name="fk_int_conn_cred")}
{_fk("oauth_client_id", "integration.int_oauth_client.id", use_alter=True, name="fk_int_conn_oauth")}
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)
{WF_FIELDS}
'''

MODELS["api_credential"] = f'''"""API credential ORM per ERD_21 section 5.3."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.integration.models.mixins import IntRowMixin


class IntApiCredential(Base, *IntRowMixin):
    __tablename__ = "int_api_credential"
    __table_args__ = (
        UniqueConstraint("company_id", "credential_number", name="uk_int_api_credential_number"),
        CheckConstraint(
            "credential_type IN ('api_key','basic','bearer','custom_header')",
            name="ck_int_api_credential_type",
        ),
        CheckConstraint(
            "status IN ('draft','submitted','approved','active','expired','revoked')",
            name="ck_int_api_credential_status",
        ),
        Index("ix_int_api_cred_tenant_co_status", "tenant_id", "company_id", "status"),
        {{"schema": "integration"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
{OPT_BRANCH}
    credential_number: Mapped[str] = mapped_column(String(50), nullable=False)
    external_system_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("integration.int_external_system.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    credential_type: Mapped[str] = mapped_column(String(30), nullable=False)
    secret_vault_ref: Mapped[str] = mapped_column(String(255), nullable=False)
    key_hint: Mapped[str | None] = mapped_column(String(100), nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    rotated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
{_emp_fk("owner_employee_id")}
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)
{WF_FIELDS}
'''

MODELS["oauth_client"] = f'''"""OAuth client ORM per ERD_21 section 5.4."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.integration.models.mixins import IntRowMixin


class IntOauthClient(Base, *IntRowMixin):
    __tablename__ = "int_oauth_client"
    __table_args__ = (
        UniqueConstraint("company_id", "client_number", name="uk_int_oauth_client_number"),
        CheckConstraint(
            "grant_type IN ('client_credentials','authorization_code','refresh_token')",
            name="ck_int_oauth_grant_type",
        ),
        CheckConstraint(
            "status IN ('draft','active','revoked')",
            name="ck_int_oauth_client_status",
        ),
        Index("ix_int_oauth_tenant_co_status", "tenant_id", "company_id", "status"),
        {{"schema": "integration"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
{OPT_BRANCH}
    client_number: Mapped[str] = mapped_column(String(50), nullable=False)
    external_system_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("integration.int_external_system.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    client_id_public: Mapped[str] = mapped_column(String(255), nullable=False)
    client_secret_vault_ref: Mapped[str] = mapped_column(String(255), nullable=False)
    token_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    authorize_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    scopes: Mapped[str | None] = mapped_column(String(500), nullable=True)
    grant_type: Mapped[str] = mapped_column(String(40), nullable=False)
    token_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)
'''

MODELS["webhook"] = f'''"""Webhook ORM per ERD_21 section 5.5."""

from uuid import UUID, uuid4

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.integration.models.mixins import IntRowMixin


class IntWebhook(Base, *IntRowMixin):
    __tablename__ = "int_webhook"
    __table_args__ = (
        UniqueConstraint("company_id", "webhook_number", name="uk_int_webhook_number"),
        CheckConstraint(
            "direction IN ('inbound','outbound')",
            name="ck_int_webhook_direction",
        ),
        CheckConstraint(
            "status IN ('draft','submitted','approved','active','paused','retired')",
            name="ck_int_webhook_status",
        ),
        Index("ix_int_webhook_tenant_co_status", "tenant_id", "company_id", "status"),
        {{"schema": "integration"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
{OPT_BRANCH}
    webhook_number: Mapped[str] = mapped_column(String(50), nullable=False)
{_fk("external_system_id", "integration.int_external_system.id", nullable=True, ondelete="RESTRICT")}
{_fk("connector_id", "integration.int_connector.id", nullable=True, ondelete="RESTRICT")}
    direction: Mapped[str] = mapped_column(String(20), nullable=False)
    target_url: Mapped[str] = mapped_column(String(500), nullable=False)
{_fk("event_definition_id", "integration.int_event_definition.id", use_alter=True, name="fk_int_wh_event_def")}
    secret_vault_ref: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
{_emp_fk("owner_employee_id")}
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)
{WF_FIELDS}
'''

MODELS["event_definition"] = f'''"""Event definition ORM per ERD_21 section 5.6."""

from uuid import UUID, uuid4

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.integration.models.mixins import IntRowMixin


class IntEventDefinition(Base, *IntRowMixin):
    __tablename__ = "int_event_definition"
    __table_args__ = (
        UniqueConstraint("company_id", "event_code", name="uk_int_event_definition_code"),
        CheckConstraint(
            "source_module IN ('foundation','finance','sales','procurement','inventory',"
            "'manufacturing','quality','crm','hr','payroll','recruitment','project','asset',"
            "'service','helpdesk','document','grc','analytics','integration','external')",
            name="ck_int_event_def_source_module",
        ),
        CheckConstraint(
            "status IN ('draft','active','deprecated')",
            name="ck_int_event_definition_status",
        ),
        {{"schema": "integration"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
{OPT_BRANCH}
    event_code: Mapped[str] = mapped_column(String(100), nullable=False)
    event_name: Mapped[str] = mapped_column(String(255), nullable=False)
    source_module: Mapped[str] = mapped_column(String(40), nullable=False)
    payload_schema_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    version_no: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)
'''

MODELS["event_subscription"] = f'''"""Event subscription ORM per ERD_21 section 5.7."""

from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.integration.models.mixins import IntRowMixin


class IntEventSubscription(Base, *IntRowMixin):
    __tablename__ = "int_event_subscription"
    __table_args__ = (
        UniqueConstraint("company_id", "subscription_number", name="uk_int_event_sub_number"),
        CheckConstraint(
            "subscriber_type IN ('webhook','queue','connector','internal_handler')",
            name="ck_int_event_sub_type",
        ),
        CheckConstraint(
            "status IN ('active','paused','cancelled')",
            name="ck_int_event_sub_status",
        ),
        Index("ix_int_event_sub_tenant_co_status", "tenant_id", "company_id", "status"),
        {{"schema": "integration"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
{OPT_BRANCH}
    subscription_number: Mapped[str] = mapped_column(String(50), nullable=False)
    event_definition_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("integration.int_event_definition.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    subscriber_type: Mapped[str] = mapped_column(String(30), nullable=False)
{_fk("webhook_id", "integration.int_webhook.id")}
{_fk("message_queue_id", "integration.int_message_queue.id", use_alter=True, name="fk_int_sub_queue")}
{_fk("connector_id", "integration.int_connector.id")}
    filter_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active", index=True)
'''

MODELS["message_queue"] = f'''"""Message queue ORM per ERD_21 section 5.8."""

from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.integration.models.mixins import IntRowMixin


class IntMessageQueue(Base, *IntRowMixin):
    __tablename__ = "int_message_queue"
    __table_args__ = (
        UniqueConstraint("company_id", "queue_code", name="uk_int_message_queue_code"),
        CheckConstraint(
            "queue_type IN ('standard','fifo','priority')",
            name="ck_int_message_queue_type",
        ),
        CheckConstraint(
            "status IN ('active','paused','drained')",
            name="ck_int_message_queue_status",
        ),
        {{"schema": "integration"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
{OPT_BRANCH}
    queue_code: Mapped[str] = mapped_column(String(50), nullable=False)
    queue_name: Mapped[str] = mapped_column(String(255), nullable=False)
    queue_type: Mapped[str] = mapped_column(String(30), nullable=False, default="standard")
    max_retries: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    visibility_timeout_sec: Mapped[int] = mapped_column(Integer, nullable=False, default=30)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active", index=True)
'''

MODELS["message"] = f'''"""Message ORM per ERD_21 section 5.9."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.integration.models.mixins import IntRowMixin


class IntMessage(Base, *IntRowMixin):
    __tablename__ = "int_message"
    __table_args__ = (
        UniqueConstraint("company_id", "message_number", name="uk_int_message_number"),
        CheckConstraint(
            "status IN ('queued','processing','succeeded','failed','dead_lettered','cancelled')",
            name="ck_int_message_status",
        ),
        Index("ix_int_message_tenant_co_status", "tenant_id", "company_id", "status"),
        {{"schema": "integration"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
{OPT_BRANCH}
    message_number: Mapped[str] = mapped_column(String(50), nullable=False)
    message_queue_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("integration.int_message_queue.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
{_fk("event_definition_id", "integration.int_event_definition.id")}
    correlation_id: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    payload_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    source_module: Mapped[str | None] = mapped_column(String(40), nullable=True)
{_uuid_only("entity_ref_id")}
{_uuid_only("finance_event_ref_id")}
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    available_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="queued", index=True)
'''

MODELS["retry_queue"] = f'''"""Retry queue ORM per ERD_21 section 5.10."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.integration.models.mixins import IntRowMixin


class IntRetryQueue(Base, *IntRowMixin):
    __tablename__ = "int_retry_queue"
    __table_args__ = (
        UniqueConstraint("company_id", "retry_number", name="uk_int_retry_queue_number"),
        CheckConstraint(
            "status IN ('pending','processing','succeeded','exhausted','cancelled')",
            name="ck_int_retry_queue_status",
        ),
        Index("ix_int_retry_tenant_co_status", "tenant_id", "company_id", "status"),
        {{"schema": "integration"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
{OPT_BRANCH}
    retry_number: Mapped[str] = mapped_column(String(50), nullable=False)
    message_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("integration.int_message.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    attempt_no: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    next_attempt_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="pending", index=True)
{WF_FIELDS}
'''

MODELS["dead_letter"] = f'''"""Dead letter ORM per ERD_21 section 5.11."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.integration.models.mixins import IntRowMixin


class IntDeadLetter(Base, *IntRowMixin):
    __tablename__ = "int_dead_letter"
    __table_args__ = (
        UniqueConstraint("company_id", "dlq_number", name="uk_int_dead_letter_number"),
        CheckConstraint(
            "status IN ('open','reprocessed','discarded')",
            name="ck_int_dead_letter_status",
        ),
        Index("ix_int_dlq_tenant_co_status", "tenant_id", "company_id", "status"),
        {{"schema": "integration"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
{OPT_BRANCH}
    dlq_number: Mapped[str] = mapped_column(String(50), nullable=False)
    message_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("integration.int_message.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
{_fk("retry_id", "integration.int_retry_queue.id")}
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    payload_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    failed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    reprocessed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="open", index=True)
'''

MODELS["data_mapping"] = f'''"""Data mapping ORM per ERD_21 section 5.12."""

from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.integration.models.mixins import IntRowMixin


class IntDataMapping(Base, *IntRowMixin):
    __tablename__ = "int_data_mapping"
    __table_args__ = (
        UniqueConstraint("company_id", "mapping_code", name="uk_int_data_mapping_code"),
        CheckConstraint(
            "status IN ('draft','active','inactive')",
            name="ck_int_data_mapping_status",
        ),
        {{"schema": "integration"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
{OPT_BRANCH}
    mapping_code: Mapped[str] = mapped_column(String(50), nullable=False)
    mapping_name: Mapped[str] = mapped_column(String(255), nullable=False)
    connector_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("integration.int_connector.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    source_entity: Mapped[str | None] = mapped_column(String(100), nullable=True)
    target_entity: Mapped[str | None] = mapped_column(String(100), nullable=True)
    mapping_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)
'''

MODELS["data_transformation"] = f'''"""Data transformation ORM per ERD_21 section 5.13."""

from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.integration.models.mixins import IntRowMixin


class IntDataTransformation(Base, *IntRowMixin):
    __tablename__ = "int_data_transformation"
    __table_args__ = (
        UniqueConstraint("mapping_id", "transformation_code", name="uk_int_data_xform_code"),
        CheckConstraint(
            "transform_type IN ('jolt','template','script_ref','expression')",
            name="ck_int_data_xform_type",
        ),
        CheckConstraint(
            "status IN ('draft','active','inactive')",
            name="ck_int_data_xform_status",
        ),
        {{"schema": "integration"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
{OPT_BRANCH}
    transformation_code: Mapped[str] = mapped_column(String(50), nullable=False)
    transformation_name: Mapped[str] = mapped_column(String(255), nullable=False)
    mapping_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("integration.int_data_mapping.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    transform_type: Mapped[str] = mapped_column(String(30), nullable=False)
    definition_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    sequence_no: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)
'''

MODELS["sync_job"] = f'''"""Sync job ORM per ERD_21 section 5.14."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.integration.models.mixins import IntRowMixin


class IntSyncJob(Base, *IntRowMixin):
    __tablename__ = "int_sync_job"
    __table_args__ = (
        UniqueConstraint("company_id", "sync_number", name="uk_int_sync_job_number"),
        CheckConstraint(
            "sync_mode IN ('full','incremental','realtime')",
            name="ck_int_sync_job_mode",
        ),
        CheckConstraint(
            "direction IN ('pull','push','bidirectional')",
            name="ck_int_sync_job_direction",
        ),
        CheckConstraint(
            "status IN ('draft','submitted','approved','queued','running','succeeded','failed','cancelled')",
            name="ck_int_sync_job_status",
        ),
        Index("ix_int_sync_job_tenant_co_status", "tenant_id", "company_id", "status"),
        {{"schema": "integration"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
{OPT_BRANCH}
    sync_number: Mapped[str] = mapped_column(String(50), nullable=False)
    connector_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("integration.int_connector.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
{_fk("mapping_id", "integration.int_data_mapping.id")}
    sync_mode: Mapped[str] = mapped_column(String(30), nullable=False)
    direction: Mapped[str] = mapped_column(String(20), nullable=False)
    schedule_cron: Mapped[str | None] = mapped_column(String(100), nullable=True)
{_emp_fk("requested_by_employee_id", nullable=False)}
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    rows_processed: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)
{WF_FIELDS}
'''

MODELS["sync_log"] = f'''"""Sync log ORM per ERD_21 section 5.15."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.integration.models.mixins import IntRowMixin


class IntSyncLog(Base, *IntRowMixin):
    __tablename__ = "int_sync_log"
    __table_args__ = (
        CheckConstraint(
            "level IN ('info','warn','error')",
            name="ck_int_sync_log_level",
        ),
        CheckConstraint("status IN ('recorded')", name="ck_int_sync_log_status"),
        {{"schema": "integration"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
{OPT_BRANCH}
    sync_job_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("integration.int_sync_job.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    logged_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    level: Mapped[str] = mapped_column(String(10), nullable=False, default="info")
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
{_uuid_only("entity_ref_id")}
    payload_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="recorded", index=True)
'''

MODELS["api_usage"] = f'''"""API usage ORM per ERD_21 section 5.16."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import BigInteger, CheckConstraint, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.integration.models.mixins import IntRowMixin


class IntApiUsage(Base, *IntRowMixin):
    __tablename__ = "int_api_usage"
    __table_args__ = (
        CheckConstraint("status IN ('recorded')", name="ck_int_api_usage_status"),
        {{"schema": "integration"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
{OPT_BRANCH}
{_fk("credential_id", "integration.int_api_credential.id")}
{_fk("oauth_client_id", "integration.int_oauth_client.id")}
{_fk("connector_id", "integration.int_connector.id")}
    occurred_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    endpoint: Mapped[str | None] = mapped_column(String(500), nullable=True)
    http_method: Mapped[str | None] = mapped_column(String(10), nullable=True)
    status_code: Mapped[int | None] = mapped_column(Integer, nullable=True)
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    bytes_in: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    bytes_out: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="recorded", index=True)
'''

MODELS["rate_limit"] = f'''"""Rate limit ORM per ERD_21 section 5.17."""

from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.integration.models.mixins import IntRowMixin


class IntRateLimit(Base, *IntRowMixin):
    __tablename__ = "int_rate_limit"
    __table_args__ = (
        UniqueConstraint("company_id", "limit_code", name="uk_int_rate_limit_code"),
        CheckConstraint(
            "status IN ('active','inactive')",
            name="ck_int_rate_limit_status",
        ),
        {{"schema": "integration"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
{OPT_BRANCH}
    limit_code: Mapped[str] = mapped_column(String(50), nullable=False)
{_fk("external_system_id", "integration.int_external_system.id")}
{_fk("credential_id", "integration.int_api_credential.id")}
{_fk("connector_id", "integration.int_connector.id")}
    window_seconds: Mapped[int] = mapped_column(Integer, nullable=False)
    max_requests: Mapped[int] = mapped_column(Integer, nullable=False)
    burst_max: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active", index=True)
'''

MODELS["notification"] = f'''"""Integration notification ORM per ERD_21 section 5.18."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.integration.models.mixins import IntRowMixin


class IntNotification(Base, *IntRowMixin):
    __tablename__ = "int_notification"
    __table_args__ = (
        CheckConstraint(
            "related_entity_type IN ('connector','webhook','sync','retry','dlq','credential','monitor')",
            name="ck_int_notification_entity_type",
        ),
        CheckConstraint(
            "notification_type IN ('sync_failed','dlq_created','credential_expiring',"
            "'rate_limit_hit','monitor_down','other')",
            name="ck_int_notification_type",
        ),
        CheckConstraint(
            "delivery_status IN ('pending','sent','failed','read')",
            name="ck_int_notification_delivery",
        ),
        CheckConstraint(
            "status IN ('active','archived')",
            name="ck_int_notification_status",
        ),
        {{"schema": "integration"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
{OPT_BRANCH}
{_fk("connector_id", "integration.int_connector.id")}
    related_entity_type: Mapped[str] = mapped_column(String(40), nullable=False)
    related_entity_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    notification_type: Mapped[str] = mapped_column(String(40), nullable=False)
{_uuid_only("recipient_user_id")}
{_emp_fk("recipient_employee_id")}
    payload_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    delivery_status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active", index=True)
'''

MODELS["monitor"] = f'''"""Monitor ORM per ERD_21 section 5.19."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.integration.models.mixins import IntRowMixin


class IntMonitor(Base, *IntRowMixin):
    __tablename__ = "int_monitor"
    __table_args__ = (
        UniqueConstraint("company_id", "monitor_code", name="uk_int_monitor_code"),
        CheckConstraint(
            "check_type IN ('heartbeat','latency','error_rate','queue_depth')",
            name="ck_int_monitor_check_type",
        ),
        CheckConstraint(
            "status IN ('healthy','degraded','down','unknown','inactive')",
            name="ck_int_monitor_status",
        ),
        {{"schema": "integration"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
{OPT_BRANCH}
    monitor_code: Mapped[str] = mapped_column(String(50), nullable=False)
    monitor_name: Mapped[str] = mapped_column(String(255), nullable=False)
{_fk("external_system_id", "integration.int_external_system.id")}
{_fk("connector_id", "integration.int_connector.id")}
    check_type: Mapped[str] = mapped_column(String(30), nullable=False)
    threshold_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    last_checked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_status: Mapped[str | None] = mapped_column(String(30), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="unknown", index=True)
'''

MODELS["report"] = f'''"""Integration report ORM per ERD_21 section 5.20."""

from datetime import date, datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, Date, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.integration.models.mixins import IntRowMixin


class IntReport(Base, *IntRowMixin):
    __tablename__ = "int_report"
    __table_args__ = (
        UniqueConstraint("company_id", "report_code", name="uk_int_report_code"),
        CheckConstraint(
            "report_type IN ('delivery_success','dlq_aging','sync_performance',"
            "'api_usage','rate_limit_breaches','connector_health')",
            name="ck_int_report_type",
        ),
        CheckConstraint(
            "status IN ('draft','finalized')",
            name="ck_int_report_status",
        ),
        {{"schema": "integration"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
{OPT_BRANCH}
    report_code: Mapped[str] = mapped_column(String(50), nullable=False)
    report_type: Mapped[str] = mapped_column(String(40), nullable=False)
{_fk("external_system_id", "integration.int_external_system.id")}
    period_start: Mapped[date | None] = mapped_column(Date, nullable=True)
    period_end: Mapped[date | None] = mapped_column(Date, nullable=True)
    metrics_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    generated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)
'''

# Engine bodies continued in part 2 — written by gen via ENGINE_BODIES below
ENGINE_BODIES: dict[str, str] = {
    "ExternalSystem": '''
class ExternalSystemEngine:
    def activate(self, row) -> None:
        row.status = ExternalSystemStatus.ACTIVE.value

    def deactivate(self, row) -> None:
        row.status = ExternalSystemStatus.INACTIVE.value

    def retire(self, row) -> None:
        row.status = ExternalSystemStatus.RETIRED.value
''',
    "Connector": '''
class ConnectorEngine:
    def submit(self, row) -> None:
        if row.status != ConnectorStatus.DRAFT.value:
            raise InvalidConnectorState("Only draft connectors can be submitted")
        row.status = ConnectorStatus.SUBMITTED.value

    def approve(self, row) -> None:
        if row.status != ConnectorStatus.SUBMITTED.value:
            raise InvalidConnectorState("Only submitted connectors can be approved")
        row.status = ConnectorStatus.APPROVED.value

    def activate(self, row) -> None:
        row.status = ConnectorStatus.ACTIVE.value

    def deactivate(self, row) -> None:
        row.status = ConnectorStatus.INACTIVE.value

    def mark_failed(self, row) -> None:
        row.status = ConnectorStatus.FAILED.value

    def retire(self, row) -> None:
        row.status = ConnectorStatus.RETIRED.value
''',
    "ApiCredential": '''
class ApiCredentialEngine:
    def submit(self, row) -> None:
        if row.status != ApiCredentialStatus.DRAFT.value:
            raise InvalidApiCredentialState("Only draft credentials can be submitted")
        row.status = ApiCredentialStatus.SUBMITTED.value

    def approve(self, row) -> None:
        if row.status != ApiCredentialStatus.SUBMITTED.value:
            raise InvalidApiCredentialState("Only submitted credentials can be approved")
        row.status = ApiCredentialStatus.APPROVED.value

    def activate(self, row) -> None:
        row.status = ApiCredentialStatus.ACTIVE.value

    def revoke(self, row) -> None:
        row.status = ApiCredentialStatus.REVOKED.value

    def expire(self, row) -> None:
        row.status = ApiCredentialStatus.EXPIRED.value
''',
    "OauthClient": '''
class OauthClientEngine:
    def activate(self, row) -> None:
        row.status = OauthClientStatus.ACTIVE.value

    def revoke(self, row) -> None:
        row.status = OauthClientStatus.REVOKED.value
''',
    "Webhook": '''
class WebhookEngine:
    def submit(self, row) -> None:
        if row.status != WebhookStatus.DRAFT.value:
            raise InvalidWebhookState("Only draft webhooks can be submitted")
        row.status = WebhookStatus.SUBMITTED.value

    def approve(self, row) -> None:
        if row.status != WebhookStatus.SUBMITTED.value:
            raise InvalidWebhookState("Only submitted webhooks can be approved")
        row.status = WebhookStatus.APPROVED.value

    def activate(self, row) -> None:
        row.status = WebhookStatus.ACTIVE.value
        row.is_enabled = True

    def pause(self, row) -> None:
        row.status = WebhookStatus.PAUSED.value
        row.is_enabled = False

    def retire(self, row) -> None:
        row.status = WebhookStatus.RETIRED.value
        row.is_enabled = False
''',
    "EventDefinition": '''
class EventDefinitionEngine:
    def activate(self, row) -> None:
        row.status = EventDefinitionStatus.ACTIVE.value
        row.is_active = True

    def deprecate(self, row) -> None:
        row.status = EventDefinitionStatus.DEPRECATED.value
        row.is_active = False
''',
    "EventSubscription": '''
class EventSubscriptionEngine:
    def pause(self, row) -> None:
        row.status = EventSubscriptionStatus.PAUSED.value

    def activate(self, row) -> None:
        row.status = EventSubscriptionStatus.ACTIVE.value

    def cancel(self, row) -> None:
        row.status = EventSubscriptionStatus.CANCELLED.value
''',
    "MessageQueue": '''
class MessageQueueEngine:
    def pause(self, row) -> None:
        row.status = MessageQueueStatus.PAUSED.value

    def activate(self, row) -> None:
        row.status = MessageQueueStatus.ACTIVE.value

    def drain(self, row) -> None:
        row.status = MessageQueueStatus.DRAINED.value
''',
    "Message": '''
class MessageEngine:
    def start_processing(self, row) -> None:
        row.status = MessageStatus.PROCESSING.value

    def succeed(self, row) -> None:
        row.status = MessageStatus.SUCCEEDED.value

    def fail(self, row) -> None:
        row.status = MessageStatus.FAILED.value

    def dead_letter(self, row) -> None:
        row.status = MessageStatus.DEAD_LETTERED.value

    def cancel(self, row) -> None:
        row.status = MessageStatus.CANCELLED.value
''',
    "RetryQueue": '''
class RetryQueueEngine:
    def submit(self, row) -> None:
        if row.status not in {RetryQueueStatus.PENDING.value, RetryQueueStatus.EXHAUSTED.value}:
            raise InvalidRetryQueueState("Retry not reviewable")
        row.workflow_status = "submitted"

    def start(self, row) -> None:
        row.status = RetryQueueStatus.PROCESSING.value

    def succeed(self, row) -> None:
        row.status = RetryQueueStatus.SUCCEEDED.value

    def exhaust(self, row) -> None:
        row.status = RetryQueueStatus.EXHAUSTED.value

    def cancel(self, row) -> None:
        row.status = RetryQueueStatus.CANCELLED.value
''',
    "DeadLetter": '''
class DeadLetterEngine:
    def reprocess(self, row) -> None:
        if row.status != DeadLetterStatus.OPEN.value:
            raise InvalidDeadLetterState("Only open dead letters can be reprocessed")
        row.status = DeadLetterStatus.REPROCESSED.value

    def discard(self, row) -> None:
        row.status = DeadLetterStatus.DISCARDED.value
''',
    "DataMapping": '''
class DataMappingEngine:
    def activate(self, row) -> None:
        row.status = DataMappingStatus.ACTIVE.value

    def deactivate(self, row) -> None:
        row.status = DataMappingStatus.INACTIVE.value
''',
    "DataTransformation": '''
class DataTransformationEngine:
    def activate(self, row) -> None:
        row.status = DataTransformationStatus.ACTIVE.value

    def deactivate(self, row) -> None:
        row.status = DataTransformationStatus.INACTIVE.value
''',
    "SyncJob": '''
class SyncJobEngine:
    def submit(self, row) -> None:
        if row.status != SyncJobStatus.DRAFT.value:
            raise InvalidSyncJobState("Only draft sync jobs can be submitted")
        row.status = SyncJobStatus.SUBMITTED.value

    def approve(self, row) -> None:
        if row.status != SyncJobStatus.SUBMITTED.value:
            raise InvalidSyncJobState("Only submitted sync jobs can be approved")
        row.status = SyncJobStatus.APPROVED.value

    def run(self, row) -> None:
        if row.status not in {SyncJobStatus.APPROVED.value, SyncJobStatus.QUEUED.value}:
            raise InvalidSyncJobState("Sync job must be approved or queued to run")
        row.status = SyncJobStatus.RUNNING.value

    def succeed(self, row) -> None:
        row.status = SyncJobStatus.SUCCEEDED.value

    def fail(self, row) -> None:
        row.status = SyncJobStatus.FAILED.value

    def cancel(self, row) -> None:
        row.status = SyncJobStatus.CANCELLED.value
''',
    "SyncLog": '''
class SyncLogEngine:
    def record(self, row) -> None:
        row.status = SyncLogStatus.RECORDED.value
''',
    "ApiUsage": '''
class ApiUsageEngine:
    def record(self, row) -> None:
        row.status = ApiUsageStatus.RECORDED.value
''',
    "RateLimit": '''
class RateLimitEngine:
    def activate(self, row) -> None:
        row.status = RateLimitStatus.ACTIVE.value

    def deactivate(self, row) -> None:
        row.status = RateLimitStatus.INACTIVE.value
''',
    "Notification": '''
class NotificationEngine:
    def archive(self, row) -> None:
        row.status = NotificationStatus.ARCHIVED.value

    def acknowledge(self, row) -> None:
        row.delivery_status = "read"
''',
    "Monitor": '''
class MonitorEngine:
    def mark_healthy(self, row) -> None:
        row.status = MonitorStatus.HEALTHY.value
        row.last_status = MonitorStatus.HEALTHY.value

    def mark_degraded(self, row) -> None:
        row.status = MonitorStatus.DEGRADED.value
        row.last_status = MonitorStatus.DEGRADED.value

    def mark_down(self, row) -> None:
        row.status = MonitorStatus.DOWN.value
        row.last_status = MonitorStatus.DOWN.value

    def deactivate(self, row) -> None:
        row.status = MonitorStatus.INACTIVE.value
''',
    "Report": '''
class ReportEngine:
    def finalize(self, row) -> None:
        row.status = ReportStatus.FINALIZED.value
''',
}


def gen_scaffold() -> None:
    w(INTEGRATION / "__init__.py", '"""Enterprise Integration Hub module — Sprint 21."""\n')
    w(INTEGRATION / "domain" / "__init__.py", '"""Integration domain layer."""\n')
    w(INTEGRATION / "adapters" / "__init__.py", '"""Integration cross-module adapters."""\n')
    w(INTEGRATION / "service" / "__init__.py", '"""Integration services — populated after generation."""\n')
    w(INTEGRATION / "service" / "engines" / "__init__.py", '"""Integration engines — populated after generation."""\n')
    w(INTEGRATION / "repository" / "__init__.py", '"""Integration repositories."""\n')
    w(INTEGRATION / "models" / "__init__.py", '"""Integration models — populated after generation."""\n')
    w(
        INTEGRATION / "models" / "mixins.py",
        '''"""Integration ORM mixin bundles per ERD_21."""

from database.mixins import (
    AuditMixin,
    CompanyMixin,
    SoftDeleteMixin,
    TenantMixin,
    VersionMixin,
)

IntRowMixin = (
    AuditMixin,
    TenantMixin,
    CompanyMixin,
    SoftDeleteMixin,
    VersionMixin,
)
''',
    )


def gen_domain() -> None:
    w(
        INTEGRATION / "domain" / "enums.py",
        '''"""Integration domain enums per ERD_21 section 8."""

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
''',
    )
    exc_lines = []
    for _, _, name, _ in TABLES:
        exc_lines.append(
            f'''
class Invalid{name}State(ConflictException):
    def __init__(self, message: str = "Invalid {name.lower()} state") -> None:
        super().__init__(message)
'''
        )
    w(
        INTEGRATION / "domain" / "exceptions.py",
        '"""Integration domain exceptions."""\n\nfrom core.exceptions import ConflictException\n'
        + "".join(exc_lines),
    )
    w(
        INTEGRATION / "domain" / "value_objects.py",
        '''"""Integration value objects."""

from dataclasses import dataclass


@dataclass(frozen=True)
class IntegrationCodes:
    document_number: str
''',
    )
    w(
        INTEGRATION / "domain" / "entities.py",
        '''"""Integration domain entity markers."""

from dataclasses import dataclass
from uuid import UUID


@dataclass
class ExternalSystemIdentity:
    system_id: UUID
    system_number: str
''',
    )


def gen_models() -> None:
    for key, body in MODELS.items():
        w(INTEGRATION / "models" / f"{key}.py", body)
    imports = "\n".join(
        f"from modules.integration.models.{k} import {CLASS_MAP[k]}" for k in CLASS_MAP
    )
    all_names = ",\n    ".join(f'"{CLASS_MAP[k]}"' for k in CLASS_MAP)
    w(
        INTEGRATION / "models" / "__init__.py",
        f'"""Integration ORM models."""\n\n{imports}\n\n__all__ = [\n    {all_names},\n]\n',
    )


def gen_migrations() -> None:
    w(
        ALEMBIC / "0377_create_integration_schema.py",
        '''"""Create integration schema."""

from collections.abc import Sequence

from alembic import op

revision: str = "0377_create_integration_schema"
down_revision: str | None = "0376_seed_analytics_workflows"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS integration")


def downgrade() -> None:
    op.execute("DROP SCHEMA IF EXISTS integration CASCADE")
''',
    )
    for rev, target, down in MIGRATIONS:
        if target == "schema" or (isinstance(target, str) and target.startswith("seed")):
            continue
        if isinstance(target, list):
            imports = "\n".join(
                f"from modules.integration.models.{m} import {CLASS_MAP[m]}  # noqa: F401"
                for m in target
            )
            creates = "\n    ".join(
                f"{CLASS_MAP[m]}.__table__.create(bind=op.get_bind(), checkfirst=True)"
                for m in target
            )
            drops = "\n    ".join(
                f"{CLASS_MAP[m]}.__table__.drop(bind=op.get_bind(), checkfirst=True)"
                for m in reversed(target)
            )
            w(
                ALEMBIC / f"{rev}.py",
                f'''"""Create int_retry_queue and int_dead_letter tables."""

import sys
from collections.abc import Sequence
from pathlib import Path

from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

{imports}

revision: str = "{rev}"
down_revision: str | None = "{down}"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    {creates}


def downgrade() -> None:
    {drops}
''',
            )
        else:
            cls = CLASS_MAP[target]
            w(
                ALEMBIC / f"{rev}.py",
                f'''"""Create {cls} table."""

import sys
from collections.abc import Sequence
from pathlib import Path

from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from modules.integration.models.{target} import {cls}  # noqa: F401

revision: str = "{rev}"
down_revision: str | None = "{down}"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    {cls}.__table__.create(bind=op.get_bind(), checkfirst=True)


def downgrade() -> None:
    {cls}.__table__.drop(bind=op.get_bind(), checkfirst=True)
''',
            )


def repo_template(module: str, cls: str, name: str, branch: bool) -> str:
    return f'''"""Integration {cls} repository."""

from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from modules.foundation.domain.value_objects import TenantContext
from modules.integration.models import {cls}
from modules.integration.repository.base import IntegrationScopedRepository, utcnow


class {name}Repository(IntegrationScopedRepository):
    def __init__(self, db: Session) -> None:
        super().__init__(db)

    def get(self, ctx: TenantContext, row_id: UUID) -> {cls} | None:
        stmt = select({cls}).where({cls}.id == row_id, {cls}.is_deleted.is_(False))
        stmt = self.apply_integration_filter(stmt, {cls}, ctx, branch_scoped={branch})
        return self.db.scalar(stmt)

    def list_rows(self, ctx: TenantContext, company_id: UUID):
        stmt = select({cls}).where(
            {cls}.company_id == company_id,
            {cls}.is_deleted.is_(False),
        )
        stmt = self.apply_integration_filter(stmt, {cls}, ctx, branch_scoped={branch})
        return list(self.db.scalars(stmt).all())

    def create(self, ctx: TenantContext, **fields) -> {cls}:
        row = {cls}(
            id=uuid4(),
            tenant_id=ctx.tenant_id,
            created_by=ctx.user_id,
            updated_by=ctx.user_id,
            **fields,
        )
        self.db.add(row)
        self.db.flush()
        return row

    def update(self, ctx: TenantContext, row_id: UUID, **fields) -> {cls} | None:
        row = self.get(ctx, row_id)
        if row is None:
            return None
        for k, v in fields.items():
            if v is not None:
                setattr(row, k, v)
        row.updated_at = utcnow()
        row.updated_by = ctx.user_id
        if hasattr(row, "version"):
            row.version = int(row.version or 1) + 1
        self.db.flush()
        return row
'''


def gen_repos() -> None:
    w(
        INTEGRATION / "repository" / "base.py",
        '''"""Integration scoped repository base."""

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import ForbiddenException
from modules.foundation.domain.value_objects import TenantContext
from modules.organization.repository.base import OrgScopedRepository


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class IntegrationScopedRepository(OrgScopedRepository):
    def __init__(self, db: Session) -> None:
        super().__init__(db)

    @staticmethod
    def apply_integration_filter(stmt, model, ctx: TenantContext, *, branch_scoped: bool = False):
        stmt = IntegrationScopedRepository.apply_tenant_filter(stmt, model, ctx)
        if ctx.company_id and ctx.user_type not in {"super_admin", "tenant_admin"}:
            stmt = stmt.where(model.company_id == ctx.company_id)
        if (
            branch_scoped
            and ctx.branch_id
            and ctx.user_type not in {"super_admin", "tenant_admin"}
            and hasattr(model, "branch_id")
        ):
            stmt = stmt.where(model.branch_id == ctx.branch_id)
        return stmt

    @staticmethod
    def resolve_company_id(ctx: TenantContext, company_id: UUID | None) -> UUID:
        if company_id is not None:
            IntegrationScopedRepository.ensure_company_access(ctx, company_id)
            return company_id
        if ctx.company_id is None:
            raise ForbiddenException("Company context required")
        return ctx.company_id
''',
    )
    w(
        INTEGRATION / "repository" / "code_sequence_repository.py",
        '''"""Integration code sequences."""

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from modules.integration.domain.enums import CODE_PREFIXES, IntegrationEntityType


class CodeSequenceRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def next_code(self, entity: IntegrationEntityType, company_id: UUID, model, code_column: str) -> str:
        prefix, width, include_year = CODE_PREFIXES[entity]
        year = datetime.now(timezone.utc).year
        full_prefix = f"{prefix}{year}-" if include_year else prefix
        stmt = select(getattr(model, code_column)).where(
            model.company_id == company_id,
            getattr(model, code_column).like(f"{full_prefix}%"),
            model.is_deleted.is_(False),
        )
        existing = list(self.db.scalars(stmt).all())
        seq = 1
        if existing:
            nums = []
            for code in existing:
                try:
                    nums.append(int(str(code).rsplit("-", 1)[-1]))
                except ValueError:
                    continue
            if nums:
                seq = max(nums) + 1
        return f"{full_prefix}{seq:0{width}d}"
''',
    )
    for module, cls, name, branch in TABLES:
        w(
            INTEGRATION / "repository" / f"{module}_repository.py",
            repo_template(module, cls, name, branch),
        )


def gen_engines() -> None:
    status_imports = {n: f"{n}Status" for n in ENGINE_NAMES}
    exc_imports = {
        "Connector": "InvalidConnectorState",
        "ApiCredential": "InvalidApiCredentialState",
        "Webhook": "InvalidWebhookState",
        "RetryQueue": "InvalidRetryQueueState",
        "DeadLetter": "InvalidDeadLetterState",
        "SyncJob": "InvalidSyncJobState",
    }
    for eng_name, body in ENGINE_BODIES.items():
        fname = ENGINE_FILE_MAP[eng_name]
        st = status_imports[eng_name]
        header = f'"""{eng_name} lifecycle engine."""\n\n'
        header += f"from modules.integration.domain.enums import (\n    {st},\n)\n"
        if eng_name in exc_imports:
            header += (
                f"from modules.integration.domain.exceptions import (\n"
                f"    {exc_imports[eng_name]},\n)\n"
            )
        header += "\n"
        w(INTEGRATION / "service" / "engines" / f"{fname}_engine.py", header + body.lstrip("\n"))
    lines = [
        f"from modules.integration.service.engines.{ENGINE_FILE_MAP[n]}_engine "
        f"import {n}Engine"
        for n in ENGINE_NAMES
    ]
    all_names = ",\n    ".join(f'"{n}Engine"' for n in ENGINE_NAMES)
    w(
        INTEGRATION / "service" / "engines" / "__init__.py",
        '"""Integration business engines."""\n\n'
        + "\n".join(lines)
        + f"\n\n__all__ = [\n    {all_names},\n]\n",
    )


def catalog_service(
    svc_name: str,
    cls: str,
    repo_name: str,
    entity: str,
    engine_name: str,
) -> str:
    return f'''"""{svc_name} application service."""

from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import NotFoundException
from modules.foundation.domain.value_objects import TenantContext
from modules.foundation.service.audit_service import AuditService
from modules.integration.models import {cls}
from modules.integration.repository.{entity}_repository import {repo_name}Repository
from modules.integration.service.engines import {engine_name}Engine
from modules.integration.service.integration_scope_validator import IntegrationScopeValidator


class {svc_name}:
    def __init__(self, db: Session) -> None:
        self._repo = {repo_name}Repository(db)
        self._scope = IntegrationScopeValidator(db)
        self._engine = {engine_name}Engine()
        self._audit = AuditService(db)

    def list(self, ctx: TenantContext, company_id: UUID | None = None):
        cid = self._scope.resolve_company_id(ctx, company_id)
        return self._repo.list_rows(ctx, cid)

    def get(self, ctx: TenantContext, row_id: UUID) -> {cls}:
        row = self._repo.get(ctx, row_id)
        if row is None:
            raise NotFoundException("{svc_name} not found")
        return row

    def create(self, ctx: TenantContext, company_id: UUID | None = None, **fields):
        cid = self._scope.resolve_company_id(ctx, company_id)
        row = self._repo.create(ctx, company_id=cid, **fields)
        self._audit.log_entity_change(
            tenant_id=ctx.tenant_id,
            entity_name="int_{entity}",
            entity_id=row.id,
            operation="create",
            performed_by=ctx.user_id,
        )
        return row

    def update(self, ctx: TenantContext, row_id: UUID, **fields):
        self.get(ctx, row_id)
        row = self._repo.update(ctx, row_id, **fields)
        if row is None:
            raise NotFoundException("{svc_name} not found")
        return row
'''


def numbered_service(
    svc_name: str,
    cls: str,
    repo_name: str,
    entity: str,
    entity_type: str,
    code_col: str,
    engine_name: str,
    actions: list[str],
) -> str:
    action_methods = ""
    for act in actions:
        action_methods += f'''
    def {act}(self, ctx: TenantContext, row_id: UUID):
        row = self.get(ctx, row_id)
        self._engine.{act}(row)
        return self._repo.update(ctx, row_id, status=row.status)
'''
    return f'''"""{svc_name}."""

from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import NotFoundException
from modules.foundation.domain.value_objects import TenantContext
from modules.foundation.service.audit_service import AuditService
from modules.integration.domain.enums import IntegrationEntityType
from modules.integration.models import {cls}
from modules.integration.repository.{entity}_repository import {repo_name}Repository
from modules.integration.service.engines import {engine_name}Engine
from modules.integration.service.integration_number_service import IntegrationNumberService
from modules.integration.service.integration_scope_validator import IntegrationScopeValidator


class {svc_name}:
    def __init__(self, db: Session) -> None:
        self._repo = {repo_name}Repository(db)
        self._scope = IntegrationScopeValidator(db)
        self._numbers = IntegrationNumberService(db)
        self._engine = {engine_name}Engine()
        self._audit = AuditService(db)

    def list(self, ctx: TenantContext, company_id: UUID | None = None):
        cid = self._scope.resolve_company_id(ctx, company_id)
        return self._repo.list_rows(ctx, cid)

    def get(self, ctx: TenantContext, row_id: UUID) -> {cls}:
        row = self._repo.get(ctx, row_id)
        if row is None:
            raise NotFoundException("{svc_name} not found")
        return row

    def create(self, ctx: TenantContext, company_id: UUID | None = None, **fields):
        cid = self._scope.resolve_company_id(ctx, company_id)
        doc = self._numbers.generate(IntegrationEntityType.{entity_type}, cid, {cls}, "{code_col}")
        return self._repo.create(ctx, company_id=cid, {code_col}=doc, **fields)

    def update(self, ctx: TenantContext, row_id: UUID, **fields):
        self.get(ctx, row_id)
        row = self._repo.update(ctx, row_id, **fields)
        if row is None:
            raise NotFoundException("{svc_name} not found")
        return row
{action_methods}
'''


def gen_services() -> None:
    w(
        INTEGRATION / "service" / "integration_scope_validator.py",
        '''"""Integration scope validator."""

from uuid import UUID

from sqlalchemy.orm import Session

from modules.foundation.domain.value_objects import TenantContext
from modules.integration.repository.base import IntegrationScopedRepository


class IntegrationScopeValidator(IntegrationScopedRepository):
    def __init__(self, db: Session) -> None:
        super().__init__(db)

    def validate_company_access(self, ctx: TenantContext, company_id: UUID) -> None:
        self.ensure_company_access(ctx, company_id)

    def validate_branch_access(self, ctx: TenantContext, branch_id: UUID) -> None:
        self.ensure_branch_access(ctx, branch_id)

    def resolve_company_id(self, ctx: TenantContext, company_id: UUID | None) -> UUID:
        return IntegrationScopedRepository.resolve_company_id(ctx, company_id)
''',
    )
    w(
        INTEGRATION / "service" / "integration_number_service.py",
        '''"""Integration numbering."""

from uuid import UUID

from sqlalchemy.orm import Session

from modules.integration.domain.enums import IntegrationEntityType
from modules.integration.repository.code_sequence_repository import CodeSequenceRepository


class IntegrationNumberService:
    def __init__(self, db: Session) -> None:
        self._seq = CodeSequenceRepository(db)

    def generate(self, entity: IntegrationEntityType, company_id: UUID, model, code_column: str) -> str:
        return self._seq.next_code(entity, company_id, model, code_column)
''',
    )

    simple_specs = [
        ("EventDefinitionService", "IntEventDefinition", "EventDefinition", "event_definition", "EventDefinition", "event_definition_service.py"),
        ("MessageQueueService", "IntMessageQueue", "MessageQueue", "message_queue", "MessageQueue", "message_queue_service.py"),
        ("DataMappingService", "IntDataMapping", "DataMapping", "data_mapping", "DataMapping", "data_mapping_service.py"),
        ("DataTransformationService", "IntDataTransformation", "DataTransformation", "data_transformation", "DataTransformation", "data_transformation_service.py"),
        ("SyncLogService", "IntSyncLog", "SyncLog", "sync_log", "SyncLog", "sync_log_service.py"),
        ("ApiUsageService", "IntApiUsage", "ApiUsage", "api_usage", "ApiUsage", "api_usage_service.py"),
        ("RateLimitService", "IntRateLimit", "RateLimit", "rate_limit", "RateLimit", "rate_limit_service.py"),
        ("NotificationService", "IntNotification", "Notification", "notification", "Notification", "notification_service.py"),
        ("MonitorService", "IntMonitor", "Monitor", "monitor", "Monitor", "monitor_service.py"),
        ("ReportService", "IntReport", "Report", "report", "Report", "report_service.py"),
    ]
    for svc, cls, repo, entity, eng, fname in simple_specs:
        body = catalog_service(svc, cls, repo, entity, eng)
        if svc == "NotificationService":
            body = body.rstrip() + '''

    def acknowledge(self, ctx: TenantContext, row_id: UUID):
        row = self.get(ctx, row_id)
        self._engine.acknowledge(row)
        return self._repo.update(ctx, row_id, delivery_status=row.delivery_status)
'''
        w(INTEGRATION / "service" / fname, body)

    numbered = [
        ("ExternalSystemService", "IntExternalSystem", "ExternalSystem", "external_system", "EXTERNAL_SYSTEM", "system_number", "ExternalSystem", [], "external_system_service.py"),
        ("ConnectorService", "IntConnector", "Connector", "connector", "CONNECTOR", "connector_number", "Connector", ["submit", "approve"], "connector_service.py"),
        ("ApiCredentialService", "IntApiCredential", "ApiCredential", "api_credential", "API_CREDENTIAL", "credential_number", "ApiCredential", ["submit", "approve"], "api_credential_service.py"),
        ("OauthClientService", "IntOauthClient", "OauthClient", "oauth_client", "OAUTH_CLIENT", "client_number", "OauthClient", [], "oauth_client_service.py"),
        ("WebhookService", "IntWebhook", "Webhook", "webhook", "WEBHOOK", "webhook_number", "Webhook", ["submit", "approve"], "webhook_service.py"),
        ("EventSubscriptionService", "IntEventSubscription", "EventSubscription", "event_subscription", "EVENT_SUBSCRIPTION", "subscription_number", "EventSubscription", [], "event_subscription_service.py"),
        ("MessageService", "IntMessage", "Message", "message", "MESSAGE", "message_number", "Message", [], "message_service.py"),
        ("RetryQueueService", "IntRetryQueue", "RetryQueue", "retry_queue", "RETRY_QUEUE", "retry_number", "RetryQueue", ["submit"], "retry_queue_service.py"),
        ("DeadLetterService", "IntDeadLetter", "DeadLetter", "dead_letter", "DEAD_LETTER", "dlq_number", "DeadLetter", ["reprocess"], "dead_letter_service.py"),
        ("SyncJobService", "IntSyncJob", "SyncJob", "sync_job", "SYNC_JOB", "sync_number", "SyncJob", ["submit", "approve", "run"], "sync_job_service.py"),
    ]
    for svc, cls, repo, entity, etype, col, eng, acts, fname in numbered:
        w(
            INTEGRATION / "service" / fname,
            numbered_service(svc, cls, repo, entity, etype, col, eng, acts),
        )

    w(
        INTEGRATION / "service" / "integration_service.py",
        '''"""Integration Hub peer port — C-01 masters + org; Finance event-ref ONLY.

NEVER uses PostingService. NEVER writes fin_* or peer operational tables.
Peers communicate via events / REST / webhooks / UUID only.
"""

from uuid import UUID

from sqlalchemy.orm import Session

from modules.foundation.domain.value_objects import TenantContext
from modules.integration.adapters.finance_event_port import IntegrationFinanceEventAdapter
from modules.integration.adapters.master_data_port import IntegrationMasterDataAdapter
from modules.integration.adapters.organization_port import IntegrationOrganizationAdapter


class IntegrationIntegrationService:
    def __init__(self, db: Session) -> None:
        self._master = IntegrationMasterDataAdapter(db)
        self._org = IntegrationOrganizationAdapter(db)
        self._finance = IntegrationFinanceEventAdapter(db)

    def get_employee(self, ctx: TenantContext, employee_id: UUID):
        return self._master.get_employee(ctx, employee_id)

    def get_customer(self, ctx: TenantContext, customer_id: UUID):
        return self._master.get_customer(ctx, customer_id)

    def get_product(self, ctx: TenantContext, product_id: UUID):
        return self._master.get_product(ctx, product_id)

    def get_vendor(self, ctx: TenantContext, vendor_id: UUID):
        return self._master.get_vendor(ctx, vendor_id)

    def get_department(self, ctx: TenantContext, department_id: UUID):
        return self._org.get_department(ctx, department_id)

    def finance_event_ref(self, ctx: TenantContext, finance_event_ref_id: UUID | None) -> UUID | None:
        return self._finance.resolve_event_ref(ctx, finance_event_ref_id)
''',
    )

    svc_imports = """from modules.integration.service.api_credential_service import ApiCredentialService
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
from modules.integration.service.webhook_service import WebhookService"""

    w(
        INTEGRATION / "service" / "application_service.py",
        f'''"""Integration application service facade."""

from sqlalchemy.orm import Session

{svc_imports}


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
''',
    )

    w(
        INTEGRATION / "service" / "__init__.py",
        f'''"""Integration services."""

from modules.integration.service.application_service import IntegrationApplicationService
{svc_imports}

__all__ = [
    "ApiCredentialService",
    "ApiUsageService",
    "ConnectorService",
    "DataMappingService",
    "DataTransformationService",
    "DeadLetterService",
    "EventDefinitionService",
    "EventSubscriptionService",
    "ExternalSystemService",
    "IntegrationApplicationService",
    "IntegrationIntegrationService",
    "MessageQueueService",
    "MessageService",
    "MonitorService",
    "NotificationService",
    "OauthClientService",
    "RateLimitService",
    "ReportService",
    "RetryQueueService",
    "SyncJobService",
    "SyncLogService",
    "WebhookService",
]
''',
    )


def gen_adapters() -> None:
    w(
        INTEGRATION / "adapters" / "master_data_port.py",
        '''"""Master Data port — employee / customer / product / vendor (C-01)."""

from uuid import UUID

from sqlalchemy.orm import Session

from modules.foundation.domain.value_objects import TenantContext
from modules.master_data.service.customer_service import CustomerService
from modules.master_data.service.employee_service import EmployeeService
from modules.master_data.service.product_service import ProductService
from modules.master_data.service.vendor_service import VendorService


class IntegrationMasterDataAdapter:
    def __init__(self, db: Session) -> None:
        self._customers = CustomerService(db)
        self._employees = EmployeeService(db)
        self._products = ProductService(db)
        self._vendors = VendorService(db)

    def get_customer(self, ctx: TenantContext, customer_id: UUID):
        return self._customers.get_customer(ctx, customer_id)

    def get_employee(self, ctx: TenantContext, employee_id: UUID):
        return self._employees.get_employee(ctx, employee_id)

    def get_product(self, ctx: TenantContext, product_id: UUID):
        return self._products.get_product(ctx, product_id)

    def get_vendor(self, ctx: TenantContext, vendor_id: UUID):
        return self._vendors.get_vendor(ctx, vendor_id)
''',
    )
    w(
        INTEGRATION / "adapters" / "organization_port.py",
        '''"""Organization port — read org_department only."""

from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import NotFoundException
from modules.foundation.domain.value_objects import TenantContext
from modules.organization.repository.hierarchy_repository import DepartmentRepository


class IntegrationOrganizationAdapter:
    def __init__(self, db: Session) -> None:
        self._departments = DepartmentRepository(db)

    def get_department(self, ctx: TenantContext, department_id: UUID):
        row = self._departments.get_by_id(ctx, department_id)
        if row is None:
            raise NotFoundException("Department not found")
        return row
''',
    )
    w(
        INTEGRATION / "adapters" / "finance_event_port.py",
        '''"""Finance event-ref port — Integration Hub NEVER posts.

NEVER uses PostingService. NEVER writes fin_* tables.
UUID / event-ref passthrough stubs only (Finance may publish events into Hub).
"""

from uuid import UUID

from sqlalchemy.orm import Session

from modules.foundation.domain.value_objects import TenantContext


class IntegrationFinanceEventAdapter:
    def __init__(self, db: Session) -> None:
        self._db = db

    def resolve_event_ref(self, ctx: TenantContext, finance_event_ref_id: UUID | None) -> UUID | None:
        """Read-only UUID passthrough for finance event references."""
        _ = (ctx, self._db)
        return finance_event_ref_id
''',
    )


def gen_permissions() -> None:
    w(
        INTEGRATION / "permissions.py",
        '''"""Integration permission constants per ERD_21 section 10."""

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
''',
    )


def gen_api() -> None:
    w(
        INTEGRATION / "dependencies.py",
        '''"""Integration module dependencies."""

from dataclasses import dataclass
from typing import Annotated

from fastapi import Query

from database.session import get_db
from modules.foundation.dependencies import get_tenant_context, require_permission
from modules.foundation.domain.value_objects import TenantContext

__all__ = [
    "PaginationParams",
    "get_pagination",
    "get_tenant_context",
    "require_permission",
    "TenantContext",
    "get_db",
    "paginate",
    "extract_update_fields",
]


@dataclass(frozen=True)
class PaginationParams:
    page: int
    page_size: int

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size


def get_pagination(
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=200)] = 25,
) -> PaginationParams:
    return PaginationParams(page=page, page_size=page_size)


def paginate(items: list, pagination: PaginationParams) -> list:
    return items[pagination.offset : pagination.offset + pagination.page_size]


def extract_update_fields(body) -> dict:
    fields = body.model_dump(exclude_unset=True)
    fields.pop("version", None)
    return fields
''',
    )

    schema_lines = [
        '"""Integration Pydantic schemas."""',
        "",
        "from uuid import UUID",
        "",
        "from pydantic import BaseModel, ConfigDict",
        "",
        "",
        "class OrmModel(BaseModel):",
        "    model_config = ConfigDict(from_attributes=True)",
        "",
    ]
    for _, name, _, _, _ in ROUTE_SPECS:
        schema_lines += [
            "",
            f"class {name}Create(BaseModel):",
            "    company_id: UUID | None = None",
            "    status: str | None = None",
            "",
            f"class {name}Update(BaseModel):",
            "    status: str | None = None",
            "    version: int | None = None",
            "",
            f"class {name}Response(OrmModel):",
            "    id: UUID",
            "    company_id: UUID",
            "    status: str",
            "    version: int",
        ]
    w(INTEGRATION / "schemas.py", "\n".join(schema_lines) + "\n")

    router_parts: list[str] = [
        '"""Integration API route handlers."""',
        "",
        "from typing import Annotated",
        "from uuid import UUID",
        "",
        "from fastapi import APIRouter, Depends",
        "from sqlalchemy.orm import Session",
        "",
        "from modules.integration.dependencies import (",
        "    PaginationParams,",
        "    extract_update_fields,",
        "    get_db,",
        "    get_pagination,",
        "    paginate,",
        "    require_permission,",
        ")",
        "from modules.integration.schemas import (",
    ]
    for _, name, _, _, _ in ROUTE_SPECS:
        router_parts.append(f"    {name}Create,")
        router_parts.append(f"    {name}Response,")
        router_parts.append(f"    {name}Update,")
    router_parts += [
        ")",
        "from modules.integration.service import (",
    ]
    seen_svc: set[str] = set()
    for _, _, svc, _, _ in ROUTE_SPECS:
        if svc not in seen_svc:
            router_parts.append(f"    {svc},")
            seen_svc.add(svc)
    router_parts.append(")")
    router_parts.append("from modules.foundation.domain.value_objects import TenantContext")
    router_parts.append("from shared.schemas import APIResponse")
    router_parts.append("")

    exports: list[str] = []
    route_actions: dict[str, list[tuple[str, str]]] = {
        "connectors": [
            ("submit", "integration.connector:submit"),
            ("approve", "integration.connector:approve"),
        ],
        "api-credentials": [
            ("submit", "integration.credential:submit"),
            ("approve", "integration.credential:approve"),
        ],
        "webhooks": [
            ("submit", "integration.webhook:submit"),
            ("approve", "integration.webhook:approve"),
        ],
        "retry-queues": [
            ("submit", "integration.retry:submit"),
        ],
        "dead-letters": [
            ("reprocess", "integration.dlq:reprocess"),
        ],
        "sync-jobs": [
            ("submit", "integration.sync:submit"),
            ("approve", "integration.sync:approve"),
            ("run", "integration.sync:run"),
        ],
        "notifications": [
            ("acknowledge", "integration.notification:acknowledge"),
        ],
    }

    for prefix, name, svc, perm, _branch in ROUTE_SPECS:
        rname = f"{prefix.replace('-', '_')}_router"
        exports.append(rname)
        router_parts.append(f'{rname} = APIRouter(prefix="/{prefix}", tags=["Integration — {name}"])')
        router_parts.append("")
        create_call = f"{svc}(db).create(ctx, **body.model_dump(exclude_none=True))"
        update_perm = f"{perm}:update"
        create_perm = f"{perm}:create"
        if perm in {"integration.usage"}:
            pass
        elif perm == "integration.notification":
            create_perm = "integration.notification:read"
            update_perm = "integration.notification:read"
        elif perm == "integration.monitor":
            create_perm = "integration.monitor:read"
            update_perm = "integration.monitor:acknowledge"
        elif perm == "integration.report":
            create_perm = "integration.report:read"
            update_perm = "integration.report:export"
        elif perm == "integration.retry":
            update_perm = "integration.retry:review"
            create_perm = "integration.retry:read"
        elif perm == "integration.dlq":
            update_perm = "integration.dlq:review"
            create_perm = "integration.dlq:read"
        elif perm == "integration.sync" and prefix == "sync-logs":
            create_perm = "integration.sync:read"
            update_perm = "integration.sync:read"
        elif perm == "integration.message":
            update_perm = "integration.message:requeue"

        fn = prefix.replace("-", "_")
        router_parts += [
            f'@{rname}.get("", response_model=APIResponse[list[{name}Response]])',
            f"def list_{fn}(",
            f'    ctx: Annotated[TenantContext, Depends(require_permission("{perm}:read"))],',
            "    db: Annotated[Session, Depends(get_db)],",
            "    pagination: Annotated[PaginationParams, Depends(get_pagination)],",
            "    company_id: UUID | None = None,",
            "):",
            f"    items = {svc}(db).list(ctx, company_id=company_id)",
            '    return APIResponse(message="OK", data=paginate(items, pagination))',
            "",
            f'@{rname}.get("/{{row_id}}", response_model=APIResponse[{name}Response])',
            f"def get_{fn}(",
            "    row_id: UUID,",
            f'    ctx: Annotated[TenantContext, Depends(require_permission("{perm}:read"))],',
            "    db: Annotated[Session, Depends(get_db)],",
            "):",
            f'    return APIResponse(message="OK", data={svc}(db).get(ctx, row_id))',
            "",
            f'@{rname}.post("", response_model=APIResponse[{name}Response])',
            f"def create_{fn}(",
            f"    body: {name}Create,",
            f'    ctx: Annotated[TenantContext, Depends(require_permission("{create_perm}"))],',
            "    db: Annotated[Session, Depends(get_db)],",
            "):",
            f'    return APIResponse(message="Created", data={create_call})',
            "",
            f'@{rname}.patch("/{{row_id}}", response_model=APIResponse[{name}Response])',
            f"def update_{fn}(",
            "    row_id: UUID,",
            f"    body: {name}Update,",
            f'    ctx: Annotated[TenantContext, Depends(require_permission("{update_perm}"))],',
            "    db: Annotated[Session, Depends(get_db)],",
            "):",
            (
                f'    return APIResponse(message="Updated", '
                f"data={svc}(db).update(ctx, row_id, **extract_update_fields(body)))"
            ),
            "",
        ]

        for act, pcode in route_actions.get(prefix, []):
            router_parts += [
                f'@{rname}.post("/{{row_id}}/{act}", response_model=APIResponse[{name}Response])',
                f"def {act}_{fn}(",
                "    row_id: UUID,",
                f'    ctx: Annotated[TenantContext, Depends(require_permission("{pcode}"))],',
                "    db: Annotated[Session, Depends(get_db)],",
                "):",
                f'    return APIResponse(message="{act}", data={svc}(db).{act}(ctx, row_id))',
                "",
            ]

    w(INTEGRATION / "routers" / "__init__.py", "\n".join(router_parts) + "\n")

    import_list = ",\n    ".join(exports)
    include_lines = "\n".join(f"integration_router.include_router({e})" for e in exports)
    w(
        INTEGRATION / "router.py",
        f'''"""Integration module router aggregation."""

from fastapi import APIRouter

from modules.integration.routers import (
    {import_list},
)

integration_router = APIRouter(prefix="/integration")
{include_lines}
''',
    )


def gen_tasks_tests() -> None:
    w(
        INTEGRATION / "tasks.py",
        '''"""Integration Celery task stubs per ERD_21 section 11."""

from workers.celery_app import celery_app


@celery_app.task(name="integration.retry_processor")
def retry_processor() -> dict:
    from sqlalchemy import select

    from database.session import SessionLocal
    from modules.integration.models import IntRetryQueue

    db = SessionLocal()
    try:
        rows = list(
            db.scalars(
                select(IntRetryQueue).where(
                    IntRetryQueue.is_deleted.is_(False),
                    IntRetryQueue.status.in_(["pending", "processing"]),
                )
            ).all()
        )
        return {"status": "ok", "retries_due": len(rows)}
    finally:
        db.close()


@celery_app.task(name="integration.dead_letter_reprocessor")
def dead_letter_reprocessor() -> dict:
    from sqlalchemy import select

    from database.session import SessionLocal
    from modules.integration.models import IntDeadLetter

    db = SessionLocal()
    try:
        rows = list(
            db.scalars(
                select(IntDeadLetter).where(
                    IntDeadLetter.is_deleted.is_(False),
                    IntDeadLetter.status == "open",
                )
            ).all()
        )
        return {"status": "ok", "dlq_open": len(rows)}
    finally:
        db.close()


@celery_app.task(name="integration.webhook_dispatcher")
def webhook_dispatcher() -> dict:
    from sqlalchemy import select

    from database.session import SessionLocal
    from modules.integration.models import IntWebhook

    db = SessionLocal()
    try:
        rows = list(
            db.scalars(
                select(IntWebhook).where(
                    IntWebhook.is_deleted.is_(False),
                    IntWebhook.is_enabled.is_(True),
                    IntWebhook.status == "active",
                )
            ).all()
        )
        return {"status": "ok", "webhooks": len(rows)}
    finally:
        db.close()


@celery_app.task(name="integration.sync_scheduler")
def sync_scheduler() -> dict:
    from sqlalchemy import select

    from database.session import SessionLocal
    from modules.integration.models import IntSyncJob

    db = SessionLocal()
    try:
        rows = list(
            db.scalars(
                select(IntSyncJob).where(
                    IntSyncJob.is_deleted.is_(False),
                    IntSyncJob.status.in_(["approved", "queued"]),
                )
            ).all()
        )
        return {"status": "ok", "syncs_due": len(rows)}
    finally:
        db.close()


@celery_app.task(name="integration.rate_limit_enforcer")
def rate_limit_enforcer() -> dict:
    from sqlalchemy import select

    from database.session import SessionLocal
    from modules.integration.models import IntRateLimit

    db = SessionLocal()
    try:
        rows = list(
            db.scalars(
                select(IntRateLimit).where(
                    IntRateLimit.is_deleted.is_(False),
                    IntRateLimit.status == "active",
                )
            ).all()
        )
        return {"status": "ok", "limits": len(rows)}
    finally:
        db.close()


@celery_app.task(name="integration.message_queue_poller")
def message_queue_poller() -> dict:
    from sqlalchemy import select

    from database.session import SessionLocal
    from modules.integration.models import IntMessage

    db = SessionLocal()
    try:
        rows = list(
            db.scalars(
                select(IntMessage).where(
                    IntMessage.is_deleted.is_(False),
                    IntMessage.status == "queued",
                )
            ).all()
        )
        return {"status": "ok", "queued": len(rows)}
    finally:
        db.close()
''',
    )

    w(
        TESTS / "unit" / "integration" / "test_int_hub_engines.py",
        '''"""Unit tests for Integration Hub engines."""

from types import SimpleNamespace

from modules.integration.service.engines import (
    ConnectorEngine,
    DeadLetterEngine,
    SyncJobEngine,
    WebhookEngine,
)


def test_connector_lifecycle():
    row = SimpleNamespace(status="draft")
    eng = ConnectorEngine()
    eng.submit(row)
    assert row.status == "submitted"
    eng.approve(row)
    assert row.status == "approved"


def test_webhook_lifecycle():
    row = SimpleNamespace(status="draft", is_enabled=False)
    eng = WebhookEngine()
    eng.submit(row)
    eng.approve(row)
    eng.activate(row)
    assert row.status == "active"
    assert row.is_enabled is True


def test_sync_job_lifecycle_and_run():
    row = SimpleNamespace(status="draft")
    eng = SyncJobEngine()
    eng.submit(row)
    eng.approve(row)
    eng.run(row)
    assert row.status == "running"


def test_dead_letter_reprocess():
    row = SimpleNamespace(status="open")
    eng = DeadLetterEngine()
    eng.reprocess(row)
    assert row.status == "reprocessed"
''',
    )
    w(
        TESTS / "unit" / "integration" / "test_int_hub_tasks.py",
        '''"""Unit tests for Integration Hub Celery task names."""

from modules.integration import tasks


def test_integration_task_names_registered():
    assert tasks.retry_processor.name == "integration.retry_processor"
    assert tasks.dead_letter_reprocessor.name == "integration.dead_letter_reprocessor"
    assert tasks.webhook_dispatcher.name == "integration.webhook_dispatcher"
    assert tasks.sync_scheduler.name == "integration.sync_scheduler"
    assert tasks.rate_limit_enforcer.name == "integration.rate_limit_enforcer"
    assert tasks.message_queue_poller.name == "integration.message_queue_poller"
''',
    )
    w(
        TESTS / "security" / "integration" / "test_int_hub_permissions.py",
        '''"""Security tests for Integration Hub permissions."""

from modules.integration.permissions import (
    API_MANAGER_PERMISSIONS,
    INTEGRATION_ADMIN_PERMISSIONS,
    INTEGRATION_ENGINEER_PERMISSIONS,
    INTEGRATION_PERMISSIONS,
    SYSTEM_OPERATOR_PERMISSIONS,
)


def test_integration_permissions_defined():
    codes = [p[0] for p in INTEGRATION_PERMISSIONS]
    assert "integration.connector:approve" in codes
    assert "integration.sync:run" in codes
    assert "integration.dlq:reprocess" in codes


def test_integration_roles():
    assert len(INTEGRATION_ADMIN_PERMISSIONS) == len(INTEGRATION_PERMISSIONS)
    assert any("connector" in p for p in INTEGRATION_ENGINEER_PERMISSIONS)
    assert any("credential" in p for p in API_MANAGER_PERMISSIONS)
    assert any("dlq" in p for p in SYSTEM_OPERATOR_PERMISSIONS)
''',
    )
    w(
        TESTS / "integration" / "integration" / "test_int_hub_module_import.py",
        '''"""Integration Hub module import smoke tests."""

from modules.integration.models import IntConnector, IntExternalSystem, IntSyncJob
from modules.integration.router import integration_router
from modules.integration.service import (
    ConnectorService,
    ExternalSystemService,
    IntegrationIntegrationService,
    SyncJobService,
)
from modules.integration.service.engines import ConnectorEngine, ExternalSystemEngine, SyncJobEngine


def test_integration_models_importable():
    assert IntExternalSystem is not None
    assert IntConnector is not None
    assert IntSyncJob is not None


def test_integration_router_mounted():
    assert integration_router.prefix == "/integration"
    assert len(integration_router.routes) > 0


def test_integration_services_and_engines_importable():
    assert ExternalSystemService is not None
    assert ConnectorService is not None
    assert SyncJobService is not None
    assert IntegrationIntegrationService is not None
    assert ExternalSystemEngine is not None
    assert ConnectorEngine is not None
    assert SyncJobEngine is not None
''',
    )


def gen_seeds() -> None:
    w(
        ALEMBIC / "0397_seed_int_permissions.py",
        '''"""Seed Integration Hub permissions and roles."""

import sys
from collections.abc import Sequence
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import sqlalchemy as sa
from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from modules.integration.permissions import (
    API_MANAGER_PERMISSIONS,
    INTEGRATION_ADMIN_PERMISSIONS,
    INTEGRATION_ENGINEER_PERMISSIONS,
    INTEGRATION_PERMISSIONS,
    SYSTEM_OPERATOR_PERMISSIONS,
)

revision: str = "0397_seed_int_permissions"
down_revision: str | None = "0396_int_report"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

PERMISSION_TABLE = sa.table(
    "sec_permission",
    sa.column("id", sa.Uuid),
    sa.column("permission_code", sa.String),
    sa.column("resource", sa.String),
    sa.column("action", sa.String),
    sa.column("module", sa.String),
    sa.column("is_active", sa.Boolean),
    sa.column("created_at", sa.DateTime(timezone=True)),
    schema="foundation",
)

ROLE_SPECS: list[tuple[str, str, list[str]]] = [
    ("INTEGRATION_ADMIN", "Integration Admin", INTEGRATION_ADMIN_PERMISSIONS),
    ("INTEGRATION_ENGINEER", "Integration Engineer", INTEGRATION_ENGINEER_PERMISSIONS),
    ("API_MANAGER", "API Manager", API_MANAGER_PERMISSIONS),
    ("SYSTEM_OPERATOR", "System Operator", SYSTEM_OPERATOR_PERMISSIONS),
]


def _ensure_permission(conn, now, code, resource, action, module):
    exists = conn.execute(
        sa.text("SELECT id FROM foundation.sec_permission WHERE permission_code = :code"),
        {"code": code},
    ).first()
    if exists:
        return str(exists[0])
    perm_id = str(uuid4())
    conn.execute(
        sa.insert(PERMISSION_TABLE).values(
            id=perm_id,
            permission_code=code,
            resource=resource,
            action=action,
            module=module,
            is_active=True,
            created_at=now,
        )
    )
    return perm_id


def _ensure_role(conn, now, tenant_id, role_code, role_name):
    exists = conn.execute(
        sa.text(
            """
            SELECT id FROM foundation.sec_role
            WHERE tenant_id = :tid AND role_code = :code AND is_deleted = false
            """
        ),
        {"tid": tenant_id, "code": role_code},
    ).first()
    if exists:
        return str(exists[0])
    role_id = str(uuid4())
    conn.execute(
        sa.text(
            """
            INSERT INTO foundation.sec_role
            (id, tenant_id, role_code, role_name, is_system_role, status,
             created_at, updated_at, is_deleted, version)
            VALUES (:id, :tid, :code, :name, true, 'active', :now, :now, false, 1)
            """
        ),
        {"id": role_id, "tid": tenant_id, "code": role_code, "name": role_name, "now": now},
    )
    return role_id


def _grant(conn, now, tenant_id, role_id, perm_id):
    exists = conn.execute(
        sa.text(
            """
            SELECT 1 FROM foundation.sec_role_permission
            WHERE role_id = :rid AND permission_id = :pid
            """
        ),
        {"rid": role_id, "pid": perm_id},
    ).first()
    if exists:
        return
    conn.execute(
        sa.text(
            """
            INSERT INTO foundation.sec_role_permission
            (id, tenant_id, role_id, permission_id, granted_at)
            VALUES (:id, :tid, :rid, :pid, :now)
            """
        ),
        {"id": str(uuid4()), "tid": tenant_id, "rid": role_id, "pid": perm_id, "now": now},
    )


def upgrade() -> None:
    conn = op.get_bind()
    now = datetime.now(timezone.utc)
    perm_ids: dict[str, str] = {}
    for code, resource, action, module in INTEGRATION_PERMISSIONS:
        perm_ids[code] = _ensure_permission(conn, now, code, resource, action, module)
    tenants = conn.execute(
        sa.text("SELECT id FROM foundation.sec_tenant WHERE is_deleted = false")
    ).fetchall()
    for (tenant_id,) in tenants:
        tid = str(tenant_id)
        for role_code, role_name, perms in ROLE_SPECS:
            role_id = _ensure_role(conn, now, tid, role_code, role_name)
            for perm_code in perms:
                _grant(conn, now, tid, role_id, perm_ids[perm_code])


def downgrade() -> None:
    conn = op.get_bind()
    for role_code, _, _ in reversed(ROLE_SPECS):
        conn.execute(
            sa.text(
                "DELETE FROM foundation.sec_role WHERE role_code = :code AND is_system_role = true"
            ),
            {"code": role_code},
        )
    for code, _, _, _ in INTEGRATION_PERMISSIONS:
        conn.execute(
            sa.text("DELETE FROM foundation.sec_permission WHERE permission_code = :code"),
            {"code": code},
        )
''',
    )

    w(
        ALEMBIC / "0398_seed_integration_workflows.py",
        '''"""Seed Integration Hub workflow definitions per ERD_21."""

from collections.abc import Sequence
from datetime import datetime, timezone
from uuid import uuid4

import sqlalchemy as sa
from alembic import op

revision: str = "0398_seed_integration_workflows"
down_revision: str | None = "0397_seed_int_permissions"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

WORKFLOWS: list[tuple[str, str, str, list[tuple[int, str, str, str]]]] = [
    (
        "INT_CONNECTOR_APPROVAL",
        "Integration Connector Approval",
        "int_connector",
        [
            (1, "INTEGRATION_ENGINEER", "Engineer Submit", "role"),
            (2, "API_MANAGER", "API Manager Approval", "role"),
            (3, "INTEGRATION_ADMIN", "Integration Admin Approval", "role"),
        ],
    ),
    (
        "INT_WEBHOOK_APPROVAL",
        "Integration Webhook Approval",
        "int_webhook",
        [
            (1, "INTEGRATION_ENGINEER", "Engineer Submit", "role"),
            (2, "API_MANAGER", "API Manager Approval", "role"),
            (3, "INTEGRATION_ADMIN", "Integration Admin Approval", "role"),
        ],
    ),
    (
        "INT_API_CREDENTIAL_APPROVAL",
        "Integration API Credential Approval",
        "int_api_credential",
        [
            (1, "INTEGRATION_ENGINEER", "Engineer Submit", "role"),
            (2, "API_MANAGER", "API Manager Approval", "role"),
            (3, "INTEGRATION_ADMIN", "Integration Admin Approval", "role"),
        ],
    ),
    (
        "INT_SYNC_APPROVAL",
        "Integration Sync Approval",
        "int_sync_job",
        [
            (1, "INTEGRATION_ENGINEER", "Engineer Submit", "role"),
            (2, "SYSTEM_OPERATOR", "System Operator Approval", "role"),
            (3, "INTEGRATION_ADMIN", "Integration Admin Approval", "role"),
        ],
    ),
    (
        "INT_RETRY_REVIEW",
        "Integration Retry Review",
        "int_retry_queue",
        [
            (1, "SYSTEM_OPERATOR", "Operator Review", "role"),
            (2, "INTEGRATION_ADMIN", "Integration Admin Approval", "role"),
        ],
    ),
]


def upgrade() -> None:
    conn = op.get_bind()
    now = datetime.now(timezone.utc)
    tenants = conn.execute(
        sa.text("SELECT id FROM foundation.sec_tenant WHERE is_deleted = false")
    ).fetchall()
    for (tenant_id,) in tenants:
        tid = str(tenant_id)
        for workflow_code, workflow_name, document_type, steps in WORKFLOWS:
            exists = conn.execute(
                sa.text(
                    """
                    SELECT id FROM foundation.wf_definition
                    WHERE tenant_id = :tid AND workflow_code = :code AND version_no = 1
                    """
                ),
                {"tid": tid, "code": workflow_code},
            ).first()
            if exists:
                wf_id = str(exists[0])
            else:
                wf_id = str(uuid4())
                conn.execute(
                    sa.text(
                        """
                        INSERT INTO foundation.wf_definition
                        (id, tenant_id, workflow_code, workflow_name, module,
                         document_type, version_no, is_active, created_at, updated_at)
                        VALUES (:id, :tid, :code, :name, 'integration', :doc, 1, true, :now, :now)
                        """
                    ),
                    {
                        "id": wf_id,
                        "tid": tid,
                        "code": workflow_code,
                        "name": workflow_name,
                        "doc": document_type,
                        "now": now,
                    },
                )
            for step_order, step_code, step_name, approver_type in steps:
                step_exists = conn.execute(
                    sa.text(
                        """
                        SELECT 1 FROM foundation.wf_step
                        WHERE workflow_id = :wid AND step_order = :ord
                        """
                    ),
                    {"wid": wf_id, "ord": step_order},
                ).first()
                if step_exists:
                    continue
                conn.execute(
                    sa.text(
                        """
                        INSERT INTO foundation.wf_step
                        (id, tenant_id, workflow_id, step_order, step_code, step_name,
                         approver_type, is_parallel, created_at, updated_at)
                        VALUES (:id, :tid, :wid, :ord, :code, :name, :atype, false, :now, :now)
                        """
                    ),
                    {
                        "id": str(uuid4()),
                        "tid": tid,
                        "wid": wf_id,
                        "ord": step_order,
                        "code": step_code,
                        "name": step_name,
                        "atype": approver_type,
                        "now": now,
                    },
                )


def downgrade() -> None:
    conn = op.get_bind()
    for workflow_code, _, _, _ in WORKFLOWS:
        conn.execute(
            sa.text(
                """
                DELETE FROM foundation.wf_step
                WHERE workflow_id IN (
                    SELECT id FROM foundation.wf_definition WHERE workflow_code = :code
                )
                """
            ),
            {"code": workflow_code},
        )
        conn.execute(
            sa.text("DELETE FROM foundation.wf_definition WHERE workflow_code = :code"),
            {"code": workflow_code},
        )
''',
    )


def gen_wiring() -> None:
    patch_file(
        SHARED / "router.py",
        "from modules.analytics.router import analytics_router\n",
        "from modules.analytics.router import analytics_router\n"
        "from modules.integration.router import integration_router\n",
    )
    patch_file(
        SHARED / "router.py",
        "api_v1_router.include_router(analytics_router)\n",
        "api_v1_router.include_router(analytics_router)\n"
        "api_v1_router.include_router(integration_router)\n",
    )
    patch_file(
        ROOT / "alembic" / "env.py",
        "import modules.analytics.models  # noqa: F401 — register ORM metadata\n",
        "import modules.analytics.models  # noqa: F401 — register ORM metadata\n"
        "import modules.integration.models  # noqa: F401 — register ORM metadata\n",
    )
    patch_file(
        ROOT / "src" / "workers" / "celery_app.py",
        '        "modules.analytics",\n',
        '        "modules.analytics",\n        "modules.integration",\n',
    )
    patch_file(
        ROOT / "pyproject.toml",
        '    "modules.analytics.*",\n',
        '    "modules.analytics.*",\n    "modules.integration.*",\n',
    )
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    ruff_marker = (
        '"src/modules/analytics/**" = ["E501", "SIM102"]\n'
        '"src/modules/analytics/domain/enums.py" = ["UP042"]\n'
    )
    ruff_new = (
        ruff_marker
        + '"src/modules/integration/**" = ["E501", "SIM102"]\n'
        + '"src/modules/integration/domain/enums.py" = ["UP042"]\n'
    )
    if ruff_marker in pyproject and '"src/modules/integration/**"' not in pyproject:
        patch_file(ROOT / "pyproject.toml", ruff_marker, ruff_new)
    elif '"src/modules/integration/**"' not in pyproject:
        alt = '"src/modules/analytics/domain/enums.py" = ["UP042"]\n'
        if alt in pyproject:
            patch_file(
                ROOT / "pyproject.toml",
                alt,
                alt
                + '"src/modules/integration/**" = ["E501", "SIM102"]\n'
                + '"src/modules/integration/domain/enums.py" = ["UP042"]\n',
            )


def main() -> None:
    gen_scaffold()
    gen_domain()
    gen_models()
    gen_migrations()
    gen_repos()
    gen_engines()
    gen_services()
    gen_adapters()
    gen_permissions()
    gen_api()
    gen_tasks_tests()
    gen_seeds()
    gen_wiring()
    print(f"OK integration module generated — {len(FILES_WRITTEN)} files")
    print("Alembic head revision: 0398_seed_integration_workflows")


if __name__ == "__main__":
    main()
