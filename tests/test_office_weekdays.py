from datetime import date, timedelta

import pytest

from what2wear.core import (
    answer,
    get_due_shirt,
    record_override,
    set_office_weekdays,
)
from what2wear.errors import What2wearError
from what2wear.model import DayType, Garment, State
from what2wear.wardrobe import get_default_state

MON, TUE, WED, THU, FRI, SAT, SUN = range(7)

TODAY = date(2026, 8, 22)
MON31, WED_SEP2 = date(2026, 8, 31), date(2026, 9, 2)
FRI_SEP4, SAT_SEP5, SUN_SEP6 = (
    date(2026, 9, 4),
    date(2026, 9, 5),
    date(2026, 9, 6),
)
MON_SEP14, TUE_SEP15, WED_SEP16 = (
    date(2026, 9, 14),
    date(2026, 9, 15),
    date(2026, 9, 16),
)

GIVEN = get_default_state(TODAY)
# Weeks of days, some of them overridden, between the Anchors and now,
# so that re-counting under the new pattern would move every Rotation.
TOLD = record_override(
    record_override(GIVEN, WED_SEP2, DayType.HOME),
    SAT_SEP5,
    DayType.OFFICE,
)


class TestSettingThem:
    def test_the_named_days_become_the_office_days(self) -> None:
        state = set_office_weekdays(
            TOLD, frozenset({TUE, THU, SAT}), WED_SEP16
        )
        assert [
            answer(state, on, {}).day_type
            for on in (date(2026, 9, 21), date(2026, 9, 22))
        ] == [DayType.HOME, DayType.OFFICE]

    def test_a_weekend_may_be_named(self) -> None:
        state = set_office_weekdays(
            GIVEN, frozenset({FRI, SAT, SUN}), TODAY
        )
        assert answer(state, SUN_SEP6, {}).day_type is DayType.OFFICE

    @pytest.mark.parametrize(
        "weekdays",
        [
            frozenset(),
            frozenset({MON}),
            frozenset({MON, WED}),
            frozenset({MON, TUE, WED, THU}),
            frozenset(range(7)),
            (MON, MON, WED, FRI),
        ],
    )
    def test_any_count_but_three_is_refused_as_a_source_change(
        self, weekdays: tuple[int, ...]
    ) -> None:
        with pytest.raises(What2wearError, match="source"):
            set_office_weekdays(GIVEN, weekdays, TODAY)


class TestEveryRotationIsReAnchored:
    @pytest.mark.parametrize(
        "weekdays",
        [
            frozenset({TUE, THU, SAT}),
            frozenset({MON, TUE, WED}),
            frozenset({FRI, SAT, SUN}),
        ],
    )
    @pytest.mark.parametrize("today", [TUE_SEP15, WED_SEP16])
    def test_no_rotation_moves_as_a_result_of_the_change_alone(
        self, weekdays: frozenset[int], today: date
    ) -> None:
        state = set_office_weekdays(TOLD, weekdays, today)
        assert _get_due(state, today) == _get_due(TOLD, today)

    def test_restating_them_changes_nothing(self) -> None:
        # So a restatement reads as already the case, not as recorded.
        assert (
            set_office_weekdays(
                TOLD, frozenset({MON, WED, FRI}), WED_SEP16
            )
            == TOLD
        )

    def test_restating_them_changes_no_answer_for_any_date(
        self,
    ) -> None:
        state = set_office_weekdays(
            TOLD, frozenset({MON, WED, FRI}), WED_SEP16
        )
        assert all(
            answer(state, on, {}) == answer(TOLD, on, {})
            for on in (
                WED_SEP16 + timedelta(days=offset)
                for offset in range(-40, 60)
            )
        )

    def test_a_mid_week_change_can_move_that_weeks_fallback(
        self,
    ) -> None:
        # ADR-0007 accepts this knowingly, as ADR-0001 does for a
        # mid-Week Reset: the Week's earlier Office Days are resolved
        # under the new pattern. Monday's striped shirt took beige,
        # so Friday's white fell back to grey; with Thursday its only
        # earlier Office Day, beige is free again.
        state = set_office_weekdays(
            GIVEN, frozenset({THU, FRI, SAT}), FRI_SEP4
        )
        before, after = (
            answer(told, FRI_SEP4, {}).outfit for told in (GIVEN, state)
        )
        assert before.shirt.label == after.shirt.label == "White"
        assert (
            _get_label(before.sweater),
            _get_label(after.sweater),
        ) == (
            "Grey",
            "Beige",
        )


class TestTheOverrides:
    def test_those_already_recorded_are_left_alone(self) -> None:
        # Including Saturday's, which the new pattern makes redundant.
        state = set_office_weekdays(
            TOLD, frozenset({TUE, THU, SAT}), MON31
        )
        assert state.overrides == TOLD.overrides

    def test_a_fourth_office_day_still_flags_an_unavoidable_repeat(
        self,
    ) -> None:
        # Exactly three is a rule about the pattern, not about a Week:
        # going in once more is still reachable, and still costs a
        # sweater twice.
        state = record_override(
            set_office_weekdays(
                GIVEN, frozenset({TUE, THU, SAT}), TODAY
            ),
            MON_SEP14,
            DayType.OFFICE,
        )
        week = (
            MON_SEP14 + timedelta(days=offset) for offset in range(7)
        )
        assert any(
            answer(state, on, {}).unavoidable_repeat for on in week
        )


def _get_due(state: State, today: date) -> tuple[str, str, str]:
    """Each Rotation's next turn from `today`, by what it hands out."""
    next_home_day = next(
        on
        for on in (
            today + timedelta(days=offset) for offset in range(7)
        )
        if answer(state, on, {}).day_type is DayType.HOME
    )
    outfit = answer(state, next_home_day, {}).outfit
    return (
        get_due_shirt(state, DayType.OFFICE, today),
        get_due_shirt(state, DayType.HOME, today),
        "jacket" if outfit.jacket is not None else "sweater",
    )


def _get_label(garment: Garment | None) -> str | None:
    return None if garment is None else garment.label
