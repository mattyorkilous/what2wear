"""The closets, and the default state built from them."""

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
                Shirt("white", "blue"),
                Shirt("black", "tan"),
                Shirt("lblue", "black"),
                Shirt("striped", "blue"),
                Shirt("dblue", "tan"),
            ),
            rows=(
                PantsRow(
                    "blue",
                    sweater="beige",
                    shoes="brown",
                    fallback="grey",
                ),
                PantsRow(
                    "tan",
                    sweater="black",
                    shoes="black",
                    fallback="grey",
                ),
                PantsRow("black", sweater="grey", shoes="white"),
            ),
        ),
        DayType.HOME: Closet(
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
                    "blue",
                    sweater="yellow",
                    shoes="black",
                    jacket="brown",
                ),
                PantsRow(
                    "tan", sweater="blue", shoes="black", jacket="black"
                ),
                PantsRow(
                    "black",
                    sweater="beige",
                    shoes="white",
                    jacket="black",
                ),
            ),
        ),
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
