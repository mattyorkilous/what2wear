from datetime import date, timedelta

import pytest

from what2wear.core import (
    answer,
    get_due_date,
    get_due_shirt,
    record_override,
)
from what2wear.model import DayType, Garment, State
from what2wear.wardrobe import CLOSETS, get_default_state

TODAY = date(2026, 8, 22)
SUN_SEP6, LABOR_DAY, TUE_SEP8, WED_SEP9 = (
    date(2026, 9, 6),
    date(2026, 9, 7),
    date(2026, 9, 8),
    date(2026, 9, 9),
)
THANKSGIVING, FRI_NOV27 = date(2026, 11, 26), date(2026, 11, 27)

GIVEN = get_default_state(TODAY)


class TestWhichDaysAreHolidays:
    @pytest.mark.parametrize(
        "on",
        [
            LABOR_DAY,
            THANKSGIVING,
            FRI_NOV27,
            # July 4 on a Saturday is observed on Friday.
            date(2026, 7, 3),
            # July 4 on a Sunday is observed on Monday.
            date(2027, 7, 5),
            # New Year's Day on a Saturday is observed the year before.
            date(2027, 12, 31),
        ],
    )
    def test_a_holiday_on_an_office_weekday_is_a_home_day(
        self, on: date
    ) -> None:
        assert answer(GIVEN, on, {}).day_type is DayType.HOME

    def test_the_other_office_days_of_a_holiday_week_are_not(
        self,
    ) -> None:
        assert [
            answer(GIVEN, on, {}).day_type
            for on in (WED_SEP9, date(2026, 11, 23), date(2026, 11, 25))
        ] == [DayType.OFFICE] * 3


class TestTheRotations:
    def test_a_holiday_does_not_advance_the_office_shirts(
        self,
    ) -> None:
        assert get_due_shirt(
            GIVEN, DayType.OFFICE, WED_SEP9
        ) == get_due_shirt(
            record_override(GIVEN, LABOR_DAY, DayType.OFFICE),
            DayType.OFFICE,
            LABOR_DAY,
        )

    def test_a_holiday_advances_the_home_shirts(self) -> None:
        shirts = [
            answer(GIVEN, on, {}).outfit.shirt.label
            for on in (SUN_SEP6, LABOR_DAY, TUE_SEP8)
        ]
        assert shirts == ["White", "Brown", "Dark Green"]

    def test_a_holiday_takes_a_home_outerwear_turn(self) -> None:
        outerwear = [
            _get_outerwear(GIVEN, on)
            for on in (SUN_SEP6, LABOR_DAY, TUE_SEP8)
        ]
        assert outerwear == ["sweater", "jacket", "sweater"]

    def test_the_office_sweater_walk_does_not_see_the_holiday(
        self,
    ) -> None:
        # Monday's black would have taken the black sweater that
        # Wednesday's tan pants want; at home it takes nothing.
        outfit = answer(GIVEN, WED_SEP9, {}).outfit
        assert (
            outfit.shirt.label,
            outfit.pants.label,
            _get_label(outfit.sweater),
        ) == (
            "Black",
            "Tan",
            "Black",
        )

    def test_when_never_answers_an_office_shirt_with_a_holiday(
        self,
    ) -> None:
        holidays = {LABOR_DAY, THANKSGIVING, FRI_NOV27}
        due_dates = {
            get_due_date(GIVEN, DayType.OFFICE, shirt.garment, on)
            for shirt in CLOSETS[DayType.OFFICE].shirts
            for on in (TODAY + timedelta(days=d) for d in range(100))
        }
        assert not due_dates & holidays


class TestOverridingThem:
    def test_go_in_makes_a_holiday_an_office_day(self) -> None:
        state = record_override(GIVEN, LABOR_DAY, DayType.OFFICE)
        assert answer(state, LABOR_DAY, {}).day_type is DayType.OFFICE
        assert state.overrides == {LABOR_DAY: DayType.OFFICE}

    def test_go_in_on_a_holiday_counts_as_an_office_day(self) -> None:
        state = record_override(GIVEN, LABOR_DAY, DayType.OFFICE)
        assert get_due_shirt(
            state, DayType.OFFICE, WED_SEP9
        ) != get_due_shirt(state, DayType.OFFICE, LABOR_DAY)
        assert get_due_shirt(
            state, DayType.HOME, TUE_SEP8
        ) == get_due_shirt(GIVEN, DayType.HOME, LABOR_DAY)

    def test_stay_home_on_a_holiday_records_nothing(self) -> None:
        state = record_override(GIVEN, LABOR_DAY, DayType.HOME)
        assert state.overrides == {}


class TestTheCount:
    @pytest.mark.parametrize("day_type", tuple(DayType))
    @pytest.mark.parametrize("years", [-2, 3])
    def test_a_position_years_away_matches_a_day_by_day_walk(
        self, years: int, day_type: DayType
    ) -> None:
        state = record_override(
            record_override(GIVEN, LABOR_DAY, DayType.OFFICE),
            THANKSGIVING,
            DayType.HOME,
        )
        on = TODAY + timedelta(days=365 * years + 3)
        start, end = sorted((TODAY, on))
        day_types = [
            answer(state, start + timedelta(days=d), {}).day_type
            for d in range((end - start).days)
        ]
        steps = (1 if years > 0 else -1) * day_types.count(day_type)
        shirts = CLOSETS[day_type].shirts
        assert (
            get_due_shirt(state, day_type, on)
            == shirts[steps % len(shirts)].garment
        )


def _get_outerwear(state: State, on: date) -> str:
    return (
        "jacket"
        if answer(state, on, {}).outfit.jacket is not None
        else "sweater"
    )


def _get_label(garment: Garment | None) -> str | None:
    return None if garment is None else garment.label
