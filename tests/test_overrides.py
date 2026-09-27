from dataclasses import replace
from datetime import date

from what2wear.core import answer, record_override
from what2wear.model import DayType, State
from what2wear.wardrobe import get_default_state

TODAY = date(2026, 8, 22)
SAT22, SUN23 = date(2026, 8, 22), date(2026, 8, 23)
MON24, TUE25, WED26 = (
    date(2026, 8, 24),
    date(2026, 8, 25),
    date(2026, 8, 26),
)
THU27, FRI28, SAT29 = (
    date(2026, 8, 27),
    date(2026, 8, 28),
    date(2026, 8, 29),
)
MON31 = date(2026, 8, 31)

GIVEN = get_default_state(TODAY)


class TestWhichClosetTheDayDrawsFrom:
    def test_staying_home_draws_from_the_home_closet(self) -> None:
        response = answer(_with(WED26, DayType.HOME), WED26, {})
        assert response.day_type is DayType.HOME
        # Wed is now the fourth home day since the anchor.
        assert response.outfit.shirt.label == "black"

    def test_going_in_draws_from_the_office_closet(self) -> None:
        response = answer(_with(TUE25, DayType.OFFICE), TUE25, {})
        assert response.day_type is DayType.OFFICE
        assert response.outfit.shirt.label == "black"

    def test_an_override_that_agrees_with_the_pattern_changes_nothing(
        self,
    ) -> None:
        # Recording a Wednesday you were going in on anyway.
        state = _with(WED26, DayType.OFFICE)
        assert all(
            answer(state, day, {}) == answer(GIVEN, day, {})
            for day in (MON24, WED26, FRI28, MON31)
        )

    def test_the_anchor_date_parks_like_any_other_day(self) -> None:
        # The Anchor is Sat 22nd, wearing white. Spend it at the
        # office and white was not worn at home, so it is deferred to
        # the Sunday rather than lost -- the same parking rule as any
        # other date, applied to the date every Position counts from.
        state = _with(SAT22, DayType.OFFICE)
        assert answer(state, SAT22, {}).day_type is DayType.OFFICE
        assert answer(GIVEN, SUN23, {}).outfit.shirt.label == "brown"
        assert answer(state, SUN23, {}).outfit.shirt.label == "white"


class TestTheOtherRotation:
    def test_staying_home_leaves_the_office_position_parked(
        self,
    ) -> None:
        # Wednesday's black would have been lost; instead it is
        # simply deferred to Friday, and Friday's lblue to the Monday
        # after.
        state = _with(WED26, DayType.HOME)
        worn = [
            answer(state, day, {}).outfit.shirt.label
            for day in (MON24, FRI28, MON31)
        ]
        assert worn == ["white", "black", "lblue"]

    def test_going_in_advances_the_office_rotation_that_day(
        self,
    ) -> None:
        state = _with(TUE25, DayType.OFFICE)
        worn = [
            answer(state, day, {}).outfit.shirt.label
            for day in (MON24, TUE25, WED26)
        ]
        assert worn == ["white", "black", "lblue"]

    def test_staying_home_advances_the_home_rotation_that_day(
        self,
    ) -> None:
        state = _with(WED26, DayType.HOME)
        worn = [
            answer(state, day, {}).outfit.shirt.label
            for day in (TUE25, WED26, THU27)
        ]
        assert worn == ["dgreen", "black", "purple"]

    def test_a_holiday_is_recorded_like_any_other_override(
        self,
    ) -> None:
        # A public holiday on the Monday is a Day Type Override and
        # nothing else, so Monday's white reappears on the Wednesday.
        state = _with(MON24, DayType.HOME)
        assert answer(state, MON24, {}).day_type is DayType.HOME
        assert answer(state, WED26, {}).outfit.shirt.label == "white"


class TestLookAhead:
    def test_a_future_override_changes_look_ahead_from_then_on(
        self,
    ) -> None:
        state = _with(WED26, DayType.HOME)
        assert answer(GIVEN, MON31, {}).outfit.shirt.label == "striped"
        assert answer(state, MON31, {}).outfit.shirt.label == "lblue"

    def test_dates_before_the_override_are_untouched(self) -> None:
        state = _with(WED26, DayType.HOME)
        assert answer(state, MON24, {}) == answer(GIVEN, MON24, {})


class TestRecordingOne:
    def test_it_lands_in_the_state_under_its_own_date(self) -> None:
        assert _applied(WED26, DayType.HOME) == _with(
            WED26, DayType.HOME
        )

    def test_it_moves_no_anchor(self) -> None:
        state = _applied(WED26, DayType.HOME)
        assert state.anchors == GIVEN.anchors

    def test_taking_one_back_leaves_the_state_as_it_was(self) -> None:
        # Wed is an Office Day already, so going back to going in is
        # not a third thing to record -- it is the record removed.
        home = record_override(GIVEN, WED26, DayType.HOME)
        both = record_override(home, WED26, DayType.OFFICE)
        assert both == GIVEN
        assert answer(both, WED26, {}).day_type is DayType.OFFICE

    def test_agreeing_with_the_pattern_records_nothing(self) -> None:
        # Going in on a Wednesday was never news.
        assert record_override(GIVEN, WED26, DayType.OFFICE) == GIVEN

    def test_a_past_date_records_like_any_other(self) -> None:
        # Only the question has no answer. Correcting what a date now
        # behind us was still has to be possible.
        past = date(2026, 8, 17)
        assert record_override(GIVEN, past, DayType.HOME) == _with(
            past, DayType.HOME
        )


class TestAFourthOfficeDay:
    def test_going_in_on_a_saturday_draws_from_the_office_closet(
        self,
    ) -> None:
        # What the fourth Office Day does to the sweaters is
        # `test_resolution.py`'s business; that it answers at all is
        # this one's.
        response = answer(_with(SAT29, DayType.OFFICE), SAT29, {})
        assert response.day_type is DayType.OFFICE
        assert response.outfit.shirt.label == "striped"


def _with(on: date, day_type: DayType) -> State:
    return replace(GIVEN, overrides={on: day_type})


def _applied(on: date, day_type: DayType) -> State:
    return record_override(GIVEN, on, day_type)
