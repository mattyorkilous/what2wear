from datetime import date

import pytest

from what2wear.core import answer, record_override, reset
from what2wear.errors import What2wearError
from what2wear.model import Anchor, DayType, Outfit, State
from what2wear.wardrobe import get_default_state

TODAY = date(2026, 8, 22)
TUE25, WED26 = date(2026, 8, 25), date(2026, 8, 26)
THU27, FRI28, SAT29 = (
    date(2026, 8, 27),
    date(2026, 8, 28),
    date(2026, 8, 29),
)
MON31, WED_SEP2, FRI_SEP4 = (
    date(2026, 8, 31),
    date(2026, 9, 2),
    date(2026, 9, 4),
)

GIVEN = get_default_state(TODAY)


class TestANamedReset:
    def test_it_jumps_straight_to_that_shirt(self) -> None:
        assert _shirt(_reset(WED26, "dblue"), WED26) == "dblue"

    def test_it_anchors_today_at_that_shirts_position(self) -> None:
        # dblue sits at 4, whatever the day stood at before.
        assert _reset(WED26, "dblue").anchors[DayType.OFFICE] == Anchor(
            WED26, 4
        )

    def test_a_shirt_already_behind_is_simply_landed_on(self) -> None:
        # Monday's white is behind Wednesday's black, and naming it
        # goes back to it rather than round the closet to reach it.
        assert _shirt(_reset(WED26, "white"), WED26) == "white"

    def test_naming_the_shirt_already_due_changes_no_date(self) -> None:
        # The Anchor moves and the Rotation does not, which is what
        # "the Anchor states a Position" has to mean.
        state = _reset(WED26, "black")
        assert state.anchors[DayType.OFFICE] == Anchor(WED26, 1)
        assert all(
            answer(state, day, {}) == answer(GIVEN, day, {})
            for day in (WED26, FRI28, MON31, FRI_SEP4)
        )


class TestTheClosetIsInferredFromTheDay:
    def test_a_home_day_names_a_home_shirt(self) -> None:
        assert _shirt(_reset(TUE25, "beige"), TUE25) == "beige"

    @pytest.mark.parametrize(
        ("today", "shirt"),
        [(WED26, "brown"), (TUE25, "striped")],
    )
    def test_a_shirt_the_days_closet_lacks_is_an_error(
        self, today: date, shirt: str
    ) -> None:
        with pytest.raises(What2wearError, match=shirt):
            _reset(today, shirt)

    def test_an_override_decides_which_closet_is_meant(self) -> None:
        # Wednesday spent at home, so a home shirt is now the one that
        # can be named on it and the office shirt is not.
        stayed_home = record_override(GIVEN, WED26, DayType.HOME)
        state = reset(stayed_home, "beige", WED26)
        assert _shirt(state, WED26) == "beige"
        assert (
            state.anchors[DayType.OFFICE]
            == GIVEN.anchors[DayType.OFFICE]
        )

    def test_the_other_closet_is_left_exactly_where_it_stood(
        self,
    ) -> None:
        assert (
            _reset(WED26, "lblue").anchors[DayType.HOME]
            == GIVEN.anchors[DayType.HOME]
        )
        assert (
            _reset(TUE25, "black").anchors[DayType.OFFICE]
            == GIVEN.anchors[DayType.OFFICE]
        )


class TestEveryLaterDateFollows:
    def test_later_dates_of_that_kind_are_shifted(self) -> None:
        state = _reset(WED26, "lblue")
        worn = [_shirt(state, day) for day in (WED26, FRI28, MON31)]
        assert worn == ["lblue", "striped", "dblue"]

    def test_resets_carry_on_from_each_other(self) -> None:
        once = _reset(WED26, "lblue")
        twice = reset(once, "dblue", FRI28)
        assert _shirt(twice, MON31) == "white"

    def test_only_the_closet_it_was_typed_in_moves(self) -> None:
        # Reset on an office day, so the home rotation stays where it
        # was and Thursday is still black.
        assert _shirt(_reset(WED26, "lblue"), THU27) == "black"

    def test_a_home_reset_leaves_the_office_closet_alone(self) -> None:
        state = _reset(TUE25, "black")
        assert _shirt(state, WED26) == "black"
        assert _shirt(state, SAT29) == "dblue"


class TestAMidWeekReset:
    def test_the_week_before_it_is_untouched(self) -> None:
        assert answer(GIVEN, FRI_SEP4, {}).outfit == Outfit(
            "white", "blue", "grey", "white"
        )

    def test_it_moves_the_fallback_the_week_had_reached_for(
        self,
    ) -> None:
        # The walk now reads Monday as tan rather than blue, so blue's
        # own beige is free on the Friday and the Fallback goes unused.
        state = _reset(WED_SEP2, "lblue")
        assert answer(state, FRI_SEP4, {}).outfit == Outfit(
            "striped", "blue", "beige", "brown"
        )


class TestInterleavedWithOverrides:
    def test_both_kinds_apply_by_their_own_date(self) -> None:
        # Wednesday spent at home moves the home rotation on and parks
        # the office one, and the Reset typed that day moves the home
        # rotation again -- Thursday takes both.
        stayed_home = record_override(GIVEN, WED26, DayType.HOME)
        state = reset(stayed_home, "purple", WED26)
        worn = [_shirt(state, day) for day in (WED26, THU27, FRI28)]
        assert worn == ["purple", "dblue", "black"]

    def test_an_override_ahead_of_a_reset_still_parks_the_shirt(
        self,
    ) -> None:
        away = record_override(GIVEN, FRI28, DayType.HOME)
        state = reset(away, "lblue", WED26)
        assert _shirt(state, MON31) == "striped"


def _reset(today: date, shirt: str) -> State:
    return reset(GIVEN, shirt, today)


def _shirt(state: State, on: date) -> str:
    return answer(state, on, {}).outfit.shirt
