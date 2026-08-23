"""Day Type Overrides, driven through the pure `handle` seam.

Recorded decisions are passed in as part of the in-memory State --
nothing here reads the log off disk. The Wardrobe is the given one and
`today` is held at `TODAY`, which is also the Anchor with nothing
recorded, so the dates below line up with the worked calendar.
"""

from datetime import date

from what2wear.core import handle
from what2wear.model import DayType, DayTypeOverride, State

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


class TestWhichClosetTheDayDrawsFrom:
    def test_staying_home_draws_from_the_home_closet(self) -> None:
        s = _with(DayTypeOverride(WED26, DayType.HOME))
        response = handle(WED26, s, today=TODAY)
        assert response.day_type is DayType.HOME
        # Wed is now the fourth home day since the anchor.
        assert response.outfit.shirt == "black"

    def test_going_in_draws_from_the_office_closet(self) -> None:
        s = _with(DayTypeOverride(TUE25, DayType.OFFICE))
        response = handle(TUE25, s, today=TODAY)
        assert response.day_type is DayType.OFFICE
        assert response.outfit.shirt == "black"

    def test_an_override_that_agrees_with_the_pattern_changes_nothing(
        self,
    ) -> None:
        # Recording a Wednesday you were going in on anyway.
        s = _with(DayTypeOverride(WED26, DayType.OFFICE))
        assert all(
            handle(day, s, today=TODAY)
            == handle(day, State(), today=TODAY)
            for day in (MON24, WED26, FRI28, MON31)
        )

    def test_the_anchor_date_parks_like_any_other_day(self) -> None:
        # The Anchor is Sat 22nd, wearing white. Spend it at the
        # office and white was not worn at home, so it is deferred to
        # the Sunday rather than lost -- the same parking rule as any
        # other date, applied to the date every Position counts from.
        s = _with(DayTypeOverride(SAT22, DayType.OFFICE))
        assert handle(SAT22, s, today=TODAY).day_type is DayType.OFFICE
        assert handle(SUN23, State(), today=TODAY).outfit.shirt == (
            "brown"
        )
        assert handle(SUN23, s, today=TODAY).outfit.shirt == "white"

    def test_the_most_recently_recorded_override_wins(self) -> None:
        s = _with(
            DayTypeOverride(WED26, DayType.HOME),
            DayTypeOverride(WED26, DayType.OFFICE),
        )
        assert handle(WED26, s, today=TODAY).day_type is DayType.OFFICE


class TestTheOtherRotation:
    def test_staying_home_leaves_the_office_position_parked(
        self,
    ) -> None:
        # Wednesday's black would have been lost; instead it is
        # simply deferred to Friday, and Friday's lblue to the Monday
        # after.
        s = _with(DayTypeOverride(WED26, DayType.HOME))
        worn = [
            handle(day, s, today=TODAY).outfit.shirt
            for day in (MON24, FRI28, MON31)
        ]
        assert worn == ["white", "black", "lblue"]

    def test_going_in_advances_the_office_rotation_that_day(
        self,
    ) -> None:
        s = _with(DayTypeOverride(TUE25, DayType.OFFICE))
        worn = [
            handle(day, s, today=TODAY).outfit.shirt
            for day in (MON24, TUE25, WED26)
        ]
        assert worn == ["white", "black", "lblue"]

    def test_staying_home_advances_the_home_rotation_that_day(
        self,
    ) -> None:
        s = _with(DayTypeOverride(WED26, DayType.HOME))
        worn = [
            handle(day, s, today=TODAY).outfit.shirt
            for day in (TUE25, WED26, THU27)
        ]
        assert worn == ["dgreen", "black", "purple"]

    def test_a_holiday_is_recorded_like_any_other_override(
        self,
    ) -> None:
        # A public holiday on the Monday is a Day Type Override and
        # nothing else, so Monday's white reappears on the Wednesday.
        s = _with(DayTypeOverride(MON24, DayType.HOME))
        assert handle(MON24, s, today=TODAY).day_type is DayType.HOME
        assert handle(WED26, s, today=TODAY).outfit.shirt == "white"


class TestLookAhead:
    def test_a_future_override_changes_look_ahead_from_then_on(
        self,
    ) -> None:
        s = _with(DayTypeOverride(WED26, DayType.HOME))
        assert handle(MON31, State(), today=TODAY).outfit.shirt == (
            "striped"
        )
        assert handle(MON31, s, today=TODAY).outfit.shirt == "lblue"

    def test_dates_before_the_override_are_untouched(self) -> None:
        s = _with(DayTypeOverride(WED26, DayType.HOME))
        assert handle(MON24, s, today=TODAY) == handle(
            MON24, State(), today=TODAY
        )


class TestRecordingADecision:
    def test_the_response_carries_the_decision_to_append(self) -> None:
        response = handle(
            WED26, State(), today=TODAY, record=DayType.HOME
        )
        assert response.decision == DayTypeOverride(WED26, DayType.HOME)

    def test_the_response_already_reflects_what_it_records(
        self,
    ) -> None:
        response = handle(
            WED26, State(), today=TODAY, record=DayType.HOME
        )
        assert response.day_type is DayType.HOME
        assert response.outfit.shirt == "black"

    def test_recording_defaults_to_today(self) -> None:
        response = handle(
            None, State(), today=WED26, record=DayType.HOME
        )
        assert response.decision == DayTypeOverride(WED26, DayType.HOME)

    def test_asking_without_recording_appends_nothing(self) -> None:
        assert handle(WED26, State(), today=TODAY).decision is None


class TestAFourthOfficeDay:
    def test_going_in_on_a_saturday_draws_from_the_office_closet(
        self,
    ) -> None:
        # What the fourth Office Day does to the sweaters is
        # `test_resolution.py`'s business; that it answers at all is
        # this one's.
        s = _with(DayTypeOverride(SAT29, DayType.OFFICE))
        response = handle(SAT29, s, today=TODAY)
        assert response.day_type is DayType.OFFICE
        assert response.outfit.shirt == "striped"


def _with(*overrides: DayTypeOverride) -> State:
    return State(overrides=overrides)
