import re
from collections import Counter
from datetime import date

import pytest

from what2wear.model import Closet, DayType, Rotation
from what2wear.wardrobe import (
    CLOSETS,
    build_default_colors,
    build_default_labels,
    get_default_state,
)

OFFICE = CLOSETS[DayType.OFFICE]
HOME = CLOSETS[DayType.HOME]

CLOSETS = [
    pytest.param(OFFICE, id="office"),
    pytest.param(HOME, id="home"),
]


@pytest.mark.parametrize("closet", CLOSETS)
def test_the_top_of_every_closet_is_white(closet: Closet) -> None:
    # What makes Position 0 the same promise in both Closets: a fresh
    # installation opens on white whichever kind of day it is.
    given = get_default_state(date(2026, 8, 22))
    position = given.anchors[Rotation.OFFICE].position
    assert closet.shirts[position].garment == "white"


@pytest.mark.parametrize("closet", CLOSETS)
class TestEveryCloset:
    def test_no_garment_names_two_shirts(self, closet: Closet) -> None:
        labels = [shirt.garment for shirt in closet.shirts]
        assert len(set(labels)) == len(labels)

    def test_every_shirt_has_a_row_for_its_pants(
        self, closet: Closet
    ) -> None:
        assert {shirt.pants for shirt in closet.shirts} <= {
            row.pants for row in closet.rows
        }

    def test_no_pair_of_pants_has_two_rows(
        self, closet: Closet
    ) -> None:
        worn = [row.pants for row in closet.rows]
        assert len(set(worn)) == len(worn)


def test_every_given_garment_has_a_color() -> None:
    colors = build_default_colors()
    assert colors.keys() == build_default_labels().keys()
    assert all(
        re.fullmatch(r"#[0-9a-f]{6}", color)
        for color, _ in colors.values()
    )


def test_only_the_striped_shirt_has_a_stripe_color() -> None:
    labels = build_default_labels()
    striped = {
        key: stripe_color
        for key, (_, stripe_color) in build_default_colors().items()
        if stripe_color is not None
    }
    assert {labels[key] for key in striped} == {"striped"}
    assert all(
        re.fullmatch(r"#[0-9a-f]{6}", color)
        for color in striped.values()
    )


def test_both_closets_wear_the_same_pants() -> None:
    # One set of trousers, both Closets wearing it, with a row per
    # pair per Closet -- ADR-0003. What they are worn
    # *with* is the row, and those differ.
    assert tuple(row.pants for row in OFFICE.rows) == tuple(
        row.pants for row in HOME.rows
    )


class TestTheOfficeCloset:
    def test_sweaters_are_one_to_one_with_shoes(self) -> None:
        # A Fallback brings its donor row's shoes across, so two rows
        # sharing a sweater would leave the shoes ambiguous.
        rows = OFFICE.rows
        assert len({row.sweater for row in rows}) == len(rows)
        assert len({row.shoes for row in rows}) == len(rows)

    def test_every_fallback_is_another_rows_sweater(self) -> None:
        rows = OFFICE.rows
        assert all(
            row.fallback
            in {
                other.sweater
                for other in rows
                if other.pants != row.pants
            }
            for row in rows
            if row.fallback is not None
        )

    def test_pants_two_shirts_share_have_a_fallback(self) -> None:
        # A sweater collision is exactly two office Shirts in a Week
        # sharing Pants, so those rows are the ones that need one.
        worn = Counter(shirt.pants for shirt in OFFICE.shirts)
        assert all(
            row.fallback is not None
            for row in OFFICE.rows
            if worn[row.pants] > 1
        )


class TestTheHomeCloset:
    def test_no_row_carries_a_fallback(self) -> None:
        # Home has no no-repeat rule, so there is nothing to fall back
        # from.
        assert all(row.fallback is None for row in HOME.rows)
