"""Master Data domain exceptions."""


class MasterDataException(Exception):
    """Base master data domain exception."""


class DuplicateMasterCodeError(MasterDataException):
    """Raised when a duplicate business code is detected."""


class InvalidStatusTransitionError(MasterDataException):
    """Raised when an invalid status transition is attempted."""


class VersionConflictError(MasterDataException):
    """Raised on optimistic locking version mismatch."""
