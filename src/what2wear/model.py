"""The domain vocabulary, as data.

See CONTEXT.md -- these names are authoritative. The Wardrobe's own
shape lives in `wardrobe.py`; everything here is either what the tool
has been told or what it derived.
"""

from dataclasses import dataclass
from datetime import date
from enum import StrEnum

from what2wear import wardrobe


class DayType(StrEnum):
    """Every date is exactly one of these."""

    OFFICE = "office"
    HOME = "home"


@dataclass(frozen=True)
class State:
    """Everything the tool has been told, in memory.

    Nothing structural appears here: the Wardrobe is given, so a State
    is the recorded decisions and nothing else.
    """

    overrides: tuple[DayTypeOverride, ...] = ()
    resets: tuple[Reset, ...] = ()

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
            pattern_day_type(on),
        )

    def shirt_shift(self, day_type: DayType, on: date) -> int:
        """Add up what the Resets in force on a date move a Closet by.

        A Reset is permanent from its own date forward. Which Closet
        it moves is the one its own date drew from, which is why the
        record names the Shirt Rotation and not which of the two --
        and why an Override recorded later against that same date
        carries the Reset across to the other Closet with it.
        """
        return sum(
            reset.offset
            for reset in self.resets
            if reset.rotation is Rotation.SHIRT
            and reset.on <= on
            and self.day_type(reset.on) is day_type
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
            - (pattern_day_type(on) is day_type)
            for on in frozenset(
                override.on for override in self.overrides
            )
            if start <= on < end
        )


def closet_for(day_type: DayType) -> wardrobe.Closet:
    """Give the Closet a kind of day draws from."""
    return (
        wardrobe.DEFAULT_OFFICE
        if day_type is DayType.OFFICE
        else wardrobe.DEFAULT_HOME
    )


def pattern_day_type(on: date) -> DayType:
    """Say what the given weekly pattern alone makes a date.

    Before any Override. Office Days follow the given weekdays; every
    other date, weekends included, is a Home Day.
    """
    return (
        DayType.OFFICE
        if on.weekday() in wardrobe.DEFAULT_OFFICE_WEEKDAYS
        else DayType.HOME
    )


@dataclass(frozen=True)
class DayTypeOverride:
    """A record of what one date is, whatever the pattern says.

    An Office Day or a Home Day. Staying home on a Wednesday, going
    in on a Saturday, a public holiday and a day of leave are all this
    one thing.
    """

    on: date
    day_type: DayType


class Rotation(StrEnum):
    """Which Rotation a Reset shifts.

    The Closet a Shirt Reset moves is inferred from its date, so the
    only thing a record has to name is the kind of Rotation.
    """

    SHIRT = "shirt"


@dataclass(frozen=True)
class Reset:
    """A record shifting one Rotation from a date forward, for good.

    Every later date moves with it, so the Rotation stays continuous
    rather than snapping back the next day.
    """

    on: date
    rotation: Rotation
    offset: int


type Decision = DayTypeOverride | Reset


@dataclass(frozen=True)
class ResetRequest:
    """A command asking for a Reset, before its offset is known.

    Bare, it moves on to the next Shirt. Naming a Shirt jumps to that
    one instead; the Closet comes from the date, never from the Label.
    """

    shirt: str | None = None


@dataclass(frozen=True)
class Response:
    """What a command resolved to, ready for a shell to render."""

    on: date
    day_type: DayType
    outfit: Outfit
    unavoidable_repeat: bool = False
    decision: Decision | None = None


@dataclass(frozen=True)
class Outfit:
    """The resolved garments for one date.

    Always derived, never authored.
    """

    shirt: str
    pants: str
    sweater: str
    shoes: str
