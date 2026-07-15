"""E-Commerce value objects."""

from dataclasses import dataclass


@dataclass(frozen=True)
class EcommerceCodes:
    document_number: str
