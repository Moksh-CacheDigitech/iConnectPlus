"""Platform ORM models for Alembic discovery."""

from modules.platform.models.idempotency import FndIdempotencyRecord
from modules.platform.models.job_run import FndJobRun
from modules.platform.models.numbering import FndDocumentSequence
from modules.platform.models.outbox import FndOutboxMessage
from modules.platform.read_models import (
    AnaFinancePostingFact,
    AnaInventoryMovementFact,
    AnaPayrollRunFact,
)

__all__ = [
    "AnaFinancePostingFact",
    "AnaInventoryMovementFact",
    "AnaPayrollRunFact",
    "FndDocumentSequence",
    "FndIdempotencyRecord",
    "FndJobRun",
    "FndOutboxMessage",
]
