"""Sales domain exceptions."""

from core.exceptions import AppException, ConflictException


class CreditLimitExceeded(ConflictException):
    def __init__(self, message: str = "Customer credit limit exceeded") -> None:
        super().__init__(message)


class CreditHoldError(ConflictException):
    def __init__(self, message: str = "Customer is on credit hold") -> None:
        super().__init__(message)


class InvalidConversion(ConflictException):
    def __init__(self, message: str = "Document cannot be converted in its current state") -> None:
        super().__init__(message)


class InvalidDocumentState(ConflictException):
    def __init__(self, message: str = "Invalid document state for this operation") -> None:
        super().__init__(message)


class PricingNotFound(AppException):
    def __init__(self, message: str = "No matching price found") -> None:
        super().__init__(message, status_code=404)


class SegregationOfDutiesError(ConflictException):
    def __init__(self, message: str = "Segregation of duties violation") -> None:
        super().__init__(message)


class QuantityExceeded(ConflictException):
    def __init__(self, message: str = "Quantity exceeds allowed remaining quantity") -> None:
        super().__init__(message)
