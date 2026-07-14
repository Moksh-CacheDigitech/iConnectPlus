"""HolidayCalendar lifecycle engine."""

from modules.hr.domain.enums import HolidayCalendarStatus
from modules.hr.domain.exceptions import InvalidHolidayCalendarState


class HolidayCalendarEngine:
    def publish(self, row) -> None:
        if row.status != HolidayCalendarStatus.DRAFT.value:
            raise InvalidHolidayCalendarState("Only draft calendars can be published")
        row.status = HolidayCalendarStatus.PUBLISHED.value

    def archive(self, row) -> None:
        if row.status != HolidayCalendarStatus.PUBLISHED.value:
            raise InvalidHolidayCalendarState("Only published calendars can be archived")
        row.status = HolidayCalendarStatus.ARCHIVED.value
