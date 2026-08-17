"""Resolution: the sweater and shoes that follow from the pants, and
the office Week Fallback.

Everything is driven through the pure `handle` seam and asserted on
the resolved Outfit -- never on how a Week was walked.
"""

from dataclasses import replace
from datetime import date

import pytest

from wardrobe import WARDROBE
from what2wear.core import handle
from what2wear.model import Outfit, Response, State

MON, TUE, WED, THU = 0, 1, 2, 3

# The five office Week shapes. Five Shirts and three Office Days are
# coprime, so the Weeks cycle over five before repeating. Three resolve
# cleanly; two share pants and need a Fallback.
WEEK_SHAPES = (
    (
        (date(2026, 8, 17), "sateen", "slate", "ink", "ebony"),
        (date(2026, 8, 19), "poplin", "sand", "cream", "walnut"),
        # Slate again, and Monday took ink -- so the Fallback, and its
        # donor row's shoes with it.
        (date(2026, 8, 21), "twill", "slate", "ash", "bone"),
    ),
    (
        (date(2026, 8, 24), "flannel", "moss", "ash", "bone"),
        (date(2026, 8, 26), "gingham", "sand", "cream", "walnut"),
        (date(2026, 8, 28), "sateen", "slate", "ink", "ebony"),
    ),
    (
        (date(2026, 8, 31), "poplin", "sand", "cream", "walnut"),
        (date(2026, 9, 2), "twill", "slate", "ink", "ebony"),
        (date(2026, 9, 4), "flannel", "moss", "ash", "bone"),
    ),
    (
        (date(2026, 9, 7), "gingham", "sand", "cream", "walnut"),
        (date(2026, 9, 9), "sateen", "slate", "ink", "ebony"),
        # Sand again, and Monday took cream.
        (date(2026, 9, 11), "poplin", "sand", "ash", "bone"),
    ),
    (
        (date(2026, 9, 14), "twill", "slate", "ink", "ebony"),
        (date(2026, 9, 16), "flannel", "moss", "ash", "bone"),
        (date(2026, 9, 18), "gingham", "sand", "cream", "walnut"),
    ),
)

# One Monday-start Week of Home Days. Sunday wears moss pants again,
# so its oatmeal sweater and bone shoes repeat Tuesday's inside the
# Week -- at the office that would force a Fallback; at home it is
# simply what the row says, which is the no-no-repeat rule in the only
# form it can be observed.
HOME_WEEK = (
    (date(2026, 8, 18), "henley", "moss", "oatmeal", "bone"),
    (date(2026, 8, 20), "jersey", "slate", "indigo", "ebony"),
    (date(2026, 8, 22), "twill", "sand", "mustard", "ebony"),
    (date(2026, 8, 23), "waffle", "moss", "oatmeal", "bone"),
)


class TestOfficeWeeks:
    @pytest.mark.parametrize(
        ("on", "shirt", "pants", "sweater", "shoes"),
        [day for week in WEEK_SHAPES for day in week],
    )
    def test_every_office_week_shape_resolves(
        self,
        on: date,
        shirt: str,
        pants: str,
        sweater: str,
        shoes: str,
    ) -> None:
        assert _outfit(on) == Outfit(
            shirt=shirt, pants=pants, sweater=sweater, shoes=shoes
        )

    @pytest.mark.parametrize("week", WEEK_SHAPES)
    def test_no_sweater_repeats_within_a_week(
        self, week: tuple[tuple[date, str, str, str, str], ...]
    ) -> None:
        worn = [_outfit(day[0]).sweater for day in week]
        assert len(set(worn)) == len(worn)

    @pytest.mark.parametrize("week", WEEK_SHAPES)
    def test_no_shoes_repeat_within_a_week(
        self, week: tuple[tuple[date, str, str, str, str], ...]
    ) -> None:
        worn = [_outfit(day[0]).shoes for day in week]
        assert len(set(worn)) == len(worn)

    def test_a_week_that_resolves_cleanly_flags_no_repeat(self) -> None:
        assert not any(
            _response(day[0]).unavoidable_repeat
            for day in WEEK_SHAPES[1]
        )

    def test_a_fallback_is_not_an_unavoidable_repeat(self) -> None:
        assert not _response(date(2026, 8, 21)).unavoidable_repeat


class TestFourOfficeDays:
    """A fourth Office Day exhausts the sweaters a Week can offer, so
    one of them has to come round twice."""

    STATE = replace(
        WARDROBE, office_weekdays=frozenset({MON, TUE, WED, THU})
    )

    @pytest.mark.parametrize(
        ("on", "shirt", "pants", "sweater", "shoes"),
        [
            (date(2026, 8, 17), "sateen", "slate", "ink", "ebony"),
            (date(2026, 8, 18), "poplin", "sand", "cream", "walnut"),
            (date(2026, 8, 19), "twill", "slate", "ash", "bone"),
            # Moss pants want ash, Wednesday's Fallback took it, and
            # that row has no Fallback of its own.
            (date(2026, 8, 20), "flannel", "moss", "ash", "bone"),
        ],
    )
    def test_the_week_still_resolves(
        self,
        on: date,
        shirt: str,
        pants: str,
        sweater: str,
        shoes: str,
    ) -> None:
        assert _outfit(on, self.STATE) == Outfit(
            shirt=shirt, pants=pants, sweater=sweater, shoes=shoes
        )

    def test_the_repeated_day_is_flagged(self) -> None:
        assert _response(
            date(2026, 8, 20), self.STATE
        ).unavoidable_repeat

    def test_the_days_before_it_are_not(self) -> None:
        assert not any(
            _response(on, self.STATE).unavoidable_repeat
            for on in (
                date(2026, 8, 17),
                date(2026, 8, 18),
                date(2026, 8, 19),
            )
        )


class TestHome:
    @pytest.mark.parametrize(
        ("on", "shirt", "pants", "sweater", "shoes"), HOME_WEEK
    )
    def test_sweater_and_shoes_follow_the_pants(
        self,
        on: date,
        shirt: str,
        pants: str,
        sweater: str,
        shoes: str,
    ) -> None:
        assert _outfit(on) == Outfit(
            shirt=shirt, pants=pants, sweater=sweater, shoes=shoes
        )

    def test_a_home_day_is_never_flagged_as_a_repeat(self) -> None:
        assert not any(
            _response(day[0]).unavoidable_repeat for day in HOME_WEEK
        )


def _outfit(on: date, state: State = WARDROBE) -> Outfit:
    return _response(on, state).outfit


def _response(on: date, state: State = WARDROBE) -> Response:
    return handle(on, state, today=date(2026, 8, 15))
