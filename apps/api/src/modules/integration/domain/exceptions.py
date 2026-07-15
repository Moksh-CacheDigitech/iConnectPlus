"""Integration domain exceptions."""

from core.exceptions import ConflictException


class InvalidExternalSystemState(ConflictException):
    def __init__(self, message: str = "Invalid externalsystem state") -> None:
        super().__init__(message)

class InvalidConnectorState(ConflictException):
    def __init__(self, message: str = "Invalid connector state") -> None:
        super().__init__(message)

class InvalidApiCredentialState(ConflictException):
    def __init__(self, message: str = "Invalid apicredential state") -> None:
        super().__init__(message)

class InvalidOauthClientState(ConflictException):
    def __init__(self, message: str = "Invalid oauthclient state") -> None:
        super().__init__(message)

class InvalidWebhookState(ConflictException):
    def __init__(self, message: str = "Invalid webhook state") -> None:
        super().__init__(message)

class InvalidEventDefinitionState(ConflictException):
    def __init__(self, message: str = "Invalid eventdefinition state") -> None:
        super().__init__(message)

class InvalidEventSubscriptionState(ConflictException):
    def __init__(self, message: str = "Invalid eventsubscription state") -> None:
        super().__init__(message)

class InvalidMessageQueueState(ConflictException):
    def __init__(self, message: str = "Invalid messagequeue state") -> None:
        super().__init__(message)

class InvalidMessageState(ConflictException):
    def __init__(self, message: str = "Invalid message state") -> None:
        super().__init__(message)

class InvalidRetryQueueState(ConflictException):
    def __init__(self, message: str = "Invalid retryqueue state") -> None:
        super().__init__(message)

class InvalidDeadLetterState(ConflictException):
    def __init__(self, message: str = "Invalid deadletter state") -> None:
        super().__init__(message)

class InvalidDataMappingState(ConflictException):
    def __init__(self, message: str = "Invalid datamapping state") -> None:
        super().__init__(message)

class InvalidDataTransformationState(ConflictException):
    def __init__(self, message: str = "Invalid datatransformation state") -> None:
        super().__init__(message)

class InvalidSyncJobState(ConflictException):
    def __init__(self, message: str = "Invalid syncjob state") -> None:
        super().__init__(message)

class InvalidSyncLogState(ConflictException):
    def __init__(self, message: str = "Invalid synclog state") -> None:
        super().__init__(message)

class InvalidApiUsageState(ConflictException):
    def __init__(self, message: str = "Invalid apiusage state") -> None:
        super().__init__(message)

class InvalidRateLimitState(ConflictException):
    def __init__(self, message: str = "Invalid ratelimit state") -> None:
        super().__init__(message)

class InvalidNotificationState(ConflictException):
    def __init__(self, message: str = "Invalid notification state") -> None:
        super().__init__(message)

class InvalidMonitorState(ConflictException):
    def __init__(self, message: str = "Invalid monitor state") -> None:
        super().__init__(message)

class InvalidReportState(ConflictException):
    def __init__(self, message: str = "Invalid report state") -> None:
        super().__init__(message)
