"""Document numbering SSOT port."""

from __future__ import annotations

from typing import Protocol

from modules.platform.dto import NumberRequest


class IDocumentNumbering(Protocol):
    def next_number(self, request: NumberRequest) -> str:
        """Allocate next document number for sequence_key within tenant/company."""
        ...
