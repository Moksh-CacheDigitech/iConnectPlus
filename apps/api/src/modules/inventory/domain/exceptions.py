"""Inventory domain exceptions."""

from core.exceptions import AppException, ConflictException


class InsufficientStock(ConflictException):
    def __init__(self, message: str = "Insufficient available stock") -> None:
        super().__init__(message)


class InvalidDocumentState(ConflictException):
    def __init__(self, message: str = "Invalid document state for this operation") -> None:
        super().__init__(message)


class SegregationOfDutiesError(ConflictException):
    def __init__(self, message: str = "Segregation of duties violation") -> None:
        super().__init__(message)


class InventoryPeriodClosed(ConflictException):
    def __init__(self, message: str = "Inventory period is closed") -> None:
        super().__init__(message)


class IdempotentReplay(AppException):
    def __init__(self, message: str = "Inventory movement already processed") -> None:
        super().__init__(message, status_code=200)


class InventoryScopeError(AppException):
    def __init__(self, message: str = "Inventory scope validation failed") -> None:
        super().__init__(message, status_code=403)


class ValuationError(ConflictException):
    def __init__(self, message: str = "FIFO valuation failed") -> None:
        super().__init__(message)
