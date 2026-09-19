"""The types the package passes between its modules."""

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import date
from enum import StrEnum
from types import MappingProxyType

type UpdateFunction = Callable[[State], State]


@dataclass(frozen=True)
class State:
    """The recorded state.

    Attributes:
        anchors: Where each rotation stood, keyed by day type.
        labels: Each garment's place in its closet, such as
            `office.shirt.0` or `pants.1`, mapped to the label the
            garment there has now.
        overrides: The day type recorded for a date, keyed by date.
    """

    anchors: Mapping[DayType, Anchor]
    labels: Mapping[str, str]
    overrides: Mapping[date, DayType] = MappingProxyType({})


@dataclass(frozen=True)
class Anchor:
    """The closet position the rotation stood at on `on`."""

    on: date
    position: int


@dataclass(frozen=True)
class Response:
    """The answer for one date.

    Attributes:
        on: The date answered for.
        day_type: The kind of day it is.
        outfit: What to wear on it.
        unavoidable_repeat: Whether its sweater was already worn that
            week.
        cold: Whether it is cold enough for the outfit's sweater, or
            None if its weather is not known. A warm day names no
            sweater; an unknown one names it, to be worn if it's cold.
    """

    on: date
    day_type: DayType
    outfit: Outfit
    unavoidable_repeat: bool = False
    cold: bool | None = None


@dataclass(frozen=True)
class Outfit:
    """The garments worn on a day, the sweater only if it's cold."""

    shirt: str
    pants: str
    sweater: str | None
    shoes: str


@dataclass(frozen=True)
class Closet:
    """The shirts and pants rows available for a day type."""

    shirts: tuple[Shirt, ...]
    rows: tuple[PantsRow, ...]


@dataclass(frozen=True)
class Shirt:
    """A shirt and the pants worn with it."""

    garment: str
    pants: str


@dataclass(frozen=True)
class PantsRow:
    """The sweater and shoes worn with `pants`.

    Attributes:
        pants: The pants the row hangs from.
        sweater: The sweater worn with them.
        shoes: The shoes worn with them.
        fallback: A second sweater, for when the first is taken.
    """

    pants: str
    sweater: str
    shoes: str
    fallback: str | None = None


class DayType(StrEnum):
    """The kind of day a date is."""

    OFFICE = "office"
    HOME = "home"
