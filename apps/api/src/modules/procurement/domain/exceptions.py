"""Procurement domain exceptions."""

from core.exceptions import AppException, ConflictException


class InvalidDocumentState(ConflictException):
    def __init__(self, message: str = "Invalid document state for this operation") -> None:
        super().__init__(message)


class InvalidConversion(ConflictException):
    def __init__(self, message: str = "Document cannot be converted in its current state") -> None:
        super().__init__(message)


class SegregationOfDutiesError(ConflictException):
    def __init__(self, message: str = "Segregation of duties violation") -> None:
        super().__init__(message)


class QuantityExceeded(ConflictException):
    def __init__(self, message: str = "Quantity exceeds allowed remaining quantity") -> None:
        super().__init__(message)


class VendorQuotationExpired(ConflictException):
    def __init__(self, message: str = "Vendor quotation has expired") -> None:
        super().__init__(message)


class InvoiceAlreadyPosted(ConflictException):
    def __init__(self, message: str = "Invoice is already posted and cannot be modified") -> None:
        super().__init__(message)


class ProcurementScopeError(AppException):
    def __init__(self, message: str = "Procurement scope validation failed") -> None:
        super().__init__(message, status_code=403)


class ContractExpired(ConflictException):
    def __init__(self, message: str = "Vendor contract has expired") -> None:
        super().__init__(message)
