"""Asset domain exceptions."""

from core.exceptions import ConflictException


class InvalidAssetCategoryState(ConflictException):
    def __init__(self, message: str = "Invalid assetcategory state") -> None:
        super().__init__(message)

class InvalidAssetState(ConflictException):
    def __init__(self, message: str = "Invalid asset state") -> None:
        super().__init__(message)

class InvalidAssetComponentState(ConflictException):
    def __init__(self, message: str = "Invalid assetcomponent state") -> None:
        super().__init__(message)

class InvalidAssetAssignmentState(ConflictException):
    def __init__(self, message: str = "Invalid assetassignment state") -> None:
        super().__init__(message)

class InvalidAssetTransferState(ConflictException):
    def __init__(self, message: str = "Invalid assettransfer state") -> None:
        super().__init__(message)

class InvalidAssetLocationState(ConflictException):
    def __init__(self, message: str = "Invalid assetlocation state") -> None:
        super().__init__(message)

class InvalidAssetWarrantyState(ConflictException):
    def __init__(self, message: str = "Invalid assetwarranty state") -> None:
        super().__init__(message)

class InvalidAssetInsuranceState(ConflictException):
    def __init__(self, message: str = "Invalid assetinsurance state") -> None:
        super().__init__(message)

class InvalidAssetMaintenancePlanState(ConflictException):
    def __init__(self, message: str = "Invalid assetmaintenanceplan state") -> None:
        super().__init__(message)

class InvalidAssetMaintenanceState(ConflictException):
    def __init__(self, message: str = "Invalid assetmaintenance state") -> None:
        super().__init__(message)

class InvalidAssetServiceHistoryState(ConflictException):
    def __init__(self, message: str = "Invalid assetservicehistory state") -> None:
        super().__init__(message)

class InvalidAssetDepreciationState(ConflictException):
    def __init__(self, message: str = "Invalid assetdepreciation state") -> None:
        super().__init__(message)

class InvalidAssetDisposalState(ConflictException):
    def __init__(self, message: str = "Invalid assetdisposal state") -> None:
        super().__init__(message)

class InvalidAssetRevaluationState(ConflictException):
    def __init__(self, message: str = "Invalid assetrevaluation state") -> None:
        super().__init__(message)

class InvalidAssetAuditState(ConflictException):
    def __init__(self, message: str = "Invalid assetaudit state") -> None:
        super().__init__(message)

class InvalidAssetDocumentState(ConflictException):
    def __init__(self, message: str = "Invalid assetdocument state") -> None:
        super().__init__(message)

class InvalidAssetChecklistState(ConflictException):
    def __init__(self, message: str = "Invalid assetchecklist state") -> None:
        super().__init__(message)

class InvalidAssetMeterReadingState(ConflictException):
    def __init__(self, message: str = "Invalid assetmeterreading state") -> None:
        super().__init__(message)

class InvalidAssetNotificationState(ConflictException):
    def __init__(self, message: str = "Invalid assetnotification state") -> None:
        super().__init__(message)

class InvalidAssetReportState(ConflictException):
    def __init__(self, message: str = "Invalid assetreport state") -> None:
        super().__init__(message)
