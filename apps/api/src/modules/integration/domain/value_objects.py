"""Integration value objects."""

from dataclasses import dataclass


@dataclass(frozen=True)
class IntegrationCodes:
    document_number: str
