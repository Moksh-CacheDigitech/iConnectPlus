"""Integration Pydantic schemas."""

from uuid import UUID

from pydantic import BaseModel, ConfigDict


class OrmModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class ExternalSystemCreate(BaseModel):
    company_id: UUID | None = None
    status: str | None = None

class ExternalSystemUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class ExternalSystemResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class ConnectorCreate(BaseModel):
    company_id: UUID | None = None
    status: str | None = None

class ConnectorUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class ConnectorResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class ApiCredentialCreate(BaseModel):
    company_id: UUID | None = None
    status: str | None = None

class ApiCredentialUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class ApiCredentialResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class OauthClientCreate(BaseModel):
    company_id: UUID | None = None
    status: str | None = None

class OauthClientUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class OauthClientResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class WebhookCreate(BaseModel):
    company_id: UUID | None = None
    status: str | None = None

class WebhookUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class WebhookResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class EventDefinitionCreate(BaseModel):
    company_id: UUID | None = None
    status: str | None = None

class EventDefinitionUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class EventDefinitionResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class EventSubscriptionCreate(BaseModel):
    company_id: UUID | None = None
    status: str | None = None

class EventSubscriptionUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class EventSubscriptionResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class MessageQueueCreate(BaseModel):
    company_id: UUID | None = None
    status: str | None = None

class MessageQueueUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class MessageQueueResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class MessageCreate(BaseModel):
    company_id: UUID | None = None
    status: str | None = None

class MessageUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class MessageResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class RetryQueueCreate(BaseModel):
    company_id: UUID | None = None
    status: str | None = None

class RetryQueueUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class RetryQueueResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class DeadLetterCreate(BaseModel):
    company_id: UUID | None = None
    status: str | None = None

class DeadLetterUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class DeadLetterResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class DataMappingCreate(BaseModel):
    company_id: UUID | None = None
    status: str | None = None

class DataMappingUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class DataMappingResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class DataTransformationCreate(BaseModel):
    company_id: UUID | None = None
    status: str | None = None

class DataTransformationUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class DataTransformationResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class SyncJobCreate(BaseModel):
    company_id: UUID | None = None
    status: str | None = None

class SyncJobUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class SyncJobResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class SyncLogCreate(BaseModel):
    company_id: UUID | None = None
    status: str | None = None

class SyncLogUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class SyncLogResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class ApiUsageCreate(BaseModel):
    company_id: UUID | None = None
    status: str | None = None

class ApiUsageUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class ApiUsageResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class RateLimitCreate(BaseModel):
    company_id: UUID | None = None
    status: str | None = None

class RateLimitUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class RateLimitResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class NotificationCreate(BaseModel):
    company_id: UUID | None = None
    status: str | None = None

class NotificationUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class NotificationResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class MonitorCreate(BaseModel):
    company_id: UUID | None = None
    status: str | None = None

class MonitorUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class MonitorResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class ReportCreate(BaseModel):
    company_id: UUID | None = None
    status: str | None = None

class ReportUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class ReportResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int
