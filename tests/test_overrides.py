"""Day Type Overrides, driven through the pure `handle` seam.

Recorded decisions are passed in as part of the in-memory State --
nothing here reads the log off disk. The wardrobe is the authored one,
so the dates below line up with the worked calendar.
"""

from dataclasses import replace
from datetime import date

from wardrobe import WARDROBE
from what2wear.core import handle
from what2wear.model import DayType, DayTypeOverride, State

MON17, TUE18, WED19, THU20, FRI21 = (
    date(2026, 8, 17),
    date(2026, 8, 18),
    date(2026, 8, 19),
    date(2026, 8, 20),
    date(2026, 8, 21),
)
SAT15, SUN16 = date(2026, 8, 15), date(2026, 8, 16)
SAT22, MON24 = date(2026, 8, 22), date(2026, 8, 24)


class TestWhichClosetTheDayDrawsFrom:
    def test_staying_home_draws_from_the_home_closet(self) -> None:
        s = _with(DayTypeOverride(WED19, DayType.HOME))
        response = handle(WED19, s, today=MON17)
        assert response.day_type is DayType.HOME
        # Wed is now the fourth home day since Saturday's anchor.
        assert response.outfit.shirt == "dgreen"

    def test_going_in_draws_from_the_office_closet(self) -> None:
        s = _with(DayTypeOverride(TUE18, DayType.OFFICE))
        response = handle(TUE18, s, today=MON17)
        assert response.day_type is DayType.OFFICE
        assert response.outfit.shirt == "white"

    def test_an_override_that_agrees_with_the_pattern_changes_nothing(
        self,
    ) -> None:
        # Recording a Wednesday you were going in on anyway.
        s = _with(DayTypeOverride(WED19, DayType.OFFICE))
        for day in (MON17, WED19, FRI21, MON24):
            assert handle(day, s, today=MON17) == handle(
                day, WARDROBE, today=MON17
            )

    def test_an_anchor_date_parks_like_any_other_day(self) -> None:
        # The home anchor is Sat 15th, wearing lgreen. Spend it at the
        # office and lgreen was not worn, so it is deferred to the
        # Sunday rather than lost -- the same parking rule as any other
        # date, applied to the date every Position counts from.
        s = _with(DayTypeOverride(SAT15, DayType.OFFICE))
        assert handle(SAT15, s, today=MON17).day_type is DayType.OFFICE
        assert handle(SUN16, WARDROBE, today=MON17).outfit.shirt == (
            "white"
        )
        assert handle(SUN16, s, today=MON17).outfit.shirt == "lgreen"

    def test_the_most_recently_recorded_override_wins(self) -> None:
        s = _with(
            DayTypeOverride(WED19, DayType.HOME),
            DayTypeOverride(WED19, DayType.OFFICE),
        )
        assert handle(WED19, s, today=MON17).day_type is DayType.OFFICE


class TestTheOtherRotation:
    def test_staying_home_leaves_the_office_position_parked(
        self,
    ) -> None:
        # Wednesday's white would have been lost; instead it is simply
        # deferred to Friday, and Friday's black to the Monday after.
        s = _with(DayTypeOverride(WED19, DayType.HOME))
        worn = [
            handle(day, s, today=MON17).outfit.shirt
            for day in (MON17, FRI21, MON24)
        ]
        assert worn == ["dblue", "white", "black"]

    def test_going_in_advances_the_office_rotation_that_day(
        self,
    ) -> None:
        s = _with(DayTypeOverride(TUE18, DayType.OFFICE))
        worn = [
            handle(day, s, today=MON17).outfit.shirt
            for day in (MON17, TUE18, WED19)
        ]
        assert worn == ["dblue", "white", "black"]

    def test_staying_home_advances_the_home_rotation_that_day(
        self,
    ) -> None:
        s = _with(DayTypeOverride(WED19, DayType.HOME))
        worn = [
            handle(day, s, today=MON17).outfit.shirt
            for day in (TUE18, WED19, THU20)
        ]
        assert worn == ["brown", "dgreen", "black"]

    def test_a_holiday_is_recorded_like_any_other_override(
        self,
    ) -> None:
        # A public holiday on the Monday is a Day Type Override and
        # nothing else, so Monday's dblue reappears on the Wednesday.
        s = _with(DayTypeOverride(MON17, DayType.HOME))
        assert handle(MON17, s, today=MON17).day_type is DayType.HOME
        assert handle(WED19, s, today=MON17).outfit.shirt == "dblue"


class TestAnyDatePastOrFuture:
    def test_a_future_override_changes_look_ahead_from_then_on(
        self,
    ) -> None:
        s = _with(DayTypeOverride(WED19, DayType.HOME))
        assert handle(MON24, WARDROBE, today=MON17).outfit.shirt == (
            "lblue"
        )
        assert handle(MON24, s, today=MON17).outfit.shirt == "black"

    def test_dates_before_the_override_are_untouched(self) -> None:
        s = _with(DayTypeOverride(WED19, DayType.HOME))
        assert handle(MON17, s, today=MON17) == handle(
            MON17, WARDROBE, today=MON17
        )

    def test_a_past_override_changes_what_earlier_dates_resolve_to(
        self,
    ) -> None:
        s = _with(DayTypeOverride(WED19, DayType.HOME))
        assert handle(FRI21, s, today=MON24).outfit.shirt == "white"


class TestRecordingADecision:
    def test_the_response_carries_the_decision_to_append(self) -> None:
        response = handle(
            WED19, WARDROBE, today=MON17, record=DayType.HOME
        )
        assert response.decision == DayTypeOverride(WED19, DayType.HOME)

    def test_the_response_already_reflects_what_it_records(
        self,
    ) -> None:
        response = handle(
            WED19, WARDROBE, today=MON17, record=DayType.HOME
        )
        assert response.day_type is DayType.HOME
        assert response.outfit.shirt == "dgreen"

    def test_recording_defaults_to_today(self) -> None:
        response = handle(
            None, WARDROBE, today=WED19, record=DayType.HOME
        )
        assert response.decision == DayTypeOverride(WED19, DayType.HOME)

    def test_asking_without_recording_appends_nothing(self) -> None:
        assert handle(WED19, WARDROBE, today=MON17).decision is None


class TestAFourthOfficeDay:
    def test_going_in_on_a_saturday_still_answers(self) -> None:
        # Four Office Days in a Week and only three sweaters left to
        # offer, so the repeat is unavoidable and said so.
        s = _with(DayTypeOverride(SAT22, DayType.OFFICE))
        response = handle(SAT22, s, today=MON17)
        assert response.day_type is DayType.OFFICE
        assert response.unavoidable_repeat


def _with(*overrides: DayTypeOverride) -> State:
    return replace(WARDROBE, overrides=overrides)
