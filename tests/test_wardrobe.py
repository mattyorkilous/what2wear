"""The given Wardrobe holds the properties the rules assume.

Per ADR-0005 the shape is given, so the properties the rules lean on
are asserted once here. If one of these fails, the source is wrong --
the tool has no way to be told otherwise.
"""

from collections import Counter
from datetime import date

import pytest

from what2wear import wardrobe

CLOSETS = [
    pytest.param(wardrobe.DEFAULT_OFFICE, id="office"),
    pytest.param(wardrobe.DEFAULT_HOME, id="home"),
]


class TestTheDefaultAnchor:
    def test_it_stands_at_the_top_of_the_rotation(self) -> None:
        anchor = wardrobe.get_default_anchor(date(2026, 8, 22))
        assert anchor.position == 0

    def test_it_sits_on_the_day_it_is_asked_about(self) -> None:
        today = date(2026, 8, 22)
        assert wardrobe.get_default_anchor(today).on == today

    @pytest.mark.parametrize("closet", CLOSETS)
    def test_the_top_of_every_closet_is_white(
        self, closet: wardrobe.Closet
    ) -> None:
        # What makes Position 0 the same promise in both Closets: a
        # fresh installation opens on white whichever kind of day it
        # is.
        anchor = wardrobe.get_default_anchor(date(2026, 8, 22))
        assert closet.shirts[anchor.position].label == "white"


@pytest.mark.parametrize("closet", CLOSETS)
class TestEveryCloset:
    def test_no_label_names_two_shirts(
        self, closet: wardrobe.Closet
    ) -> None:
        labels = [shirt.label for shirt in closet.shirts]
        assert len(set(labels)) == len(labels)

    def test_every_shirt_has_a_row_for_its_pants(
        self, closet: wardrobe.Closet
    ) -> None:
        assert {shirt.pants for shirt in closet.shirts} <= {
            row.pants for row in closet.rows
        }

    def test_no_pair_of_pants_has_two_rows(
        self, closet: wardrobe.Closet
    ) -> None:
        worn = [row.pants for row in closet.rows]
        assert len(set(worn)) == len(worn)


def test_both_closets_wear_the_same_pants() -> None:
    # One set of trousers, both Closets wearing it, with a row per
    # pair per Closet -- ADR-0003. What they are worn
    # *with* is the row, and those differ.
    assert tuple(
        row.pants for row in wardrobe.DEFAULT_OFFICE.rows
    ) == tuple(row.pants for row in wardrobe.DEFAULT_HOME.rows)


class TestTheOfficeCloset:
    """What the Week-scoped no-repeat rule needs to be answerable."""

    def test_sweaters_are_one_to_one_with_shoes(self) -> None:
        # A Fallback brings its donor row's shoes across, so two rows
        # sharing a sweater would leave the shoes ambiguous.
        rows = wardrobe.DEFAULT_OFFICE.rows
        assert len({row.sweater for row in rows}) == len(rows)
        assert len({row.shoes for row in rows}) == len(rows)

    def test_every_fallback_is_another_rows_sweater(self) -> None:
        rows = wardrobe.DEFAULT_OFFICE.rows
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
        worn = Counter(
            shirt.pants for shirt in wardrobe.DEFAULT_OFFICE.shirts
        )
        assert all(
            row.fallback is not None
            for row in wardrobe.DEFAULT_OFFICE.rows
            if worn[row.pants] > 1
        )

    def test_no_row_carries_a_jacket(self) -> None:
        assert all(
            row.jacket is None for row in wardrobe.DEFAULT_OFFICE.rows
        )


class TestTheHomeCloset:
    def test_every_row_carries_a_jacket(self) -> None:
        assert all(
            row.jacket is not None for row in wardrobe.DEFAULT_HOME.rows
        )

    def test_no_row_carries_a_fallback(self) -> None:
        # Home has no no-repeat rule, so there is nothing to fall back
        # from.
        assert all(
            row.fallback is None for row in wardrobe.DEFAULT_HOME.rows
        )
