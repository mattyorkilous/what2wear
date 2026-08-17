"""The example Wardrobe, in memory.

This mirrors the shipped `example.yaml` so that the core can be
exercised against whole closets without a test ever touching a file.
`test_config.py` pins the two together.
"""

from datetime import date

from what2wear.model import Closet, PantsRow, Shirt, State

WARDROBE = State(
    office=Closet(
        shirts=(
            Shirt("poplin", "sand"),
            Shirt("twill", "slate"),
            Shirt("flannel", "moss"),
            Shirt("gingham", "sand"),
            Shirt("sateen", "slate"),
        ),
        pants=(
            PantsRow(
                "sand", sweater="cream", shoes="walnut", fallback="ash"
            ),
            PantsRow(
                "slate", sweater="ink", shoes="ebony", fallback="ash"
            ),
            PantsRow("moss", sweater="ash", shoes="bone"),
        ),
        anchor_date=date(2026, 8, 17),
        anchor_shirt="sateen",
    ),
    home=Closet(
        shirts=(
            Shirt("poplin", "sand"),
            Shirt("henley", "moss"),
            Shirt("jersey", "slate"),
            Shirt("twill", "sand"),
            Shirt("waffle", "moss"),
            Shirt("sateen", "slate"),
            Shirt("rugby", "sand"),
            Shirt("flannel", "moss"),
            Shirt("pique", "slate"),
        ),
        pants=(
            PantsRow(
                "sand",
                sweater="mustard",
                shoes="ebony",
                jacket="bomber",
            ),
            PantsRow(
                "slate",
                sweater="indigo",
                shoes="ebony",
                jacket="peacoat",
            ),
            PantsRow(
                "moss",
                sweater="oatmeal",
                shoes="bone",
                jacket="peacoat",
            ),
        ),
        anchor_date=date(2026, 8, 15),
        anchor_shirt="pique",
    ),
    office_weekdays=frozenset({0, 2, 4}),
)
