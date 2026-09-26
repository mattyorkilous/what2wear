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
        Outfit("purple", "black", None, "white", jacket="black"),
    ),  # Sat -- a jacket day, and Sunday a sweater day
    (
        date(2026, 8, 30),
        DayType.HOME,
        Outfit("dblue", "tan", "blue", "black"),
    ),  # Sun
    (
        date(2026, 8, 31),
        DayType.OFFICE,
        Outfit("striped", "blue", "beige", "brown"),
    ),  # Mon -- takes beige, which Friday then wants
    (
        date(2026, 9, 1),
        DayType.HOME,
        Outfit("beige", "blue", None, "black", jacket="brown"),
    ),
    (
        date(2026, 9, 2),
        DayType.OFFICE,
        Outfit("dblue", "tan", "black", "black"),
    ),
    (
        date(2026, 9, 3),
        DayType.HOME,
        Outfit("lblue", "black", "beige", "white"),
    ),
    (
        date(2026, 9, 4),
        DayType.OFFICE,
        Outfit("white", "blue", "grey", "white"),
    ),  # Fri -- shares blue with Monday, so the fallback and its shoes
    (
        date(2026, 9, 5),
        DayType.HOME,
        Outfit("lgreen", "tan", None, "black", jacket="black"),
    ),  # Sat -- the end of the home closet
    (
        date(2026, 9, 6),
        DayType.HOME,
        Outfit("white", "blue", "yellow", "black"),
    ),  # Sun -- wraps back to the start
    (
        date(2026, 9, 7),
        DayType.HOME,
        Outfit("brown", "black", None, "white", jacket="black"),
    ),  # Mon -- Labor Day, so a Home Day, and the next home shirt
]


@pytest.mark.parametrize(("on", "day_type", "outfit"), SEQUENCE)
def test_the_worked_calendar(
    on: date, day_type: DayType, outfit: Outfit
) -> None:
    response = answer(get_default_state(TODAY), on, {})
    assert (response.day_type, response.outfit) == (day_type, outfit)
