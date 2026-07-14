"""Manufacturing domain exceptions."""

from core.exceptions import AppException, ConflictException


class InvalidBomState(ConflictException):
    def __init__(self, detail: str = "Invalid BOM state") -> None:
        super().__init__(detail)


class ActiveBomExists(ConflictException):
    def __init__(self, detail: str = "Active BOM already exists for product") -> None:
        super().__init__(detail)


class InvalidProductionOrderState(ConflictException):
    def __init__(self, detail: str = "Invalid production order state") -> None:
        super().__init__(detail)


class InvalidMaterialDocumentState(ConflictException):
    def __init__(self, detail: str = "Invalid material document state") -> None:
        super().__init__(detail)


class InvalidScrapState(ConflictException):
    def __init__(self, detail: str = "Invalid scrap state") -> None:
        super().__init__(detail)


class InvalidWipState(ConflictException):
    def __init__(self, detail: str = "Invalid WIP state") -> None:
        super().__init__(detail)


class InvalidRoutingState(ConflictException):
    def __init__(self, detail: str = "Invalid routing state") -> None:
        super().__init__(detail)


class BomExplosionError(AppException):
    def __init__(self, detail: str = "BOM explosion failed") -> None:
        super().__init__(detail)
