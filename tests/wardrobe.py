"""The authored wardrobe, in memory.

This mirrors the shipped `what2wear.yaml` so that the core can be exercised
against the real closets without a test ever touching a file. `test_config.py`
pins the two together.
"""

from datetime import date

from what2wear.model import Closet, Shirt, State

WARDROBE = State(
    office=Closet(
        shirts=(
            Shirt("white", "blue"),
            Shirt("black", "tan"),
            Shirt("lblue", "black"),
            Shirt("striped", "blue"),
            Shirt("dblue", "tan"),
        ),
        anchor_date=date(2026, 8, 17),
        anchor_shirt="dblue",
    ),
    home=Closet(
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
        anchor_date=date(2026, 8, 15),
        anchor_shirt="lgreen",
    ),
    office_weekdays=frozenset({0, 2, 4}),
)
