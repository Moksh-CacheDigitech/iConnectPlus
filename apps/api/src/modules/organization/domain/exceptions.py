"""Organization domain exceptions."""

from core.exceptions import AppException


class OrganizationDomainException(AppException):
    """Base organization domain error."""


class HierarchyViolationException(OrganizationDomainException):
    def __init__(self, message: str = "Invalid organization hierarchy") -> None:
        super().__init__(message, status_code=400)


class OrgScopeDeniedException(OrganizationDomainException):
    def __init__(self, message: str = "Organization scope access denied") -> None:
        super().__init__(message, status_code=403)
