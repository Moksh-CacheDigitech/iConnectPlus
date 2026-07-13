"""Master Data domain value objects."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AddressJson:
    line1: str
    city: str
    country_code: str
    state: str | None = None
    postal_code: str | None = None

    def to_dict(self) -> dict:
        return {
            "line1": self.line1,
            "city": self.city,
            "country_code": self.country_code,
            "state": self.state,
            "postal_code": self.postal_code,
        }
