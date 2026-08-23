"""The Aug 29 - Sep 7 2026 sequence, against the given Wardrobe.

The whole Outfit -- Shirt, pants, sweater and shoes -- including the
Friday Sep 4 Fallback, where blue pants want beige but Monday already
took it, and the shoes move from brown to white alongside it. It also
carries the home wrap from Sat Sep 5 round to Sun Sep 6, and the Week
resetting cleanly on Mon Sep 7.

One State for the whole range, anchored at `TODAY`: nothing is
recorded across it, so every date is the same call with a different
argument.
"""

from datetime import date

import pytest

from what2wear.core import answer
from what2wear.model import DayType, Outfit, default_state

TODAY = date(2026, 8, 22)

SEQUENCE = [
    (
        date(2026, 8, 29),
        DayType.HOME,
        Outfit("purple", "black", "beige", "white"),
    ),  # Sat
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
        Outfit("beige", "blue", "yellow", "black"),
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
        Outfit("lgreen", "tan", "blue", "black"),
    ),  # Sat -- the end of the home closet
    (
        date(2026, 9, 6),
        DayType.HOME,
        Outfit("white", "blue", "yellow", "black"),
    ),  # Sun -- wraps back to the start
    (
        date(2026, 9, 7),
        DayType.OFFICE,
        Outfit("black", "tan", "black", "black"),
    ),  # Mon -- a fresh week, so tan takes black cleanly
]


@pytest.mark.parametrize(("on", "day_type", "outfit"), SEQUENCE)
def test_the_worked_calendar(
    on: date, day_type: DayType, outfit: Outfit
) -> None:
    response = answer(default_state(TODAY), on)
    assert (response.day_type, response.outfit) == (day_type, outfit)
