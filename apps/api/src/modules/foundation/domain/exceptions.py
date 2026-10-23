"""Foundation domain exceptions."""

from core.exceptions import AppException


class FoundationDomainException(AppException):
    """Base foundation domain error."""


class InvalidCredentialsException(FoundationDomainException):
    def __init__(self, message: str = "Invalid credentials") -> None:
        super().__init__(message, status_code=401)


class AccountLockedException(FoundationDomainException):
    def __init__(self, message: str = "Account is locked") -> None:
        super().__init__(message, status_code=403)


class PermissionDeniedException(FoundationDomainException):
    def __init__(self, message: str = "Permission denied") -> None:
        super().__init__(message, status_code=403)


class InvalidPasswordPolicyException(FoundationDomainException):
    def __init__(self, message: str = "Password does not meet policy requirements") -> None:
        super().__init__(message, status_code=422)


class WorkflowStateException(FoundationDomainException):
    def __init__(self, message: str = "Invalid workflow state transition") -> None:
        super().__init__(message, status_code=400)


class PasswordResetTokenInvalidException(FoundationDomainException):
    def __init__(
        self, message: str = "This reset link is invalid or has expired. Request a new one."
    ) -> None:
        super().__init__(message, status_code=400)


class ErpAdminRequiredException(FoundationDomainException):
    def __init__(self, message: str = "Only ERP admins can perform this action") -> None:
        super().__init__(message, status_code=403)
