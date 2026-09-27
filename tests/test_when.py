from datetime import date, timedelta
from itertools import islice

import pytest

from what2wear.core import (
    HORIZON_DAYS,
    answer,
    get_due_date,
    get_due_shirt,
    record_override,
    replace_,
    reset,
    set_office_weekdays,
    swap,
)
from what2wear.errors import What2wearError
from what2wear.model import DayType, State
from what2wear.wardrobe import CLOSETS, get_default_state

TUE, THU, SAT = 1, 3, 5

TODAY = date(2026, 8, 22)
MON24, WED26, FRI28 = (
    date(2026, 8, 24),
    date(2026, 8, 26),
    date(2026, 8, 28),
)
MON31 = date(2026, 8, 31)

GIVEN = get_default_state(TODAY)


class TestTheDateFound:
    def test_a_shirt_due_today_answers_today(self) -> None:
        # A fresh state anchors today at the top of its closet, and
        # today is a Saturday.
        assert _get_due(GIVEN, DayType.HOME, "White") == TODAY

    @pytest.mark.parametrize("day_type", tuple(DayType))
    def test_each_shirt_answers_with_the_next_date_that_wears_it(
        self, day_type: DayType
    ) -> None:
        # The five office shirts and the nine home ones answer with the
        # next five and nine days of their own kind -- so in rotation
        # order, none of that kind skipped over, and never a day of the
        # other kind.
        shirts = _shirts(day_type)
        days = _get_days_of_kind(GIVEN, day_type, len(shirts))
        assert [
            _get_due(GIVEN, day_type, shirt) for shirt in shirts
        ] == days
        assert (
            tuple(get_due_shirt(GIVEN, day_type, on) for on in days)
            == shirts
        )

    def test_a_label_no_shirt_in_that_closet_has_is_refused(
        self,
    ) -> None:
        with pytest.raises(What2wearError, match="ecru"):
            _get_due(GIVEN, DayType.OFFICE, "ecru")


class TestWhatMovesTheDate:
    def test_an_override_pushes_it_to_the_next_day_of_that_kind(
        self,
    ) -> None:
        # Wednesday wore black; staying home that day leaves Friday
        # the second office day since the anchor, so Friday wears it.
        assert _get_due(GIVEN, DayType.OFFICE, "Black") == WED26
        state = record_override(GIVEN, WED26, DayType.HOME)
        assert _get_due(state, DayType.OFFICE, "Black") == FRI28

    def test_a_stretch_of_overrides_covering_the_year_answers_none(
        self,
    ) -> None:
        state = GIVEN
        for offset in range(HORIZON_DAYS):
            state = record_override(
                state, TODAY + timedelta(days=offset), DayType.HOME
            )
        assert _get_due(state, DayType.OFFICE, "White") is None

    def test_the_horizon_is_a_year(self) -> None:
        assert HORIZON_DAYS == 365

    def test_a_reset_moves_the_date(self) -> None:
        state = reset(GIVEN, "Dark Blue", WED26)
        assert _get_due(state, DayType.OFFICE, "White") == FRI28

    def test_a_reset_to_the_shirt_makes_it_answer_that_date(
        self,
    ) -> None:
        state = reset(GIVEN, "Dark Blue", WED26)
        assert _get_due(state, DayType.OFFICE, "Dark Blue") == WED26

    def test_a_replace_changes_which_label_answers(self) -> None:
        state = replace_(GIVEN, "office.shirt.White", "ecru")
        assert _get_due(state, DayType.OFFICE, "ecru") == MON24
        with pytest.raises(What2wearError, match="White"):
            _get_due(state, DayType.OFFICE, "White")

    def test_a_swap_exchanges_the_two_dates(self) -> None:
        # White and Striped share Blue pants, so the swap is cosmetic
        # and their dates simply trade.
        before = [
            _get_due(GIVEN, DayType.OFFICE, shirt)
            for shirt in ("White", "Striped")
        ]
        state = swap(GIVEN, DayType.OFFICE, "White", "Striped")
        after = [
            _get_due(state, DayType.OFFICE, shirt)
            for shirt in ("White", "Striped")
        ]
        assert before == [MON24, MON31]
        assert after == list(reversed(before))

    def test_changing_the_office_weekdays_keeps_the_two_readings_agreed(
        self,
    ) -> None:
        # Every anchor moves with the change, so the shirt the closet
        # is due to give still answers with the soonest office day --
        # which the new pattern makes today.
        state = set_office_weekdays(GIVEN, (TUE, THU, SAT), TODAY)
        due = get_due_shirt(state, DayType.OFFICE, TODAY)
        assert _get_due(state, DayType.OFFICE, due) == TODAY


def _get_due(
    state: State, day_type: DayType, shirt: str
) -> date | None:
    return get_due_date(state, day_type, shirt, TODAY)


def _shirts(day_type: DayType) -> tuple[str, ...]:
    return tuple(shirt.garment for shirt in CLOSETS[day_type].shirts)


def _get_days_of_kind(
    state: State, day_type: DayType, count: int
) -> list[date]:
    """The next `count` `day_type` days from today, today included."""
    days = (
        TODAY + timedelta(days=offset) for offset in range(HORIZON_DAYS)
    )
    return list(
        islice(
            (
                on
                for on in days
                if answer(state, on, {}).day_type is day_type
            ),
            count,
        )
    )
