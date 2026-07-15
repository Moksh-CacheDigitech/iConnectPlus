"""ServiceFeedback lifecycle engine."""

from modules.service.domain.enums import (
    ServiceFeedbackStatus,
)
from modules.service.domain.exceptions import (
    InvalidServiceFeedbackState,
)


class ServiceFeedbackEngine:
    def review(self, row) -> None:
        if row.status != ServiceFeedbackStatus.CAPTURED.value:
            raise InvalidServiceFeedbackState("Only captured feedback can be reviewed")
        row.status = ServiceFeedbackStatus.REVIEWED.value

    def archive(self, row) -> None:
        row.status = ServiceFeedbackStatus.ARCHIVED.value

