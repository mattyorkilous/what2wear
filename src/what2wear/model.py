"""The domain vocabulary, as types.

See CONTEXT.md -- these names are authoritative. Nothing here decides
anything: the values a fresh installation starts from live in
`wardrobe.py`, and every rule that reads either lives in `core.py`.
This module imports nothing else from the tool, which is what lets the
other two import it.
"""

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date
from enum import StrEnum
from types import MappingProxyType


@dataclass(frozen=True)
class State:
    """Everything the tool has been told, in memory.

    Nothing structural appears here, and nothing is keyed by a Label:
    an Anchor states a Position, the Anchors are keyed by the kind of
    day their Rotation dresses and the Overrides are keyed by date, so
    replacing a Garment can never move a Rotation.
    """

    anchors: Mapping[DayType, Anchor]
    overrides: Mapping[date, DayType] = MappingProxyType({})


@dataclass(frozen=True)
class Anchor:
    """A date and the Position one Rotation stood at on it.

    A Position rather than a Label, so that renaming a Garment can
    never move a Rotation.
    """

    on: date
    position: int


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


type Command = DayTypeOverride | ResetRequest


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
    """A command moving a Shirt Rotation, from the date it acts on.

    Bare, it moves on to the next Shirt. Naming a Shirt jumps to that
    one instead; the Closet comes from the date, never from the Label.
    """

    shirt: str | None = None


@dataclass(frozen=True)
class Closet:
    """One setting's Shirts and its Pants Rows."""

    shirts: tuple[Shirt, ...]
    rows: tuple[PantsRow, ...]


@dataclass(frozen=True)
class Shirt:
    """One position in a Closet, carrying the Pants welded to it."""

    label: str
    pants: str


@dataclass(frozen=True)
class PantsRow:
    """What one Closet pairs with one pair of Pants.

    Sweaters and shoes follow from the Pants rather than from the
    Shirt, so a Closet has three of these however many Shirts it
    holds. Only the Office Closet fills in `fallback`, because only an
    Office Week has a sweater it may not repeat.
    """

    pants: str
    sweater: str
    shoes: str
    fallback: str | None = None


class DayType(StrEnum):
    """Every date is exactly one of these."""

    OFFICE = "office"
    HOME = "home"
