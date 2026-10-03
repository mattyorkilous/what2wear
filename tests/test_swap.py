from dataclasses import replace
from datetime import date, timedelta

import pytest

from what2wear.core import answer, swap
from what2wear.errors import What2wearError
from what2wear.model import DayType, State
from what2wear.wardrobe import get_default_state

TODAY = date(2026, 8, 22)
MON24, MON31 = date(2026, 8, 24), date(2026, 8, 31)
GIVEN = get_default_state(TODAY)
FORTNIGHT = tuple(
    TODAY + timedelta(days=offset) for offset in range(14)
)


def _swapped(closet: DayType, first: str, second: str) -> State:
    return swap(GIVEN, closet, first, second)


def test_two_shirts_sharing_pants_trade_labels() -> None:
    # Position 0 is Monday's and Position 3 the Monday after, and the
    # names change hands rather than the Positions.
    told = _swapped(DayType.OFFICE, "White", "Striped")
    assert [
        answer(told, on, {}).outfit.shirt.label for on in (MON24, MON31)
    ] == [
        "Striped",
        "White",
    ]


def test_no_outfit_differs_except_in_which_shirt_it_names() -> None:
    told = _swapped(DayType.HOME, "White", "Black")
    assert [_but_the_shirt(told, on) for on in FORTNIGHT] == [
        _but_the_shirt(GIVEN, on) for on in FORTNIGHT
    ]


def test_colors_travel_with_labels() -> None:
    told = _swapped(DayType.OFFICE, "White", "Striped")
    assert [
        answer(state, MON31, {}).outfit.shirt for state in (GIVEN, told)
    ] == [
        answer(state, MON24, {}).outfit.shirt for state in (told, GIVEN)
    ]


class TestARefusedSwap:
    def test_two_shirts_with_different_pants_are_refused(self) -> None:
        # `White` wears blue and `Black` tan, so trading them would
        # move the sweater and the shoes with the name.
        with pytest.raises(What2wearError, match="pants"):
            _swapped(DayType.OFFICE, "White", "Black")

    def test_a_label_the_closet_does_not_have_is_refused(self) -> None:
        with pytest.raises(What2wearError, match="no office shirt"):
            _swapped(DayType.OFFICE, "White", "Purple")


def _but_the_shirt(state: State, on: date) -> object:
    response = answer(state, on, {})
    return replace(response, outfit=replace(response.outfit, shirt=""))
