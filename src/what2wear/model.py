"""The domain vocabulary, as data.

See CONTEXT.md -- these names are authoritative. The Wardrobe's own
shape lives in `wardrobe.py`; everything here is either what the tool
has been told or what it derived.
"""

from collections.abc import Mapping
from dataclasses import dataclass, replace
from datetime import date
from enum import StrEnum
from types import MappingProxyType

from what2wear import wardrobe


class DayType(StrEnum):
    """Every date is exactly one of these."""

    OFFICE = "office"
    HOME = "home"


_NOTHING_OVERRIDDEN: Mapping[date, DayType] = MappingProxyType({})


@dataclass(frozen=True)
class State:
    """Everything the tool has been told, in memory.

    Nothing structural appears here, and nothing is keyed by a Label:
    an Anchor states a Position and the Overrides are keyed by date,
    so replacing a Garment can never move a Rotation.
    """

    office_anchor: wardrobe.Anchor
    home_anchor: wardrobe.Anchor
    overrides: Mapping[date, DayType] = _NOTHING_OVERRIDDEN

    def anchor(self, day_type: DayType) -> wardrobe.Anchor:
        """Give the Anchor a kind of day's Shirts are counted from."""
        return (
            self.office_anchor
            if day_type is DayType.OFFICE
            else self.home_anchor
        )

    def moved(
        self, day_type: DayType, anchor: wardrobe.Anchor
    ) -> State:
        """Give back this State with one Shirt Anchor somewhere else.

        The other Rotation stays exactly where it stood, which is what
        lets a Reset be about the Closet the day drew from and nothing
        else.
        """
        return (
            replace(self, office_anchor=anchor)
            if day_type is DayType.OFFICE
            else replace(self, home_anchor=anchor)
        )

    def overriding(self, command: DayTypeOverride) -> State:
        """Give back this State with one more date said to be a kind.

        One record per date, so saying the opposite for a date
        replaces what was said before rather than stacking on it.
        """
        return replace(
            self,
            overrides=MappingProxyType(
                {**self.overrides, command.on: command.day_type}
            ),
        )

    def day_type(self, on: date) -> DayType:
        """Say what kind of day a date actually is.

        A Day Type Override wins over the weekly pattern. There is one
        record per date, so saying the opposite replaced what was said
        before rather than stacking on top of it.
        """
        return self.overrides.get(on, pattern_day_type(on))

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
            for on in self.overrides
            if start <= on < end
        )


def default_state(today: date) -> State:
    """Give the State a fresh installation starts from.

    The given Anchors with nothing recorded. It is what a missing
    State file reads as, and the first write is what pins it -- until
    then the Anchors move with today.
    """
    return State(
        office_anchor=wardrobe.default_anchor(today),
        home_anchor=wardrobe.default_anchor(today),
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
    """A command saying what one date is, whatever the pattern says.

    An Office Day or a Home Day. Staying home on a Wednesday, going
    in on a Saturday, a public holiday and a day of leave are all this
    one thing.
    """

    on: date
    day_type: DayType


@dataclass(frozen=True)
class ResetRequest:
    """A command moving the day's Shirt Rotation, always from today.

    Bare, it moves on to the next Shirt. Naming a Shirt jumps to that
    one instead; the Closet comes from the date, never from the Label.
    """

    shirt: str | None = None


type Command = DayTypeOverride | ResetRequest


@dataclass(frozen=True)
class Response:
    """What a date resolved to, ready for a shell to render."""

    on: date
    day_type: DayType
    outfit: Outfit
    unavoidable_repeat: bool = False


@dataclass(frozen=True)
class Outfit:
    """The resolved garments for one date.

    Always derived, never authored.
    """

    shirt: str
    pants: str
    sweater: str
    shoes: str
