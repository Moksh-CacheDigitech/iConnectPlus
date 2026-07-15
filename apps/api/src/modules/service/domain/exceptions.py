"""Service domain exceptions."""

from core.exceptions import ConflictException


class InvalidServiceCategoryState(ConflictException):
    def __init__(self, message: str = "Invalid servicecategory state") -> None:
        super().__init__(message)

class InvalidServiceRequestState(ConflictException):
    def __init__(self, message: str = "Invalid servicerequest state") -> None:
        super().__init__(message)

class InvalidServiceTicketState(ConflictException):
    def __init__(self, message: str = "Invalid serviceticket state") -> None:
        super().__init__(message)

class InvalidServiceAssignmentState(ConflictException):
    def __init__(self, message: str = "Invalid serviceassignment state") -> None:
        super().__init__(message)

class InvalidServiceScheduleState(ConflictException):
    def __init__(self, message: str = "Invalid serviceschedule state") -> None:
        super().__init__(message)

class InvalidServiceWorkOrderState(ConflictException):
    def __init__(self, message: str = "Invalid serviceworkorder state") -> None:
        super().__init__(message)

class InvalidServiceTaskState(ConflictException):
    def __init__(self, message: str = "Invalid servicetask state") -> None:
        super().__init__(message)

class InvalidServiceChecklistState(ConflictException):
    def __init__(self, message: str = "Invalid servicechecklist state") -> None:
        super().__init__(message)

class InvalidServiceVisitState(ConflictException):
    def __init__(self, message: str = "Invalid servicevisit state") -> None:
        super().__init__(message)

class InvalidServiceMaterialState(ConflictException):
    def __init__(self, message: str = "Invalid servicematerial state") -> None:
        super().__init__(message)

class InvalidServiceTimeEntryState(ConflictException):
    def __init__(self, message: str = "Invalid servicetimeentry state") -> None:
        super().__init__(message)

class InvalidServiceExpenseState(ConflictException):
    def __init__(self, message: str = "Invalid serviceexpense state") -> None:
        super().__init__(message)

class InvalidServiceSlaState(ConflictException):
    def __init__(self, message: str = "Invalid servicesla state") -> None:
        super().__init__(message)

class InvalidServiceEscalationState(ConflictException):
    def __init__(self, message: str = "Invalid serviceescalation state") -> None:
        super().__init__(message)

class InvalidServiceFeedbackState(ConflictException):
    def __init__(self, message: str = "Invalid servicefeedback state") -> None:
        super().__init__(message)

class InvalidServiceResolutionState(ConflictException):
    def __init__(self, message: str = "Invalid serviceresolution state") -> None:
        super().__init__(message)

class InvalidServiceDocumentState(ConflictException):
    def __init__(self, message: str = "Invalid servicedocument state") -> None:
        super().__init__(message)

class InvalidServiceNotificationState(ConflictException):
    def __init__(self, message: str = "Invalid servicenotification state") -> None:
        super().__init__(message)

class InvalidServiceContractState(ConflictException):
    def __init__(self, message: str = "Invalid servicecontract state") -> None:
        super().__init__(message)

class InvalidServiceReportState(ConflictException):
    def __init__(self, message: str = "Invalid servicereport state") -> None:
        super().__init__(message)
