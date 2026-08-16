"""The agreed Aug 15-24 2026 sequence, against the authored wardrobe.

Shirt and pants only at this stage -- sweaters, shoes and the Friday
Aug 21 fallback arrive with Resolution.
"""

from datetime import date

import pytest

from wardrobe import WARDROBE
from what2wear.core import handle
from what2wear.model import DayType, Show

SEQUENCE = [
    (
        date(2026, 8, 15),
        DayType.HOME,
        "lgreen",
        "tan",
    ),  # Sat -- the home anchor
    (
        date(2026, 8, 16),
        DayType.HOME,
        "white",
        "blue",
    ),  # Sun -- wraps back to the start
    (
        date(2026, 8, 17),
        DayType.OFFICE,
        "dblue",
        "tan",
    ),  # Mon -- the office anchor
    (date(2026, 8, 18), DayType.HOME, "brown", "black"),
    (date(2026, 8, 19), DayType.OFFICE, "white", "blue"),
    (date(2026, 8, 20), DayType.HOME, "dgreen", "tan"),
    (
        date(2026, 8, 21),
        DayType.OFFICE,
        "black",
        "tan",
    ),  # Fri -- shares tan with Monday
    (date(2026, 8, 22), DayType.HOME, "black", "blue"),
    (date(2026, 8, 23), DayType.HOME, "purple", "black"),
    (
        date(2026, 8, 24),
        DayType.OFFICE,
        "lblue",
        "black",
    ),  # Mon -- a fresh week
]


@pytest.mark.parametrize(("on", "day_type", "shirt", "pants"), SEQUENCE)
def test_the_worked_calendar(
    on: date, day_type: DayType, shirt: str, pants: str
) -> None:
    response = handle(Show(on=on), WARDROBE, today=date(2026, 8, 15))
    assert (
        response.day_type,
        response.outfit.shirt,
        response.outfit.pants,
    ) == (
        day_type,
        shirt,
        pants,
    )
