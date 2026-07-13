"""Standard API response schemas per SDD v1.1."""

from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    success: bool = True
    message: str
    data: T | None = None


class ErrorResponse(BaseModel):
    success: bool = False
    message: str
    errors: list[str] = Field(default_factory=list)
