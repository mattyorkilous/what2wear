"""The agreed Aug 15-24 2026 sequence, against the authored wardrobe.

The whole Outfit now -- Shirt, pants, sweater and shoes -- including
the Friday Aug 21 Fallback, where tan pants want black but Monday
already took it, and the shoes move from black to white alongside it.
Layers arrive with the weather.
"""

from datetime import date

import pytest

from wardrobe import WARDROBE
from what2wear.core import handle
from what2wear.model import DayType, Outfit

SEQUENCE = [
    (
        date(2026, 8, 15),
        DayType.HOME,
        Outfit("lgreen", "tan", "blue", "black"),
    ),  # Sat -- the home anchor
    (
        date(2026, 8, 16),
        DayType.HOME,
        Outfit("white", "blue", "yellow", "black"),
    ),  # Sun -- wraps back to the start
    (
        date(2026, 8, 17),
        DayType.OFFICE,
        Outfit("dblue", "tan", "black", "black"),
    ),  # Mon -- the office anchor
    (
        date(2026, 8, 18),
        DayType.HOME,
        Outfit("brown", "black", "beige", "white"),
    ),
    (
        date(2026, 8, 19),
        DayType.OFFICE,
        Outfit("white", "blue", "beige", "brown"),
    ),
    (
        date(2026, 8, 20),
        DayType.HOME,
        Outfit("dgreen", "tan", "blue", "black"),
    ),
    (
        date(2026, 8, 21),
        DayType.OFFICE,
        Outfit("black", "tan", "grey", "white"),
    ),  # Fri -- shares tan with Monday, so the fallback and its shoes
    (
        date(2026, 8, 22),
        DayType.HOME,
        Outfit("black", "blue", "yellow", "black"),
    ),
    (
        date(2026, 8, 23),
        DayType.HOME,
        Outfit("purple", "black", "beige", "white"),
    ),
    (
        date(2026, 8, 24),
        DayType.OFFICE,
        Outfit("lblue", "black", "grey", "white"),
    ),  # Mon -- a fresh week, so lblue takes grey cleanly
]


@pytest.mark.parametrize(("on", "day_type", "outfit"), SEQUENCE)
def test_the_worked_calendar(
    on: date, day_type: DayType, outfit: Outfit
) -> None:
    response = handle(on, WARDROBE, today=date(2026, 8, 15))
    assert (response.day_type, response.outfit) == (day_type, outfit)
