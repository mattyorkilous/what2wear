"""Rotation for any date, driven through the pure `handle` seam.

Every test builds State in memory, passes an explicit date, and
asserts on the returned Response. Nothing here reads a file, a clock
or the network, and nothing reaches into how a Position was derived.
"""

from datetime import date

import pytest

from what2wear.core import handle
from what2wear.model import (
    Closet,
    DayType,
    PantsRow,
    Shirt,
    State,
)

MON, TUE, WED, THU, FRI = 0, 1, 2, 3, 4


class TestDayType:
    def test_configured_weekdays_are_office_days(self) -> None:
        s = _state(office_weekdays=frozenset({MON, WED, FRI}))
        for day in (
            date(2026, 8, 17),
            date(2026, 8, 19),
            date(2026, 8, 21),
        ):
            assert handle(day, s, today=day).day_type is DayType.OFFICE

    def test_every_other_weekday_is_a_home_day(self) -> None:
        s = _state(office_weekdays=frozenset({MON, WED, FRI}))
        for day in (date(2026, 8, 18), date(2026, 8, 20)):
            assert handle(day, s, today=day).day_type is DayType.HOME

    def test_weekends_are_home_days(self) -> None:
        s = _state()
        for day in (date(2026, 8, 15), date(2026, 8, 16)):
            assert handle(day, s, today=day).day_type is DayType.HOME

    def test_the_weekday_pattern_is_configurable(self) -> None:
        s = _state(
            office_weekdays=frozenset({TUE, THU}),
            office_anchor=date(2026, 8, 18),
            home_anchor=date(2026, 8, 17),
        )
        tuesday, monday = date(2026, 8, 18), date(2026, 8, 17)
        assert (
            handle(tuesday, s, today=tuesday).day_type is DayType.OFFICE
        )
        assert handle(monday, s, today=monday).day_type is DayType.HOME


class TestBareInvocation:
    def test_no_date_resolves_today(self) -> None:
        s = _state()
        today = date(2026, 8, 17)
        assert handle(None, s, today=today) == handle(
            today, s, today=today
        )

    def test_the_response_carries_the_date_it_resolved(self) -> None:
        s = _state()
        assert handle(None, s, today=date(2026, 8, 19)).on == date(
            2026, 8, 19
        )


class TestRotation:
    def test_the_anchor_date_wears_the_anchor_shirt(self) -> None:
        s = _state(
            office_anchor=date(2026, 8, 17), office_anchor_shirt="o2"
        )
        assert (
            handle(
                date(2026, 8, 17), s, today=date(2026, 8, 17)
            ).outfit.shirt
            == "o2"
        )

    def test_the_office_rotation_advances_only_on_office_days(
        self,
    ) -> None:
        s = _state()
        worn = [
            handle(day, s, today=day).outfit.shirt
            for day in (
                date(2026, 8, 17),
                date(2026, 8, 19),
                date(2026, 8, 21),
            )
        ]
        assert worn == ["o1", "o2", "o3"]

    def test_home_days_in_between_do_not_move_the_office_rotation(
        self,
    ) -> None:
        s = _state()
        # Wed 19th follows Mon 17th in the office rotation despite
        # Tue 18th at home.
        assert (
            handle(
                date(2026, 8, 19), s, today=date(2026, 8, 19)
            ).outfit.shirt
            == "o2"
        )

    def test_the_home_rotation_advances_only_on_home_days(self) -> None:
        s = _state(
            home_shirts=[
                ("h1", "blue"),
                ("h2", "black"),
                ("h3", "khaki"),
            ]
        )
        worn = [
            handle(day, s, today=day).outfit.shirt
            for day in (
                date(2026, 8, 15),
                date(2026, 8, 16),
                date(2026, 8, 18),
            )
        ]
        assert worn == ["h1", "h2", "h3"]

    def test_each_rotation_wraps_at_the_end_of_its_closet(self) -> None:
        s = _state()
        # Three office shirts, so the fourth office day comes back
        # round to o1.
        assert (
            handle(
                date(2026, 8, 24), s, today=date(2026, 8, 24)
            ).outfit.shirt
            == "o1"
        )

    def test_dates_before_the_anchor_walk_the_rotation_backwards(
        self,
    ) -> None:
        s = _state()
        worn = [
            handle(day, s, today=day).outfit.shirt
            for day in (date(2026, 8, 12), date(2026, 8, 14))
        ]
        assert worn == ["o2", "o3"]

    def test_pants_come_welded_to_the_shirt(self) -> None:
        s = _state(
            office_shirts=[
                ("o1", "tan"),
                ("o2", "navy"),
                ("o3", "grey"),
            ]
        )
        outfit = handle(
            date(2026, 8, 19), s, today=date(2026, 8, 19)
        ).outfit
        assert (outfit.shirt, outfit.pants) == ("o2", "navy")

    @pytest.mark.parametrize(
        ("day", "shirt"),
        [
            (date(2031, 8, 18), "o1"),
            (date(2031, 8, 20), "o2"),
            (date(2031, 8, 22), "o3"),
        ],
    )
    def test_dates_years_out_resolve_by_the_same_rule(
        self, day: date, shirt: str
    ) -> None:
        # 2026-08-17 to 2031-08-18 is 1827 days = 261 whole weeks, so
        # the office rotation has advanced 783 days -- a multiple of
        # 3 -- and sits back at o1.
        s = _state()
        assert handle(day, s, today=day).outfit.shirt == shirt


def _state(
    office_shirts: list[tuple[str, str]] | None = None,
    home_shirts: list[tuple[str, str]] | None = None,
    office_anchor: date = date(2026, 8, 17),
    office_anchor_shirt: str = "o1",
    home_anchor: date = date(2026, 8, 15),
    home_anchor_shirt: str = "h1",
    office_weekdays: frozenset[int] = frozenset({MON, WED, FRI}),
) -> State:
    return State(
        office=_closet(
            office_shirts
            or [("o1", "tan"), ("o2", "navy"), ("o3", "grey")],
            office_anchor,
            office_anchor_shirt,
        ),
        home=_closet(
            home_shirts or [("h1", "blue"), ("h2", "black")],
            home_anchor,
            home_anchor_shirt,
        ),
        office_weekdays=office_weekdays,
    )


def _closet(
    names_and_pants: list[tuple[str, str]], anchor: date, shirt: str
) -> Closet:
    # A row per pants color worn, named after it. Nothing here
    # asserts on sweaters or shoes -- that is `test_resolution.py`'s
    # business -- but a Closet is not valid without them.
    return Closet(
        shirts=tuple(
            Shirt(name=n, pants=p) for n, p in names_and_pants
        ),
        pants=tuple(
            PantsRow(p, sweater=f"{p}-sweater", shoes=f"{p}-shoes")
            for p in dict.fromkeys(p for _, p in names_and_pants)
        ),
        anchor_date=anchor,
        anchor_shirt=shirt,
    )
