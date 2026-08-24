"""The given Wardrobe: two Closets and the Pants they share.

Not configured, not read from disk, not told to the tool. Its shape is
a fact about the person the tool dresses, per ADR-0005, so the
properties the rest of the code leans on -- one Label per Garment
within a Closet, a row per pair of Pants, a Fallback that is another
row's sweater, office sweaters one-to-one with office shoes -- are
asserted once by `test_wardrobe.py`.

The `DEFAULT_` names are the values a fresh installation starts from,
with nothing recorded. The Closets' *shape* is not a default and never
moves: it cannot be added to, removed from or re-paired at runtime.
"""

from dataclasses import dataclass
from datetime import date

MON, WED, FRI = 0, 2, 4
DEFAULT_OFFICE_WEEKDAYS = frozenset({MON, WED, FRI})


@dataclass(frozen=True)
class Anchor:
    """A date and the Position one Rotation stood at on it.

    A Position rather than a Label, so that renaming a Garment can
    never move a Rotation.
    """

    on: date
    position: int


@dataclass(frozen=True)
class Shirt:
    """One position in a Closet, carrying the Pants welded to it."""

    label: str
    pants: str


@dataclass(frozen=True)
class PantsRow:
    """What one Closet pairs with one pair of Pants.

    Sweaters, jackets and shoes follow from the Pants rather than from
    the Shirt, so a Closet has three of these however many Shirts it
    holds. The Office Closet fills in `fallback` and never `jacket`;
    the Home Closet the other way round.
    """

    pants: str
    sweater: str
    shoes: str
    jacket: str | None = None
    fallback: str | None = None


@dataclass(frozen=True)
class Closet:
    """One setting's Shirts and its Pants Rows."""

    shirts: tuple[Shirt, ...]
    rows: tuple[PantsRow, ...]

    def get_position(self, label: str) -> int:
        """Give the Position a Shirt with this Label sits at."""
        return next(
            index
            for index, shirt in enumerate(self.shirts)
            if shirt.label == label
        )

    def get_row_for_pants(self, pants: str) -> PantsRow:
        """Give the row that dresses a pair of Pants."""
        return next(row for row in self.rows if row.pants == pants)

    def get_row_for_sweater(self, sweater: str) -> PantsRow:
        """Trace a sweater back to the row it belongs to.

        Office sweaters are one-to-one with office rows, so a Fallback
        can be traced back to the row whose shoes it borrows.
        """
        return next(row for row in self.rows if row.sweater == sweater)


def get_default_anchor(today: date) -> Anchor:
    """Say where every Rotation stands with nothing recorded.

    Today, at the top of its Closet, so that a fresh installation
    opens on the first Shirt rather than part-way through a Rotation
    it never chose. Both Closets hold `white` at Position 0.
    """
    return Anchor(today, position=0)


DEFAULT_OFFICE = Closet(
    shirts=(
        Shirt("white", "blue"),
        Shirt("black", "tan"),
        Shirt("lblue", "black"),
        Shirt("striped", "blue"),
        Shirt("dblue", "tan"),
    ),
    rows=(
        PantsRow(
            "blue", sweater="beige", shoes="brown", fallback="grey"
        ),
        PantsRow(
            "tan", sweater="black", shoes="black", fallback="grey"
        ),
        PantsRow("black", sweater="grey", shoes="white"),
    ),
)

DEFAULT_HOME = Closet(
    shirts=(
        Shirt("white", "blue"),
        Shirt("brown", "black"),
        Shirt("dgreen", "tan"),
        Shirt("black", "blue"),
        Shirt("purple", "black"),
        Shirt("dblue", "tan"),
        Shirt("beige", "blue"),
        Shirt("lblue", "black"),
        Shirt("lgreen", "tan"),
    ),
    rows=(
        PantsRow(
            "blue", sweater="yellow", jacket="brown", shoes="black"
        ),
        PantsRow("tan", sweater="blue", jacket="black", shoes="black"),
        PantsRow(
            "black", sweater="beige", jacket="black", shoes="white"
        ),
    ),
)
