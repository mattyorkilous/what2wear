"""The domain vocabulary, as data.

See CONTEXT.md -- these names are authoritative.
"""

from dataclasses import dataclass
from datetime import date
from enum import StrEnum


@dataclass(frozen=True)
class State:
    """Everything the core needs to answer a question, parsed and in
    memory."""

    office: Closet
    home: Closet
    office_weekdays: frozenset[int]

    def day_type(self, on: date) -> DayType:
        """Office Days follow the weekday pattern; every other date is
        a Home Day."""
        return (
            DayType.OFFICE
            if on.weekday() in self.office_weekdays
            else DayType.HOME
        )

    def closet_for(self, day_type: DayType) -> Closet:
        return self.office if day_type is DayType.OFFICE else self.home


@dataclass(frozen=True)
class Closet:
    """An ordered list of Shirts for one setting, the rows that say
    what goes with their pants, and the Anchor Date it counts from.

    The anchor is authored the way it is spoken -- a date and the
    Shirt worn on that date -- rather than as a Position.
    """

    shirts: tuple[Shirt, ...]
    pants: tuple[PantsRow, ...]
    anchor_date: date
    anchor_shirt: str

    def index_of(self, name: str) -> int:
        for index, shirt in enumerate(self.shirts):
            if shirt.name == name:
                return index
        raise ValueError(f"no shirt named {name!r} in this closet")

    def row_for(self, pants: str) -> PantsRow:
        for row in self.pants:
            if row.pants == pants:
                return row
        raise ValueError(f"no row for {pants!r} pants in this closet")

    def row_wearing(self, sweater: str) -> PantsRow:
        """The row this sweater belongs to.

        Office sweaters pair one-to-one with rows -- the config
        boundary refuses a Closet where they don't -- so a Fallback
        can be traced back to the row whose shoes it borrows.
        """
        for row in self.pants:
            if row.sweater == sweater:
                return row
        raise ValueError(f"no row wears {sweater!r} in this closet")


@dataclass(frozen=True)
class Shirt:
    """The authored unit of a Closet, carrying the pants welded to
    it."""

    name: str
    pants: str


@dataclass(frozen=True)
class PantsRow:
    """What one Closet pairs with one pants colour.

    Sweaters, jackets and shoes are keyed by pants rather than by
    Shirt, so a Closet has three of these however many Shirts it
    holds. The Office Closet fills in `fallback` and never `jacket`;
    the Home Closet the other way round.
    """

    pants: str
    sweater: str
    shoes: str
    jacket: str | None = None
    fallback: str | None = None


class DayType(StrEnum):
    """Every date is exactly one of these."""

    OFFICE = "office"
    HOME = "home"


@dataclass(frozen=True)
class Show:
    """Show the Outfit for a date, defaulting to today."""

    on: date | None = None


@dataclass(frozen=True)
class Response:
    """What a command resolved to, ready for a shell to render."""

    on: date
    day_type: DayType
    outfit: Outfit
    unavoidable_repeat: bool = False
    """This Week ran out of office sweaters, so this one is worn
    twice. Only reachable when a Week has more Office Days than the
    Office Closet has sweaters left to offer it."""


@dataclass(frozen=True)
class Outfit:
    """The resolved garments for one date.

    Always derived, never authored.
    """

    shirt: str
    pants: str
    sweater: str
    shoes: str
