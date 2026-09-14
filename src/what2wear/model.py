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
    """The answer for one date."""

    on: date
    day_type: DayType
    outfit: Outfit
    unavoidable_repeat: bool = False


@dataclass(frozen=True)
class Outfit:
    """The four garments worn on a day."""

    shirt: str
    pants: str
    sweater: str
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
