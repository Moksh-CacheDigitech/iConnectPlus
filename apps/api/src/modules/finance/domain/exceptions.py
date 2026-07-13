"""Finance domain exceptions."""

from core.exceptions import AppException, ConflictException


class UnbalancedJournal(AppException):
    def __init__(self, message: str = "Journal is not balanced: total debit must equal total credit") -> None:
        super().__init__(message, status_code=409)


class PeriodClosed(ConflictException):
    def __init__(self, message: str = "Accounting period is closed for posting") -> None:
        super().__init__(message)


class PostingError(ConflictException):
    def __init__(self, message: str = "Journal posting failed") -> None:
        super().__init__(message)


class JournalStateError(ConflictException):
    def __init__(self, message: str = "Invalid journal state for this operation") -> None:
        super().__init__(message)


class SegregationOfDutiesError(ConflictException):
    def __init__(self, message: str = "Segregation of duties violation") -> None:
        super().__init__(message)
