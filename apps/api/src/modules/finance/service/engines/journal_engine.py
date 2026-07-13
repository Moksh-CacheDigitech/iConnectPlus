"""Journal validation engine."""

from decimal import Decimal

from modules.finance.domain.enums import JournalStatus, PeriodStatus
from modules.finance.domain.exceptions import PeriodClosed, UnbalancedJournal
from modules.finance.domain.value_objects import JournalTotals
from modules.finance.models.coa import FinChartOfAccount
from modules.finance.models.journal import FinJournalHeader


class JournalEngine:
    MIN_LINES = 2

    def validate_lines_count(self, lines: list) -> None:
        active_lines = [line for line in lines if not line.is_deleted]
        if len(active_lines) < self.MIN_LINES:
            raise UnbalancedJournal("Journal must have at least 2 lines")

    def validate_amounts(self, debit_amount: float, credit_amount: float) -> None:
        debit = Decimal(str(debit_amount))
        credit = Decimal(str(credit_amount))
        if debit > 0 and credit > 0:
            raise UnbalancedJournal("Line cannot have both debit and credit amounts")
        if debit == 0 and credit == 0:
            raise UnbalancedJournal("Line must have either debit or credit amount")

    def validate_posting_account(self, account: FinChartOfAccount) -> None:
        if not account.is_posting_account:
            raise UnbalancedJournal(f"Account {account.account_code} is not a posting account")
        if account.status != "active":
            raise UnbalancedJournal(f"Account {account.account_code} is not active")

    def validate_cost_center(self, account: FinChartOfAccount, cost_center_id) -> None:
        if account.is_cost_center_enabled and cost_center_id is None:
            raise UnbalancedJournal(
                f"Cost center required for account {account.account_code}"
            )

    def compute_totals(self, lines: list) -> JournalTotals:
        active_lines = [line for line in lines if not line.is_deleted]
        return JournalTotals.from_lines(active_lines)

    def validate_balanced(self, totals: JournalTotals) -> None:
        if not totals.is_balanced:
            raise UnbalancedJournal(
                f"Journal not balanced: debit={totals.total_debit}, credit={totals.total_credit}"
            )

    def validate_period_for_journal(
        self,
        period,
        journal_status: str,
        *,
        allow_adjustment: bool = False,
    ) -> None:
        if period.status == PeriodStatus.HARD_CLOSED.value:
            raise PeriodClosed("Period is hard closed")
        if period.status == PeriodStatus.SOFT_CLOSED.value:
            if journal_status != JournalStatus.ADJUSTMENT.value and not allow_adjustment:
                raise PeriodClosed("Period is soft closed; only adjustment journals allowed")

    def apply_totals_to_header(self, journal: FinJournalHeader, totals: JournalTotals) -> None:
        journal.total_debit = float(totals.total_debit)
        journal.total_credit = float(totals.total_credit)

    def compute_base_amounts(
        self, amount: Decimal, exchange_rate: Decimal
    ) -> tuple[float, float]:
        base = float((amount * exchange_rate).quantize(Decimal("0.0001")))
        return base, base
