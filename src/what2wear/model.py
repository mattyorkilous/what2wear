"""The types the package passes between its modules.

Each type is defined below the types that name it, which Python 3.13
allows only with annotations deferred.
"""

from __future__ import annotations

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
        anchors: Where each rotation stood.
        labels: Each garment's place in its closet, such as
            `office.shirt.0` or `pants.1`, mapped to the label the
            garment there has now.
        colors: Keyed like `labels`, each garment's color and the
            color of its stripes, if it has any, as `#rrggbb`.
        office_weekdays: The three weekdays, Monday 0, that are
            office days unless overridden.
        cold_threshold: The high, in degrees Fahrenheit, below which
            outerwear is worn.
        overrides: The day type recorded for a date, keyed by date.
    """

    anchors: Mapping[Rotation, Anchor]
    labels: Mapping[str, str]
    colors: Mapping[str, tuple[str, str | None]]
    office_weekdays: frozenset[int]
    cold_threshold: float
    overrides: Mapping[date, DayType] = MappingProxyType({})


@dataclass(frozen=True)
class Anchor:
    """The position a rotation stood at on `on`."""

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
        cold: Whether it is cold enough for the outfit's outerwear,
            or None if its weather is not known. A warm day names no
            outerwear; an unknown one names it, to be worn if it's
            cold.
    """

    on: date
    day_type: DayType
    outfit: Outfit
    unavoidable_repeat: bool = False
    cold: bool | None = None


@dataclass(frozen=True)
class Outfit:
    """The garments worn on a day, the outerwear only if it's cold.

    At most one of `sweater` and `jacket` is named.
    """

    shirt: Garment
    pants: Garment
    sweater: Garment | None
    shoes: Garment
    jacket: Garment | None = None


@dataclass(frozen=True)
class Garment:
    """A garment as the wearer knows it.

    Attributes:
        label: What it is called.
        color: The color it is drawn in, as `#rrggbb`.
        stripe_color: The color of its stripes, if it has any.
    """

    label: str
    color: str
    stripe_color: str | None = None


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
            Office rows only.
        jacket: The jacket worn with them. Home rows only.
    """

    pants: str
    sweater: str
    shoes: str
    fallback: str | None = None
    jacket: str | None = None


class DayType(StrEnum):
    """The kind of day a date is."""

    OFFICE = "office"
    HOME = "home"


class Rotation(StrEnum):
    """A rotation, named as the state file names its anchor.

    A closet's shirt rotation shares its day type's value, so
    `Rotation(day_type)` is that closet's.
    """

    OFFICE = "office"
    HOME = "home"
    OUTERWEAR = "outerwear"

    @property
    def day_type(self) -> DayType:
        """The kind of day the rotation advances on."""
        return (
            DayType.HOME
            if self is Rotation.OUTERWEAR
            else DayType(self)
        )
