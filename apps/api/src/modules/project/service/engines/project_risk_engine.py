"""ProjectRisk lifecycle engine."""

from modules.project.domain.enums import (
    ProjectRiskStatus,
)
from modules.project.domain.exceptions import (
    InvalidProjectRiskState,
)


class ProjectRiskEngine:
    def mitigate(self, row) -> None:
        if row.status != ProjectRiskStatus.IDENTIFIED.value:
            raise InvalidProjectRiskState("Only identified risks can mitigate")
        row.status = ProjectRiskStatus.MITIGATING.value

    def accept(self, row) -> None:
        if row.status not in {ProjectRiskStatus.IDENTIFIED.value, ProjectRiskStatus.MITIGATING.value}:
            raise InvalidProjectRiskState("Risk not acceptable")
        row.status = ProjectRiskStatus.ACCEPTED.value

    def close(self, row) -> None:
        if row.status not in {ProjectRiskStatus.MITIGATING.value, ProjectRiskStatus.ACCEPTED.value}:
            raise InvalidProjectRiskState("Risk not closable")
        row.status = ProjectRiskStatus.CLOSED.value

    def cancel(self, row) -> None:
        if row.status in {ProjectRiskStatus.CLOSED.value, ProjectRiskStatus.CANCELLED.value}:
            raise InvalidProjectRiskState("Risk already terminal")
        row.status = ProjectRiskStatus.CANCELLED.value

