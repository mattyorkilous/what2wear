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
    # Labor Day makes the Week of 7 September a Holiday Week of two
    # Office Days, and the Week after it repeats the shape above, so
    # the cycle picks up again two weeks on.
    (
        (date(2026, 9, 21), "black", "tan", "black", "black"),
        (date(2026, 9, 23), "lblue", "black", "grey", "white"),
        (date(2026, 9, 25), "striped", "blue", "beige", "brown"),
    ),
    (
        (date(2026, 9, 28), "dblue", "tan", "black", "black"),
        (date(2026, 9, 30), "white", "blue", "beige", "brown"),
        # Tan again, and Monday took black.
        (date(2026, 10, 2), "black", "tan", "grey", "white"),
    ),
    (
        (date(2026, 10, 5), "lblue", "black", "grey", "white"),
        (date(2026, 10, 7), "striped", "blue", "beige", "brown"),
        (date(2026, 10, 9), "dblue", "tan", "black", "black"),
    ),
)

# Labor Day's Week. Monday is at home, so it takes no sweater, and
# Wednesday's tan pants get the black one Monday would have.
HOLIDAY_WEEK = (
    (date(2026, 9, 9), "black", "tan", "black", "black"),
    (date(2026, 9, 11), "lblue", "black", "grey", "white"),
)

# One Monday-start Week of Home Days, alternating jacket and sweater.
# Sunday wears blue pants again, so its black shoes repeat Tuesday's
# inside the Week -- at the office that would force a Fallback; at
# home it is simply what the row says.
HOME_WEEK = (
    (date(2026, 9, 1), Outfit("beige", "blue", None, "black", "brown")),
    (date(2026, 9, 3), Outfit("lblue", "black", "beige", "white")),
    (date(2026, 9, 5), Outfit("lgreen", "tan", None, "black", "black")),
    (date(2026, 9, 6), Outfit("white", "blue", "yellow", "black")),
)


class TestOfficeWeeks:
    @pytest.mark.parametrize(
        ("on", "shirt", "pants", "sweater", "shoes"),
        [day for week in (*WEEK_SHAPES, HOLIDAY_WEEK) for day in week],
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

    @pytest.mark.parametrize("week", [*WEEK_SHAPES, HOLIDAY_WEEK])
    def test_no_sweater_repeats_within_a_week(
        self, week: tuple[tuple[date, str, str, str, str], ...]
    ) -> None:
        worn = [_outfit(day[0]).sweater for day in week]
        assert len(set(worn)) == len(worn)

    @pytest.mark.parametrize("week", [*WEEK_SHAPES, HOLIDAY_WEEK])
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
    @pytest.mark.parametrize(("on", "outfit"), HOME_WEEK)
    def test_outerwear_and_shoes_follow_the_pants(
        self, on: date, outfit: Outfit
    ) -> None:
        assert _outfit(on) == outfit

    def test_a_home_day_is_never_flagged_as_a_repeat(self) -> None:
        assert not any(
            _response(day[0]).unavoidable_repeat for day in HOME_WEEK
        )


def _outfit(on: date, state: State | None = None) -> Outfit:
    return _response(on, state).outfit


def _response(on: date, state: State | None = None) -> Response:
    return answer(state or get_default_state(TODAY), on, {})
