from dataclasses import replace
from datetime import date

import pytest

from what2wear.core import answer
from what2wear.model import (
    DayType,
    Outfit,
    Response,
    State,
)
from what2wear.wardrobe import get_default_state

TODAY = date(2026, 8, 22)

# The five office Week shapes. Five Shirts and three Office Days are
# coprime, so the Weeks cycle over five before repeating. Three resolve
# cleanly; two share pants and need a Fallback.
WEEK_SHAPES = (
    (
        (date(2026, 8, 24), "white", "blue", "beige", "brown"),
        (date(2026, 8, 26), "black", "tan", "black", "black"),
        (date(2026, 8, 28), "lblue", "black", "grey", "white"),
    ),
    (
        (date(2026, 8, 31), "striped", "blue", "beige", "brown"),
        (date(2026, 9, 2), "dblue", "tan", "black", "black"),
        # Blue again, and Monday took beige -- so the Fallback, and its
        # donor row's shoes with it.
        (date(2026, 9, 4), "white", "blue", "grey", "white"),
    ),
    (
        (date(2026, 9, 7), "black", "tan", "black", "black"),
        (date(2026, 9, 9), "lblue", "black", "grey", "white"),
        (date(2026, 9, 11), "striped", "blue", "beige", "brown"),
    ),
    (
        (date(2026, 9, 14), "dblue", "tan", "black", "black"),
        (date(2026, 9, 16), "white", "blue", "beige", "brown"),
        # Tan again, and Monday took black.
        (date(2026, 9, 18), "black", "tan", "grey", "white"),
    ),
    (
        (date(2026, 9, 21), "lblue", "black", "grey", "white"),
        (date(2026, 9, 23), "striped", "blue", "beige", "brown"),
        (date(2026, 9, 25), "dblue", "tan", "black", "black"),
    ),
)

# One Monday-start Week of Home Days. Sunday wears blue pants again,
# so its yellow sweater and black shoes repeat Tuesday's inside the
# Week -- at the office that would force a Fallback; at home it is
# simply what the row says, which is the no-no-repeat rule in the only
# form it can be observed.
HOME_WEEK = (
    (date(2026, 9, 1), "beige", "blue", "yellow", "black"),
    (date(2026, 9, 3), "lblue", "black", "beige", "white"),
    (date(2026, 9, 5), "lgreen", "tan", "blue", "black"),
    (date(2026, 9, 6), "white", "blue", "yellow", "black"),
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
            for day in WEEK_SHAPES[0]
        )

    def test_a_fallback_is_not_an_unavoidable_repeat(self) -> None:
        assert not _response(date(2026, 9, 4)).unavoidable_repeat


class TestFourOfficeDays:
    STATE = replace(
        get_default_state(TODAY),
        overrides={date(2026, 8, 29): DayType.OFFICE},
    )

    @pytest.mark.parametrize(
        ("on", "shirt", "pants", "sweater", "shoes"),
        [
            (date(2026, 8, 24), "white", "blue", "beige", "brown"),
            (date(2026, 8, 26), "black", "tan", "black", "black"),
            (date(2026, 8, 28), "lblue", "black", "grey", "white"),
            # Blue pants want beige, Monday took it, and the grey its
            # row falls back on went to the Friday.
            (date(2026, 8, 29), "striped", "blue", "beige", "brown"),
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
            date(2026, 8, 29), self.STATE
        ).unavoidable_repeat

    def test_the_days_before_it_are_not(self) -> None:
        assert not any(
            _response(on, self.STATE).unavoidable_repeat
            for on in (
                date(2026, 8, 24),
                date(2026, 8, 26),
                date(2026, 8, 28),
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


def _outfit(on: date, state: State | None = None) -> Outfit:
    return _response(on, state).outfit


def _response(on: date, state: State | None = None) -> Response:
    return answer(state or get_default_state(TODAY), on)
