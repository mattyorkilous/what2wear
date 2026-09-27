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
        ("purple", "black", None, "white", "black"),
    ),  # Sat -- a jacket day, and Sunday a sweater day
    (
        date(2026, 8, 30),
        DayType.HOME,
        ("dblue", "tan", "blue", "black", None),
    ),  # Sun
    (
        date(2026, 8, 31),
        DayType.OFFICE,
        ("striped", "blue", "beige", "brown", None),
    ),  # Mon -- takes beige, which Friday then wants
    (
        date(2026, 9, 1),
        DayType.HOME,
        ("beige", "blue", None, "black", "brown"),
    ),
    (
        date(2026, 9, 2),
        DayType.OFFICE,
        ("dblue", "tan", "black", "black", None),
    ),
    (
        date(2026, 9, 3),
        DayType.HOME,
        ("lblue", "black", "beige", "white", None),
    ),
    (
        date(2026, 9, 4),
        DayType.OFFICE,
        ("white", "blue", "grey", "white", None),
    ),  # Fri -- shares blue with Monday, so the fallback and its shoes
    (
        date(2026, 9, 5),
        DayType.HOME,
        ("lgreen", "tan", None, "black", "black"),
    ),  # Sat -- the end of the home closet
    (
        date(2026, 9, 6),
        DayType.HOME,
        ("white", "blue", "yellow", "black", None),
    ),  # Sun -- wraps back to the start
    (
        date(2026, 9, 7),
        DayType.HOME,
        ("brown", "black", None, "white", "black"),
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
