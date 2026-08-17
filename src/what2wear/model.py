"""The domain vocabulary, as data.

See CONTEXT.md -- these names are authoritative.
"""

from dataclasses import dataclass
from datetime import date
from enum import StrEnum


@dataclass(frozen=True)
class State:
    """Everything the core needs to answer a question, in memory."""

    office: Closet
    home: Closet
    office_weekdays: frozenset[int]
    overrides: tuple[DayTypeOverride, ...] = ()

    def day_type(self, on: date) -> DayType:
        """Say what kind of day a date actually is.

        A Day Type Override wins over the weekly pattern, and a later
        record wins over an earlier one for the same date.
        """
        return next(
            (
                override.day_type
                for override in reversed(self.overrides)
                if override.on == on
            ),
            self.pattern_day_type(on),
        )

    def pattern_day_type(self, on: date) -> DayType:
        """Say what the weekly pattern alone makes a date.

        Before any Override. Office Days follow the configured
        weekdays; every other date is a Home Day.
        """
        return (
            DayType.OFFICE
            if on.weekday() in self.office_weekdays
            else DayType.HOME
        )

    def overridden_days(
        self, day_type: DayType, start: date, end: date
    ) -> int:
        """Count what the Overrides in [start, end) add or take away.

        Days of `day_type`, against the weekly pattern. This is what
        parks a Rotation: a day overridden away from its
        own kind stops counting, so the Shirt it would have worn falls
        to the next day of that kind instead of being lost.
        """
        return sum(
            (self.day_type(on) is day_type)
            - (self.pattern_day_type(on) is day_type)
            for on in frozenset(
                override.on for override in self.overrides
            )
            if start <= on < end
        )


@dataclass(frozen=True)
class Closet:
    """One setting's Shirts, its Pants Rows and its Anchor Date.

    The anchor is authored the way it is spoken -- a date and the
    Shirt worn on that date -- rather than as a Position.

    The lookups below assume a Closet that came through the config
    boundary, which is what makes every one of them total.
    """

    shirts: tuple[Shirt, ...]
    pants: tuple[PantsRow, ...]
    anchor_date: date
    anchor_shirt: str

    def index_of(self, name: str) -> int:
        """Give the Position a named Shirt sits at."""
        return next(
            index
            for index, shirt in enumerate(self.shirts)
            if shirt.name == name
        )

    def row_for(self, pants: str) -> PantsRow:
        """Give the row that dresses a colour of pants."""
        return next(row for row in self.pants if row.pants == pants)

    def row_wearing(self, sweater: str) -> PantsRow:
        """Trace a sweater back to the row it belongs to.

        Office sweaters pair one-to-one with rows -- the config
        boundary refuses a Closet where they don't -- so a Fallback
        can be traced back to the row whose shoes it borrows.
        """
        return next(row for row in self.pants if row.sweater == sweater)


@dataclass(frozen=True)
class Shirt:
    """The authored unit of a Closet, carrying its pants."""

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
class DayTypeOverride:
    """A record of what one date is, whatever the pattern says.

    An Office Day or a Home Day. Staying home on a Wednesday, going
    in on a Saturday, a public holiday and a day of leave are all this
    one thing.
    """

    on: date
    day_type: DayType


@dataclass(frozen=True)
class Response:
    """What a command resolved to, ready for a shell to render."""

    on: date
    day_type: DayType
    outfit: Outfit
    unavoidable_repeat: bool = False
    decision: DayTypeOverride | None = None


@dataclass(frozen=True)
class Outfit:
    """The resolved garments for one date.

    Always derived, never authored.
    """

    shirt: str
    pants: str
    sweater: str
    shoes: str
