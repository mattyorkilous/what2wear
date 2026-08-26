"""The given Wardrobe, and what a fresh installation starts from.

Not configured, not read from disk, not told to the tool. The
Wardrobe's shape is a fact about the person the tool dresses, per
ADR-0005, so the properties the rest of the code leans on -- one Label
per Garment within a Closet, a row per pair of Pants, a Fallback that
is another row's sweater, office sweaters one-to-one with office shoes
-- are asserted once by `test_wardrobe.py`.

The `DEFAULT_` names and `get_default_*` are the values a fresh
installation starts from, with nothing recorded. The Closets' *shape*
is not a default and never moves: it cannot be added to, removed from
or re-paired at runtime. Nothing here decides anything -- the only
function that reads these values assembles the starting State from
them; every rule lives in `core.py`.
"""

from datetime import date

from what2wear.model import Anchor, Closet, PantsRow, Shirt, State

MON, WED, FRI = 0, 2, 4
DEFAULT_OFFICE_WEEKDAYS = frozenset({MON, WED, FRI})


def get_default_state(today: date) -> State:
    """Give the State a fresh installation starts from.

    The given Anchors with nothing recorded. It is what a missing
    State file reads as, and the first write is what pins it -- until
    then the Anchors move with today.
    """
    return State(
        office_anchor=get_default_anchor(today),
        home_anchor=get_default_anchor(today),
    )


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
