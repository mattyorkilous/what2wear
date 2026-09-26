from dataclasses import replace
from datetime import date

import pytest

from what2wear.core import answer
from what2wear.model import (
    DayType,
    Response,
)
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
FRI_SEP4 = date(2026, 9, 4)


class TestDayType:
    def test_the_given_weekdays_are_office_days(self) -> None:
        assert all(
            _on(day).day_type is DayType.OFFICE
            for day in (MON24, WED26, FRI28)
        )

    def test_every_other_weekday_is_a_home_day(self) -> None:
        assert all(
            _on(day).day_type is DayType.HOME for day in (TUE25, THU27)
        )

    def test_weekends_are_home_days(self) -> None:
        assert all(
            _on(day).day_type is DayType.HOME
            for day in (SAT22, SUN23, SAT29)
        )


class TestTheResponse:
    def test_it_carries_the_date_it_resolved(self) -> None:
        assert _on(TODAY).on == TODAY


class TestRotation:
    def test_today_stands_at_the_top_of_its_closet(self) -> None:
        # Nothing recorded, so the Anchor is today at Position 0 and
        # a fresh installation opens on white.
        assert _on(TODAY).outfit.shirt == "white"

    def test_the_office_rotation_advances_only_on_office_days(
        self,
    ) -> None:
        worn = [_on(day).outfit.shirt for day in (MON24, WED26, FRI28)]
        assert worn == ["white", "black", "lblue"]

    def test_home_days_in_between_do_not_move_the_office_rotation(
        self,
    ) -> None:
        # Wed 26th follows Mon 24th in the office rotation despite
        # Tue 25th at home.
        assert _on(WED26).outfit.shirt == "black"

    def test_the_home_rotation_advances_only_on_home_days(self) -> None:
        worn = [_on(day).outfit.shirt for day in (SAT22, SUN23, TUE25)]
        assert worn == ["white", "brown", "dgreen"]

    def test_each_rotation_wraps_at_the_end_of_its_closet(self) -> None:
        # Five office shirts, so the sixth office day since the anchor
        # comes back round to white.
        assert _on(FRI_SEP4).outfit.shirt == "white"

    def test_pants_come_welded_to_the_shirt(self) -> None:
        outfit = _on(TUE25).outfit
        assert (outfit.shirt, outfit.pants) == ("dgreen", "tan")

    @pytest.mark.parametrize(
        ("day", "shirt"),
        [
            # The Holidays on Office Weekdays in between are Home Days,
            # so five years of them have moved the office Rotation on.
            (date(2031, 8, 18), "lblue"),
            (date(2031, 8, 20), "striped"),
            (date(2031, 8, 22), "dblue"),
        ],
    )
    def test_dates_years_out_resolve_by_the_same_rule(
        self, day: date, shirt: str
    ) -> None:
        assert _on(day).outfit.shirt == shirt


class TestDatesBehindTheOneAsked:
    def test_an_override_behind_a_date_still_parks_its_rotation(
        self,
    ) -> None:
        # Monday spent at home, so the office rotation is parked and
        # Wednesday wears the white Monday would have.
        state = replace(
            get_default_state(TODAY), overrides={MON24: DayType.HOME}
        )
        assert answer(state, WED26, {}).outfit.shirt == "white"

    def test_the_week_walk_still_resolves_earlier_office_days(
        self,
    ) -> None:
        # Friday's blue pants want the beige sweater, and only Monday
        # and Wednesday -- both already past by Friday -- can say it is
        # taken. Resolving them is what turns the answer into the grey
        # Fallback and the white shoes that come with it.
        outfit = _on(FRI_SEP4).outfit
        assert (outfit.sweater, outfit.shoes) == ("grey", "white")


def _on(day: date) -> Response:
    return answer(get_default_state(TODAY), day, {})
