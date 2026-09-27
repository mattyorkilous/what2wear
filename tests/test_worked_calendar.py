from datetime import date

import pytest

from what2wear.core import answer
from what2wear.model import DayType, Outfit
from what2wear.wardrobe import get_default_state

TODAY = date(2026, 8, 22)

SEQUENCE = [
    (
        date(2026, 8, 29),
        DayType.HOME,
        ("Purple", "Black", None, "White", "Black"),
    ),  # Sat -- a jacket day, and Sunday a sweater day
    (
        date(2026, 8, 30),
        DayType.HOME,
        ("Dark Blue", "Tan", "Blue", "Black", None),
    ),  # Sun
    (
        date(2026, 8, 31),
        DayType.OFFICE,
        ("Striped", "Blue", "Beige", "Brown", None),
    ),  # Mon -- takes beige, which Friday then wants
    (
        date(2026, 9, 1),
        DayType.HOME,
        ("Beige", "Blue", None, "Black", "Brown"),
    ),
    (
        date(2026, 9, 2),
        DayType.OFFICE,
        ("Dark Blue", "Tan", "Black", "Black", None),
    ),
    (
        date(2026, 9, 3),
        DayType.HOME,
        ("Light Blue", "Black", "Beige", "White", None),
    ),
    (
        date(2026, 9, 4),
        DayType.OFFICE,
        ("White", "Blue", "Grey", "White", None),
    ),  # Fri -- shares blue with Monday, so the fallback and its shoes
    (
        date(2026, 9, 5),
        DayType.HOME,
        ("Light Green", "Tan", None, "Black", "Black"),
    ),  # Sat -- the end of the home closet
    (
        date(2026, 9, 6),
        DayType.HOME,
        ("White", "Blue", "Yellow", "Black", None),
    ),  # Sun -- wraps back to the start
    (
        date(2026, 9, 7),
        DayType.HOME,
        ("Brown", "Black", None, "White", "Black"),
    ),  # Mon -- Labor Day, so a Home Day, and the next home shirt
]


@pytest.mark.parametrize(("on", "day_type", "outfit"), SEQUENCE)
def test_the_worked_calendar(
    on: date, day_type: DayType, outfit: tuple[str | None, ...]
) -> None:
    response = answer(get_default_state(TODAY), on, {})
    assert (response.day_type, _get_labels(response.outfit)) == (
        day_type,
        outfit,
    )


def _get_labels(outfit: Outfit) -> tuple[str | None, ...]:
    return tuple(
        None if garment is None else garment.label
        for garment in (
            outfit.shirt,
            outfit.pants,
            outfit.sweater,
            outfit.shoes,
            outfit.jacket,
        )
    )
