"""The domain vocabulary, as data. See CONTEXT.md -- these names are authoritative."""

from dataclasses import dataclass
from datetime import date
from enum import StrEnum


class DayType(StrEnum):
    """Every date is exactly one of these."""

    OFFICE = "office"
    HOME = "home"


@dataclass(frozen=True)
class Shirt:
    """The authored unit of a Closet, carrying the pants welded to it."""

    name: str
    pants: str


@dataclass(frozen=True)
class Closet:
    """An ordered list of Shirts for one setting, plus the Anchor Date it counts from.

    The anchor is authored the way it is spoken -- a date and the Shirt worn on
    that date -- rather than as a Position.
    """

    shirts: tuple[Shirt, ...]
    anchor_date: date
    anchor_shirt: str

    def index_of(self, name: str) -> int:
        for index, shirt in enumerate(self.shirts):
            if shirt.name == name:
                return index
        raise ValueError(f"no shirt named {name!r} in this closet")


@dataclass(frozen=True)
class State:
    """Everything the core needs to answer a question, parsed and in memory."""

    office: Closet
    home: Closet
    office_weekdays: frozenset[int]

    def closet_for(self, day_type: DayType) -> Closet:
        return self.office if day_type is DayType.OFFICE else self.home


@dataclass(frozen=True)
class Show:
    """Show the Outfit for a date, defaulting to today."""

    on: date | None = None


@dataclass(frozen=True)
class Outfit:
    """The resolved garments for one date. Always derived, never authored."""

    shirt: str
    pants: str


@dataclass(frozen=True)
class Response:
    """What a command resolved to, ready for a shell to render."""

    on: date
    day_type: DayType
    outfit: Outfit
