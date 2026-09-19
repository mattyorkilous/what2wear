from datetime import date

import pytest

from what2wear.core import answer, replace_
from what2wear.errors import What2wearError
from what2wear.model import State
from what2wear.wardrobe import get_default_state

TODAY = date(2026, 8, 22)
SAT22, TUE25 = date(2026, 8, 22), date(2026, 8, 25)
MON24, WED26, FRI28 = (
    date(2026, 8, 24),
    date(2026, 8, 26),
    date(2026, 8, 28),
)
GIVEN = get_default_state(TODAY)


def _replaced(garment: str, label: str) -> State:
    return replace_(GIVEN, garment, label)


def test_a_replaced_garment_is_named_by_its_new_label() -> None:
    told = _replaced("office.shirt.white", "cream")
    assert answer(told, MON24, {}).outfit.shirt == "cream"


def test_a_replace_moves_no_rotation() -> None:
    # The replaced Shirt is still Monday's and the other two are still
    # where they were, so nothing followed the Label.
    told = _replaced("office.shirt.white", "cream")
    assert [
        answer(told, on, {}).outfit.shirt
        for on in (MON24, WED26, FRI28)
    ] == ["cream", "black", "lblue"]


def test_a_garment_is_replaced_again_by_its_new_label() -> None:
    # How a Garment is named moves with the Label, because the Label
    # is the whole of what the wearer has to go on.
    once = _replaced("home.shirt.white", "cream")
    twice = replace_(once, "home.shirt.cream", "ecru")
    assert answer(twice, SAT22, {}).outfit.shirt == "ecru"


def test_home_shoes_two_pants_rows_call_for_change_once() -> None:
    # Saturday wears blue pants and Tuesday tan, and the black shoes
    # are one pair worn with either.
    told = _replaced("home.shoes.black", "oxblood")
    assert [
        answer(told, on, {}).outfit.shoes for on in (SAT22, TUE25)
    ] == [
        "oxblood",
        "oxblood",
    ]


def test_replacing_pants_changes_them_in_both_closets() -> None:
    # One set of trousers, both Closets wearing it.
    told = _replaced("pants.blue", "navy")
    assert [
        answer(told, on, {}).outfit.pants for on in (SAT22, MON24)
    ] == [
        "navy",
        "navy",
    ]


def test_the_same_label_in_the_two_closets_stays_legal() -> None:
    # The home Closet already has a yellow sweater, and the office
    # one is a different garment.
    told = _replaced("office.sweater.beige", "yellow")
    assert answer(told, MON24, {}).outfit.sweater == "yellow"


class TestARefusedReplace:
    def test_a_label_another_garment_of_that_kind_has_is_refused(
        self,
    ) -> None:
        # The office already has black shoes, so a second pair called
        # black would leave the answer unactionable.
        with pytest.raises(What2wearError, match="black"):
            _replaced("office.shoes.brown", "black")

    def test_restating_the_label_a_garment_already_has_is_not(
        self,
    ) -> None:
        assert _replaced("office.shoes.brown", "brown") == GIVEN

    def test_a_label_naming_no_garment_is_refused(self) -> None:
        with pytest.raises(
            What2wearError, match="no office shirt is called 'puce'"
        ):
            _replaced("office.shirt.puce", "cream")

    def test_a_label_from_the_other_closet_names_nothing(
        self,
    ) -> None:
        # `purple` is a home Shirt and the office Closet has no such
        # Label, so the Closet named is what decides.
        with pytest.raises(
            What2wearError, match="no office shirt is called 'purple'"
        ):
            _replaced("office.shirt.purple", "cream")

    def test_a_garment_with_no_closet_and_kind_is_refused(self) -> None:
        # A bare Label says neither which Closet nor what kind of
        # thing, so there is no scope to report it missing from.
        with pytest.raises(
            What2wearError, match="nothing is called 'white'"
        ):
            _replaced("white", "cream")
