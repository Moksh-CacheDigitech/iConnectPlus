"""ProjectStatusHistory lifecycle engine."""



class ProjectStatusHistoryEngine:
    def record(self, row) -> None:
        row.status = "recorded"

