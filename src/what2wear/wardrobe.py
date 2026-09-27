"""Everything given: the Wardrobe, and the state a wearer starts from.

The Wardrobe's shape -- the closets, their shirts and the pants rows
that dress them -- is given and absolute. Alongside it sit the
starting values the state overlays when nothing has been told: the
labels and their colors, the anchors, the office weekdays and the cold
threshold.
"""

from collections.abc import Mapping
from datetime import date
from types import MappingProxyType

from what2wear.model import (
    Anchor,
    Closet,
    DayType,
    PantsRow,
    Rotation,
    Shirt,
    State,
)

WEEKDAYS = ("mon", "tue", "wed", "thu", "fri", "sat", "sun")
MON, WED, FRI = 0, 2, 4
DEFAULT_OFFICE_WEEKDAYS = frozenset({MON, WED, FRI})
DEFAULT_COLD_THRESHOLD = 50  # degrees Fahrenheit
LATITUDE, LONGITUDE = 38.9, -77.04  # Washington, DC.
HOME_OUTERWEAR = ("jacket", "sweater")


def get_default_state(today: date) -> State:
    """Build the state a wearer starts from.

    Args:
        today: The date every rotation is anchored to.

    Returns:
        A state with every rotation at position 0.
    """
    return State(
        anchors=MappingProxyType(
            {
                rotation: Anchor(today, position=0)
                for rotation in Rotation
            }
        ),
        labels=build_default_labels(),
        colors=build_default_colors(),
        office_weekdays=DEFAULT_OFFICE_WEEKDAYS,
        cold_threshold=DEFAULT_COLD_THRESHOLD,
    )


def build_default_labels() -> Mapping[str, str]:
    """Build the labels a wearer starts from.

    Returns:
        Each garment's place mapped to the name it was given.
    """
    return MappingProxyType(
        {
            f"pants.{place}": row.pants
            for place, row in enumerate(CLOSETS[DayType.OFFICE].rows)
        }
        | {
            f"{day_type}.{kind}.{place}": garment
            for day_type, closet in CLOSETS.items()
            for kind, place, garment, _ in get_garments(closet)
        }
    )


def build_default_colors() -> Mapping[str, tuple[str, str | None]]:
    """Build the colors a wearer starts from.

    Returns:
        Each garment's place mapped to the color its given name
        says, and the color of its stripes, if it has any.
    """
    return MappingProxyType(
        {
            key: COLORS[label]
            for key, label in build_default_labels().items()
        }
    )


def get_garments(
    closet: Closet,
) -> tuple[tuple[str, int, str, str], ...]:
    """List everything in a closet.

    Args:
        closet: The closet to list.

    Returns:
        A `(kind, place, garment, pants)` quadruple for each shirt,
        sweater, jacket and pair of shoes. Two rows wearing one garment
        share its place, so the black shoes worn with both blue and tan
        pants are one pair listed twice, not two pairs.
    """
    sweaters = tuple(dict.fromkeys(row.sweater for row in closet.rows))
    jackets = tuple(
        dict.fromkeys(
            row.jacket for row in closet.rows if row.jacket is not None
        )
    )
    shoes = tuple(dict.fromkeys(row.shoes for row in closet.rows))
    return (
        *(
            ("shirt", place, shirt.garment, shirt.pants)
            for place, shirt in enumerate(closet.shirts)
        ),
        *(
            (
                "sweater",
                sweaters.index(row.sweater),
                row.sweater,
                row.pants,
            )
            for row in closet.rows
        ),
        *(
            ("jacket", jackets.index(row.jacket), row.jacket, row.pants)
            for row in closet.rows
            if row.jacket is not None
        ),
        *(
            ("shoes", shoes.index(row.shoes), row.shoes, row.pants)
            for row in closet.rows
        ),
    )


CLOSETS: Mapping[DayType, Closet] = MappingProxyType(
    {
        DayType.OFFICE: Closet(
            shirts=(
                Shirt("White", "Blue"),
                Shirt("Black", "Tan"),
                Shirt("Light Blue", "Black"),
                Shirt("Striped", "Blue"),
                Shirt("Dark Blue", "Tan"),
            ),
            rows=(
                PantsRow(
                    "Blue",
                    sweater="Beige",
                    shoes="Brown",
                    fallback="Grey",
                ),
                PantsRow(
                    "Tan",
                    sweater="Black",
                    shoes="Black",
                    fallback="Grey",
                ),
                PantsRow("Black", sweater="Grey", shoes="White"),
            ),
        ),
        DayType.HOME: Closet(
            shirts=(
                Shirt("White", "Blue"),
                Shirt("Brown", "Black"),
                Shirt("Dark Green", "Tan"),
                Shirt("Black", "Blue"),
                Shirt("Purple", "Black"),
                Shirt("Dark Blue", "Tan"),
                Shirt("Beige", "Blue"),
                Shirt("Light Blue", "Black"),
                Shirt("Light Green", "Tan"),
            ),
            rows=(
                PantsRow(
                    "Blue",
                    sweater="Yellow",
                    shoes="Black",
                    jacket="Brown",
                ),
                PantsRow(
                    "Tan", sweater="Blue", shoes="Black", jacket="Black"
                ),
                PantsRow(
                    "Black",
                    sweater="Beige",
                    shoes="White",
                    jacket="Black",
                ),
            ),
        ),
    }
)

COLORS: Mapping[str, tuple[str, str | None]] = MappingProxyType(
    {
        "White": ("#f4f4f1", None),
        "Black": ("#26262a", None),
        "Grey": ("#8e8e93", None),
        "Brown": ("#6f4a2e", None),
        "Tan": ("#c9a878", None),
        "Beige": ("#e4d5b4", None),
        "Light Blue": ("#9fc8ee", None),
        "Dark Blue": ("#23406e", None),
        "Blue": ("#3c67b4", None),
        "Yellow": ("#f2c84b", None),
        "Dark Green": ("#2e5e3b", None),
        "Light Green": ("#a3d69c", None),
        "Purple": ("#7a4ea3", None),
        "Striped": ("#f4f4f1", "#3c67b4"),
    }
)

KEYS: Mapping[str, str] = MappingProxyType(
    {
        f"pants.{row.pants}": f"pants.{place}"
        for place, row in enumerate(CLOSETS[DayType.OFFICE].rows)
    }
    | {
        f"{day_type}.{kind}.{garment}": f"{day_type}.{kind}.{place}"
        for day_type, closet in CLOSETS.items()
        for kind, place, garment, _ in get_garments(closet)
    }
)
