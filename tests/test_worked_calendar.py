"""The agreed Aug 15-24 2026 sequence, against the example Wardrobe.

The whole Outfit now -- Shirt, pants, sweater and shoes -- including
the Friday Aug 21 Fallback, where slate pants want ink but Monday
already took it, and the shoes move from ebony to bone alongside it.
Outerwear arrives with the weather.
"""

from datetime import date

import pytest
from conftest import WARDROBE

from what2wear.core import handle
from what2wear.model import DayType, Outfit

SEQUENCE = [
    (
        date(2026, 8, 15),
        DayType.HOME,
        Outfit("pique", "slate", "indigo", "ebony"),
    ),  # Sat -- the home anchor
    (
        date(2026, 8, 16),
        DayType.HOME,
        Outfit("poplin", "sand", "mustard", "ebony"),
    ),  # Sun -- wraps back to the start
    (
        date(2026, 8, 17),
        DayType.OFFICE,
        Outfit("sateen", "slate", "ink", "ebony"),
    ),  # Mon -- the office anchor
    (
        date(2026, 8, 18),
        DayType.HOME,
        Outfit("henley", "moss", "oatmeal", "bone"),
    ),
    (
        date(2026, 8, 19),
        DayType.OFFICE,
        Outfit("poplin", "sand", "cream", "walnut"),
    ),
    (
        date(2026, 8, 20),
        DayType.HOME,
        Outfit("jersey", "slate", "indigo", "ebony"),
    ),
    (
        date(2026, 8, 21),
        DayType.OFFICE,
        Outfit("twill", "slate", "ash", "bone"),
    ),  # Fri -- shares tan with Monday, so the fallback and its shoes
    (
        date(2026, 8, 22),
        DayType.HOME,
        Outfit("twill", "sand", "mustard", "ebony"),
    ),
    (
        date(2026, 8, 23),
        DayType.HOME,
        Outfit("waffle", "moss", "oatmeal", "bone"),
    ),
    (
        date(2026, 8, 24),
        DayType.OFFICE,
        Outfit("flannel", "moss", "ash", "bone"),
    ),  # Mon -- a fresh week, so flannel takes ash cleanly
]


@pytest.mark.parametrize(("on", "day_type", "outfit"), SEQUENCE)
def test_the_worked_calendar(
    on: date, day_type: DayType, outfit: Outfit
) -> None:
    response = handle(on, WARDROBE, today=date(2026, 8, 15))
    assert (response.day_type, response.outfit) == (day_type, outfit)
